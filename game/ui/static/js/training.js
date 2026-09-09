/**
 * Training Center Manager with Beautiful Smoothing Charts and Metrics
 */
const TrainingUI = {
  lastSummary: null,
  cachedConfig: null,

  rewardPresets: {
    balanced: { exit: 50, coin: 10, convert: 20, police: -30, step: -0.05 },
    rush_exit: { exit: 160, coin: 2, convert: 0, police: -40, step: -0.4 },
    greedy_loot: { exit: 15, coin: 40, convert: 20, police: -25, step: -0.05 },
    vault_buster: { exit: 20, coin: 5, convert: 85, police: -30, step: -0.1 },
    police_phobia: { exit: 40, coin: 10, convert: 15, police: -100, step: -0.25 }
  },

  init() {
    const btnTrain = document.getElementById('btn-start-training');
    if (btnTrain) {
      btnTrain.addEventListener('click', () => this.runTraining());
    }

    const btnReset = document.getElementById('btn-reset-training');
    if (btnReset) {
      btnReset.addEventListener('click', () => this.resetTraining());
    }

    // Quick episode buttons
    document.querySelectorAll('.btn-quick-ep').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const cnt = e.target.getAttribute('data-count');
        const input = document.getElementById('train-episode-count');
        if (input && cnt) input.value = cnt;
      });
    });

    this.initRewardTuning();
    this.loadInitialConfig();
  },

  initRewardTuning() {
    // Sliders setup
    const sliders = [
      { id: 'slider-rew-exit', valId: 'val-rew-exit', fmt: (v) => `+${parseFloat(v).toFixed(1)}` },
      { id: 'slider-rew-coin', valId: 'val-rew-coin', fmt: (v) => `+${parseFloat(v).toFixed(1)}` },
      { id: 'slider-rew-convert', valId: 'val-rew-convert', fmt: (v) => `+${parseFloat(v).toFixed(1)}` },
      { id: 'slider-rew-police', valId: 'val-rew-police', fmt: (v) => `${parseFloat(v).toFixed(1)}` },
      { id: 'slider-rew-step', valId: 'val-rew-step', fmt: (v) => `${parseFloat(v).toFixed(2)}` }
    ];

    sliders.forEach(s => {
      const el = document.getElementById(s.id);
      const valEl = document.getElementById(s.valId);
      if (el && valEl) {
        el.addEventListener('input', () => {
          valEl.textContent = s.fmt(el.value);
          // Unselect preset chips if customized manually
          document.querySelectorAll('.reward-preset-btn').forEach(b => b.classList.remove('active'));
        });
      }
    });

    // Preset buttons setup
    document.querySelectorAll('.reward-preset-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const pKey = e.currentTarget.getAttribute('data-preset');
        if (pKey && this.rewardPresets[pKey]) {
          this.applyPreset(pKey);
        }
      });
    });

    // Reset button setup
    const btnResetRewards = document.getElementById('btn-reset-reward-tuning');
    if (btnResetRewards) {
      btnResetRewards.addEventListener('click', () => {
        this.applyPreset('balanced');
      });
    }

    // Train & Observe button setup
    const btnObserve = document.getElementById('btn-train-and-observe');
    if (btnObserve) {
      btnObserve.addEventListener('click', () => this.trainAndObserve());
    }
  },

  applyPreset(presetKey) {
    const p = this.rewardPresets[presetKey];
    if (!p) return;

    const setSlider = (id, valId, val, fmt) => {
      const el = document.getElementById(id);
      const valEl = document.getElementById(valId);
      if (el) el.value = val;
      if (valEl) valEl.textContent = fmt(val);
    };

    setSlider('slider-rew-exit', 'val-rew-exit', p.exit, v => `+${parseFloat(v).toFixed(1)}`);
    setSlider('slider-rew-coin', 'val-rew-coin', p.coin, v => `+${parseFloat(v).toFixed(1)}`);
    setSlider('slider-rew-convert', 'val-rew-convert', p.convert, v => `+${parseFloat(v).toFixed(1)}`);
    setSlider('slider-rew-police', 'val-rew-police', p.police, v => `${parseFloat(v).toFixed(1)}`);
    setSlider('slider-rew-step', 'val-rew-step', p.step, v => `${parseFloat(v).toFixed(2)}`);

    document.querySelectorAll('.reward-preset-btn').forEach(btn => {
      if (btn.getAttribute('data-preset') === presetKey) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  },

  getCustomRewards() {
    const wrapper = document.getElementById('reward-tuning-wrapper');
    if (!wrapper || wrapper.style.display === 'none') {
      return null;
    }

    const exit = parseFloat(document.getElementById('slider-rew-exit')?.value ?? 50);
    const coin = parseFloat(document.getElementById('slider-rew-coin')?.value ?? 10);
    const convert = parseFloat(document.getElementById('slider-rew-convert')?.value ?? 20);
    const police = parseFloat(document.getElementById('slider-rew-police')?.value ?? -30);
    const step = parseFloat(document.getElementById('slider-rew-step')?.value ?? -0.05);

    return {
      exit: isNaN(exit) ? 50 : exit,
      coin: isNaN(coin) ? 10 : coin,
      convert: isNaN(convert) ? 20 : convert,
      lose_life: isNaN(police) ? -30 : police,
      step: isNaN(step) ? -0.05 : step
    };
  },

  async updateRewardTuningVisibility() {
    const wrapper = document.getElementById('reward-tuning-wrapper');
    const badge = document.getElementById('reward-tuning-admin-badge');
    if (!wrapper) return;

    try {
      if (!this.cachedConfig) {
        this.cachedConfig = await API.getConfig();
      }
    } catch (e) {
      // ignore
    }

    const isFlagEnabled = !!(this.cachedConfig && this.cachedConfig.show_reward_tuning);
    const user = (typeof AuthUI !== 'undefined' && AuthUI.currentUser) ? AuthUI.currentUser : null;
    const isAdmin = user && user.role === 'admin';

    if (isAdmin) {
      wrapper.style.display = 'block';
      if (badge) {
        badge.style.display = 'inline-block';
        if (isFlagEnabled) {
          badge.textContent = '👑 فلگ ادمین: روشن برای کاربران عادی';
          badge.style.background = '#dcfce7';
          badge.style.color = '#15803d';
        } else {
          badge.textContent = '👑 پیش‌نمایش مدیر (برای کاربر عادی خاموش است)';
          badge.style.background = '#fef3c7';
          badge.style.color = '#92400e';
        }
      }
    } else if (isFlagEnabled) {
      wrapper.style.display = 'block';
      if (badge) badge.style.display = 'none';
    } else {
      wrapper.style.display = 'none';
    }
  },

  async loadInitialConfig() {
    try {
      const cfg = await API.getConfig();
      this.cachedConfig = cfg;
      this.updateFromConfig(cfg);
      await this.updateRewardTuningVisibility();
    } catch (e) {
      console.error("خطا در دریافت تنظیمات آموزش:", e);
      await this.updateRewardTuningVisibility();
    }
  },

  updateFromConfig(cfg) {
    if (!cfg) return;
    const rl = cfg.rl || {};
    const input = document.getElementById('train-episode-count');
    if (input && rl.episodes) {
      input.value = rl.episodes;
    }
    const badge = document.getElementById('train-active-hyperparams-badge');
    if (badge) {
      const alpha = rl.alpha ?? 0.2;
      const gamma = rl.gamma ?? 0.9;
      const epsInit = rl.initial_epsilon ?? 1.0;
      const epsMin = rl.final_epsilon ?? 0.05;
      const decay = rl.epsilon_decay ?? 0.96;
      const maxSteps = cfg.max_steps ?? 100;
      badge.innerHTML = `⚙️ <strong>هایپرپارامترهای فعال:</strong> آلفا: <code>${alpha}</code> | گاما: <code>${gamma}</code> | کاوش: <code>${epsInit} ➔ ${epsMin}</code> (کاهش: <code>${decay}</code>) | حداکثر گام: <code>${maxSteps}</code>`;
    }
  },

  async resetTraining() {
    if (!confirm('آیا از بازنشانی کامل حافظه و تجربیات هوش مصنوعی اطمینان دارید؟ تمام آموزش‌های قبلی پاک شده و آموزش از مرحله ۱ شروع خواهد شد.')) {
      return;
    }

    const btn = document.getElementById('btn-reset-training');
    if (btn) btn.disabled = true;

    try {
      const res = await API.resetTraining();
      this.lastSummary = null;

      // Reset metrics UI
      document.getElementById('metric-success-rate').textContent = '--';
      document.getElementById('metric-avg-reward').textContent = '--';
      document.getElementById('metric-divergence').textContent = '--';
      document.getElementById('metric-total-episodes').textContent = '0';

      // Clear charts
      const c1 = document.getElementById('chart-reward');
      if (c1) c1.getContext('2d').clearRect(0, 0, c1.width, c1.height);
      const c2 = document.getElementById('chart-coins');
      if (c2) c2.getContext('2d').clearRect(0, 0, c2.width, c2.height);

      const banner = document.getElementById('train-success-banner');
      if (banner) {
        banner.style.display = 'block';
        banner.style.background = '#f1f5f9';
        banner.style.borderRightColor = '#64748b';
        banner.innerHTML = `🔄 ${res.message || 'حافظه آموزش با موفقیت بازنشانی شد.'}`;
        setTimeout(() => { banner.style.display = 'none'; }, 4000);
      }
    } catch (err) {
      alert('خطا در بازنشانی: ' + err.message);
    } finally {
      if (btn) btn.disabled = false;
    }
  },

  async runTraining() {
    const btn = document.getElementById('btn-start-training');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '⏳ در حال آموزش و ارتقای تجربیات هوش مصنوعی...';
    }

    const strategy = StrategyUI.getStrategy();
    const epInput = document.getElementById('train-episode-count');
    const epCount = epInput ? (parseInt(epInput.value, 10) || 10) : 10;
    const customRewards = this.getCustomRewards();

    try {
      // Train continuing with hybrid strategy seeding and optional custom rewards
      const resp = await API.train(strategy, epCount, 'hybrid', false, customRewards);

      if (resp.success) {
        this.lastSummary = resp.summary;
        this.renderMetrics(resp.summary);
        this.renderCharts(resp.summary.metrics);

        // Update Replay selector if present
        if (typeof ReplayUI !== 'undefined' && ReplayUI.populateEpisodeSelector) {
          ReplayUI.populateEpisodeSelector(resp.summary.available_replay_episodes);
        }

        // Show prompt to switch to Replay
        const banner = document.getElementById('train-success-banner');
        if (banner) {
          banner.style.display = 'block';
          banner.style.background = '#ecfdf5';
          banner.style.borderRightColor = '#10b981';
          banner.innerHTML = `🎉 مرحله جدید آموزش با موفقیت پایان یافت! <strong>${epCount} اپیزود جدید</strong> آموزش داده شد (مجموعاً <strong>${resp.summary.total_episodes} اپیزود</strong>). میانگین پاداش به <strong>${resp.summary.avg_reward_last_5}</strong> و نرخ موفقیت به <strong>${Math.round(resp.summary.final_success_rate * 100)}%</strong> رسید.`;
        }
      }
    } catch (err) {
      alert("خطا در آموزش: " + err.message);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    }
  },

  async trainAndObserve() {
    const btn = document.getElementById('btn-train-and-observe');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '⏳ در حال آموزش با پاداش‌های جدید...';
    }

    const banner = document.getElementById('train-success-banner');
    const strategy = (typeof StrategyUI !== 'undefined' && StrategyUI.getStrategy) ? StrategyUI.getStrategy() : [];
    const epInput = document.getElementById('train-episode-count');
    const epCount = epInput ? (parseInt(epInput.value, 10) || 15) : 15;
    const customRewards = this.getCustomRewards();

    try {
      const resp = await API.train(strategy, epCount, 'hybrid', false, customRewards);

      if (resp.success) {
        this.lastSummary = resp.summary;
        this.renderMetrics(resp.summary);
        this.renderCharts(resp.summary.metrics);

        if (banner) {
          banner.style.display = 'block';
          banner.style.background = '#ecfdf5';
          banner.style.borderRightColor = '#10b981';
          banner.innerHTML = `⚡ آموزش با پاداش‌های مشخص‌شده انجام شد! اکنون مسابقه روی نقشه یکسان در حال آغاز است تا تغییر رفتار هوش مصنوعی را ببینید...`;
        }

        // Run side-by-side comparison on identical map
        if (typeof ComparisonUI !== 'undefined' && ComparisonUI.runDualComparison) {
          await ComparisonUI.runDualComparison(ComparisonUI.currentPart2Seed);
        }
      }
    } catch (err) {
      alert("خطا در آموزش و شبیه‌سازی: " + err.message);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    }
  },

  renderMetrics(summary) {
    const successRateEl = document.getElementById('metric-success-rate');
    const avgRewardEl = document.getElementById('metric-avg-reward');
    const divergenceEl = document.getElementById('metric-divergence');
    const totalEpisodesEl = document.getElementById('metric-total-episodes');

    if (successRateEl) {
      const pct = Math.round(summary.final_success_rate * 100);
      successRateEl.textContent = `${pct}%`;
      successRateEl.style.color = pct >= 60 ? '#10b981' : (pct >= 30 ? '#f59e0b' : '#ef4444');
    }

    if (avgRewardEl) {
      const r = summary.avg_reward_last_5;
      avgRewardEl.innerHTML = `<span class="ltr-num">${r > 0 ? '+' : ''}${r}</span>`;
      avgRewardEl.style.color = r >= 0 ? '#10b981' : '#ef4444';
    }

    if (divergenceEl) {
      divergenceEl.textContent = summary.strategy_divergence_count;
    }

    if (totalEpisodesEl) {
      totalEpisodesEl.textContent = summary.total_episodes;
    }
  },

  renderCharts(metrics) {
    if (!metrics || metrics.length === 0) return;
    this.drawChart('chart-reward', metrics.map(m => m.total_reward), 'رشد پاداش کل', '#4f46e5', true);
    this.drawChart('chart-coins', metrics.map(m => m.coins_exited), 'سکه‌های موفق خروجی', '#10b981', false);
  },

  drawChart(canvasId, values, label, primaryColor, isRewardChart = false) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Handle high-DPI crisp rendering
    const rect = canvas.getBoundingClientRect();
    const cssWidth = rect.width > 50 ? rect.width : 460;
    const cssHeight = 180;
    const dpr = window.devicePixelRatio || 1;

    canvas.width = cssWidth * dpr;
    canvas.height = cssHeight * dpr;
    canvas.style.width = `${cssWidth}px`;
    canvas.style.height = `${cssHeight}px`;

    ctx.save();
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, cssWidth, cssHeight);

    if (values.length === 0) {
      ctx.restore();
      return;
    }

    // 1. Compute Moving Average (SMA)
    const win = Math.max(3, Math.min(25, Math.floor(values.length / 10)));
    const sma = [];
    for (let i = 0; i < values.length; i++) {
      const start = Math.max(0, i - win + 1);
      let sum = 0;
      for (let j = start; j <= i; j++) sum += values[j];
      sma.push(sum / (i - start + 1));
    }

    // Calculate range
    let minVal = Math.min(...values);
    let maxVal = Math.max(...values);
    if (isRewardChart) {
      // Include zero in range for rewards so baseline is visible
      minVal = Math.min(minVal, 0);
      maxVal = Math.max(maxVal, 20);
    } else {
      minVal = 0;
      maxVal = Math.max(maxVal, 5);
    }
    if (minVal === maxVal) maxVal += 1;

    const padLeft = 45;
    const padRight = 20;
    const padTop = 32;
    const padBottom = 26;
    const plotW = cssWidth - padLeft - padRight;
    const plotH = cssHeight - padTop - padBottom;

    const getY = (v) => padTop + plotH * (1 - (v - minVal) / (maxVal - minVal));
    const getX = (idx) => padLeft + (values.length === 1 ? plotW / 2 : (idx / (values.length - 1)) * plotW);

    // 2. Draw subtle horizontal grid lines & Y labels
    ctx.direction = 'ltr';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.font = '10px sans-serif';

    const numGridLines = 4;
    for (let g = 0; g <= numGridLines; g++) {
      const val = minVal + (g / numGridLines) * (maxVal - minVal);
      const y = getY(val);

      ctx.strokeStyle = '#f1f5f9';
      ctx.lineWidth = 1;
      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.moveTo(padLeft, y);
      ctx.lineTo(cssWidth - padRight, y);
      ctx.stroke();

      ctx.fillStyle = '#94a3b8';
      const labelText = Math.abs(val) >= 10 ? Math.round(val).toString() : val.toFixed(1);
      ctx.fillText(labelText, padLeft - 6, y);
    }

    // 3. Highlight Zero Baseline if spans negative to positive
    if (minVal < 0 && maxVal > 0) {
      const zeroY = getY(0);
      ctx.strokeStyle = '#cbd5e1';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(padLeft, zeroY);
      ctx.lineTo(cssWidth - padRight, zeroY);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = '#64748b';
      ctx.fillText('0', padLeft - 6, zeroY);
    }

    // 4. Draw Raw Episode Values (thin faint line)
    ctx.strokeStyle = primaryColor;
    ctx.globalAlpha = 0.22;
    ctx.lineWidth = 1.2;
    ctx.setLineDash([]);
    ctx.beginPath();
    values.forEach((v, idx) => {
      const x = getX(idx);
      const y = getY(v);
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.globalAlpha = 1.0;

    // 5. Draw Gradient Fill under Moving Average Trendline
    const zeroOrBottomY = minVal < 0 && maxVal > 0 ? getY(0) : getY(minVal);
    const grad = ctx.createLinearGradient(0, padTop, 0, zeroOrBottomY);
    grad.addColorStop(0, primaryColor === '#4f46e5' ? 'rgba(99, 102, 241, 0.25)' : 'rgba(16, 185, 129, 0.25)');
    grad.addColorStop(1, 'rgba(255, 255, 255, 0.0)');

    ctx.fillStyle = grad;
    ctx.beginPath();
    sma.forEach((v, idx) => {
      const x = getX(idx);
      const y = getY(v);
      if (idx === 0) {
        ctx.moveTo(x, zeroOrBottomY);
        ctx.lineTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    const lastX = getX(sma.length - 1);
    ctx.lineTo(lastX, zeroOrBottomY);
    ctx.closePath();
    ctx.fill();

    // 6. Draw Moving Average Bold Trendline
    ctx.strokeStyle = primaryColor;
    ctx.lineWidth = 2.8;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.beginPath();
    sma.forEach((v, idx) => {
      const x = getX(idx);
      const y = getY(v);
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // 7. Highlight Data Points
    if (values.length <= 35) {
      // Draw small dots for few episodes
      values.forEach((v, idx) => {
        const x = getX(idx);
        const y = getY(v);
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(x, y, 3.5, 0, 2 * Math.PI);
        ctx.fill();
        ctx.strokeStyle = primaryColor;
        ctx.lineWidth = 2;
        ctx.stroke();
      });
    } else {
      // Draw highlighted glowing dot on Start and End
      const startX = getX(0);
      const startY = getY(sma[0]);
      ctx.fillStyle = primaryColor;
      ctx.beginPath();
      ctx.arc(startX, startY, 4, 0, 2 * Math.PI);
      ctx.fill();

      const endX = getX(sma.length - 1);
      const endY = getY(sma[sma.length - 1]);
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(endX, endY, 5, 0, 2 * Math.PI);
      ctx.fill();
      ctx.strokeStyle = primaryColor;
      ctx.lineWidth = 2.5;
      ctx.stroke();
    }

    // 8. X-Axis Episode Markers
    ctx.fillStyle = '#94a3b8';
    ctx.textAlign = 'left';
    ctx.font = '10px sans-serif';
    ctx.fillText(`اپیزود ۱`, padLeft, cssHeight - 8);

    ctx.textAlign = 'right';
    ctx.fillText(`اپیزود ${values.length}`, cssWidth - padRight, cssHeight - 8);

    // 9. Trend Badge / Header Text
    const startVal = sma[0] || 0;
    const endVal = sma[sma.length - 1] || 0;
    const diff = endVal - startVal;

    ctx.textAlign = 'left';
    ctx.font = 'bold 11px sans-serif';
    ctx.fillStyle = primaryColor;

    let trendStr = '';
    if (diff > 5) {
      trendStr = `📈 رو به رشد (\u200E+${diff.toFixed(1)})`;
    } else if (diff < -5) {
      trendStr = `📉 نیاز به تمرین بیشتر (\u200E${diff.toFixed(1)})`;
    } else {
      trendStr = `⚖️ روند تثبیت‌شده`;
    }

    ctx.fillText(`${label} — ${trendStr}`, padLeft, 18);

    ctx.textAlign = 'right';
    ctx.font = '11px sans-serif';
    ctx.fillStyle = '#64748b';
    ctx.fillText(`میانگین فعلی: \u200E${endVal.toFixed(1)}`, cssWidth - padRight, 18);

    ctx.restore();
  }
};

