/**
 * Training Center Manager with Charts and Metrics
 */
const TrainingUI = {
  lastSummary: null,

  init() {
    const btnTrain = document.getElementById('btn-start-training');
    if (btnTrain) {
      btnTrain.addEventListener('click', () => this.runTraining());
    }

    const btnReset = document.getElementById('btn-reset-training');
    if (btnReset) {
      btnReset.addEventListener('click', () => this.resetTraining());
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
    const epCount = 25; // 25 episodes per training click

    try {
      const resp = await API.train(strategy, epCount);

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
          banner.innerHTML = `🎉 مرحله جدید آموزش با موفقیت پایان یافت! مجموعاً <strong>${resp.summary.total_episodes} اپیزود</strong> آموزش داده شده است. می‌توانید روند پیشرفت را در نمودارهای زیر مشاهده کنید.`;
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

  renderMetrics(summary) {
    document.getElementById('metric-success-rate').textContent = `${Math.round(summary.final_success_rate * 100)}%`;
    document.getElementById('metric-avg-reward').textContent = summary.avg_reward_last_5;
    document.getElementById('metric-divergence').textContent = summary.strategy_divergence_count;
    document.getElementById('metric-total-episodes').textContent = summary.total_episodes;
  },

  renderCharts(metrics) {
    this.drawChart('chart-reward', metrics.map(m => m.total_reward), 'پاداش کل', '#4f46e5');
    this.drawChart('chart-coins', metrics.map(m => m.coins_exited), 'سکه‌های خارج شده', '#10b981');
  },

  drawChart(canvasId, values, label, strokeColor) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (values.length === 0) return;

    const pad = 35;
    const w = canvas.width - pad * 2;
    const h = canvas.height - pad * 2;

    const minVal = Math.min(...values);
    const maxVal = Math.max(...values, minVal + 1);

    // Draw baseline / grid
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(pad, pad);
    ctx.lineTo(pad, canvas.height - pad);
    ctx.lineTo(canvas.width - pad, canvas.height - pad);
    ctx.stroke();

    // Zero-line if minVal < 0
    if (minVal < 0 && maxVal > 0) {
      const zeroY = pad + h * (1 - (0 - minVal) / (maxVal - minVal));
      ctx.strokeStyle = '#cbd5e1';
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(pad, zeroY);
      ctx.lineTo(canvas.width - pad, zeroY);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Plot line
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = 3;
    ctx.beginPath();

    values.forEach((v, idx) => {
      const x = pad + (idx / (values.length - 1)) * w;
      const y = pad + h * (1 - (v - minVal) / (maxVal - minVal));
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Plot points
    ctx.fillStyle = strokeColor;
    values.forEach((v, idx) => {
      const x = pad + (idx / (values.length - 1)) * w;
      const y = pad + h * (1 - (v - minVal) / (maxVal - minVal));
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, 2 * Math.PI);
      ctx.fill();
    });

    // Label
    ctx.fillStyle = '#64748b';
    ctx.font = '12px sans-serif';
    ctx.fillText(`${label} (شروع: ${values[0].toFixed(0)} ➔ پایان: ${values[values.length - 1].toFixed(0)})`, pad, pad - 10);
  }
};
