/**
 * Comparison and Rule-Based Strategy Simulation UI
 */
const ComparisonUI = {
  dualResult: null,
  stratTestResult: null,
  stratTestAnimId: null,
  dualAnimId: null,
  currentPart1Seed: 12345,
  currentPart2Seed: 54321,

  async init() {
    this.bindEvents();
    await this.renderInitialMaps();
  },

  bindEvents() {
    // 1. Single strategy test from Part 1
    const btnTestStrat = document.getElementById('btn-test-strategy');
    if (btnTestStrat) {
      btnTestStrat.addEventListener('click', () => this.runStrategyTest(this.currentPart1Seed));
    }

    const btnNewMap1 = document.getElementById('btn-new-map-part1');
    if (btnNewMap1) {
      btnNewMap1.addEventListener('click', () => {
        this.currentPart1Seed = Math.floor(Math.random() * 90000) + 10000;
        this.runStrategyTest(this.currentPart1Seed);
      });
    }

    // 2. Dual comparison from Part 2
    const btnRunDual = document.getElementById('btn-run-dual-comparison');
    if (btnRunDual) {
      btnRunDual.addEventListener('click', () => this.runDualComparison(this.currentPart2Seed));
    }

    const btnNewDualMap = document.getElementById('btn-new-dual-map');
    if (btnNewDualMap) {
      btnNewDualMap.addEventListener('click', () => {
        this.currentPart2Seed = Math.floor(Math.random() * 90000) + 10000;
        this.runDualComparison(this.currentPart2Seed);
      });
    }
  },

  async renderInitialMaps() {
    try {
      // 1. Initial preview on Part 1 canvas
      const res1 = await API.testStrategy(StrategyUI.getStrategy(), this.currentPart1Seed);
      if (res1.success && res1.map_config) {
        this.stratTestResult = res1;
        const canvas1 = document.getElementById('strategy-test-canvas');
        const agentStart = res1.map_config.agent_start || (res1.summary && res1.summary.agent_start) || [0, 0];
        const enemyStart = res1.map_config.enemy_start || (res1.summary && res1.summary.enemy_start) || [res1.map_config.width - 1, res1.map_config.height - 1];
        if (canvas1) {
          const renderer1 = new GridCanvasRenderer(canvas1);
          renderer1.renderSingleAgentFrame(res1.map_config, {
            agent_pos: agentStart,
            enemy_pos: enemyStart,
            coins: res1.map_config.coins || [],
            diamonds: res1.map_config.diamonds || [],
          });
        }

        // 2. Initial preview on Part 2 dual canvases
        const canvasStrat = document.getElementById('canvas-compare-strat');
        const canvasRL = document.getElementById('canvas-compare-rl');
        if (canvasStrat && canvasRL) {
          const rendererS = new GridCanvasRenderer(canvasStrat);
          const rendererR = new GridCanvasRenderer(canvasRL);
          rendererS.renderSingleAgentFrame(res1.map_config, {
            agent_pos: agentStart,
            enemy_pos: enemyStart,
            coins: res1.map_config.coins || [],
            diamonds: res1.map_config.diamonds || [],
          });
          rendererR.renderSingleAgentFrame(res1.map_config, {
            agent_pos: agentStart,
            enemy_pos: enemyStart,
            coins: res1.map_config.coins || [],
            diamonds: res1.map_config.diamonds || [],
          });
        }
      }
    } catch (e) {
      console.warn("Could not pre-render initial maps:", e);
    }
  },

  async runStrategyTest(seed = null) {
    const btn = document.getElementById('btn-test-strategy');
    const logBox = document.getElementById('strategy-test-log');
    const critiqueBox = document.getElementById('strategy-test-critique');
    if (!btn) return;

    btn.disabled = true;
    btn.textContent = '⏳ در حال شبیه‌سازی استراتژی...';
    if (logBox) logBox.textContent = 'در حال شبیه‌سازی حرکت عامل روی نقشه...';
    if (critiqueBox) critiqueBox.innerHTML = '';

    try {
      const res = await API.testStrategy(StrategyUI.getStrategy(), seed);
      if (!res.success) throw new Error('خطا در شبیه‌سازی استراتژی');

      this.stratTestResult = res;
      this.renderStrategyTestReplay(res);
    } catch (err) {
      alert('خطا در شبیه‌سازی: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.textContent = '▶ اجرای استراتژی من روی نقشه';
    }
  },

  renderStrategyTestReplay(res) {
    const canvas = document.getElementById('strategy-test-canvas');
    const logBox = document.getElementById('strategy-test-log');
    const critiqueBox = document.getElementById('strategy-test-critique');
    const livesEl = document.getElementById('part1-agent-lives');
    const coinsEl = document.getElementById('part1-agent-coins');
    const diamondsEl = document.getElementById('part1-agent-diamonds');
    const stepEl = document.getElementById('part1-step-counter');
    const speedSelect = document.getElementById('part1-speed');

    if (!canvas) return;

    const renderer = new GridCanvasRenderer(canvas);
    const steps = res.summary.steps;
    const mapConfig = res.map_config;
    const speed = speedSelect ? parseInt(speedSelect.value) || 350 : 350;

    let idx = 0;
    if (this.stratTestAnimId) clearInterval(this.stratTestAnimId);

    const agentStart = (res.summary && res.summary.agent_start) || mapConfig.agent_start || [0, 0];
    const enemyStart = (res.summary && res.summary.enemy_start) || mapConfig.enemy_start || [mapConfig.width - 1, mapConfig.height - 1];

    renderer.renderSingleAgentFrame(mapConfig, {
      agent_pos: agentStart,
      enemy_pos: enemyStart,
      coins: mapConfig.coins || [],
      diamonds: mapConfig.diamonds || [],
    });

    if (livesEl) livesEl.textContent = '❤️❤️❤️';
    if (coinsEl) coinsEl.textContent = '0 🪙';
    if (diamondsEl) diamondsEl.textContent = '0 💎';
    if (stepEl) stepEl.textContent = 'موقعیت آغازین (گام ۰)';
    if (logBox) {
      logBox.innerHTML = `
        <div style="font-size: 0.88rem; color: #475569;">
          عامل در خانه شروع [${agentStart.join(', ')}] مستقر شد و آماده حرکت است...
        </div>
      `;
    }

    const drawStep = () => {
      if (idx >= steps.length) {
        clearInterval(this.stratTestAnimId);
        // Show educational critique
        let critiqueHtml = '';
        if (res.summary.termination_reason === 'DEATH') {
          critiqueHtml = `
            <div style="background: #fef2f2; border-right: 4px solid #ef4444; padding: 12px; border-radius: 8px; margin-top: 10px;">
              <strong style="color: #b91c1c;">⚠️ نتیجه: عامل قانون‌محور شکست خورد و توسط هیولا شکار شد!</strong>
              <p style="font-size: 0.88rem; color: #7f1d1d; margin-top: 6px; line-height: 1.6;">
                استراتژی شما به عامل گفت دنبال اهدافش برود، اما چون شروط صلب بودند، نتوانست مسیر حرکت هیولا را پیش‌بینی کند و گیر افتاد.
                <strong>این دقیقاً دلیلی است که به هوش مصنوعی و یادگیری تقویتی نیاز داریم تا مسیرها را با تجربه کشف کند!</strong>
              </p>
            </div>
          `;
        } else if (res.summary.termination_reason === 'TIMEOUT') {
          critiqueHtml = `
            <div style="background: #fffbeb; border-right: 4px solid #f59e0b; padding: 12px; border-radius: 8px; margin-top: 10px;">
              <strong style="color: #b45309;">⏳ نتیجه: زمان تمام شد و ربات سرگردان ماند!</strong>
              <p style="font-size: 0.88rem; color: #92400e; margin-top: 6px; line-height: 1.6;">
                ربات نتوانست قبل از پایان فرصت، مسیر رسیدن به درب خروج را پیدا کند. هوش مصنوعی یادگیرنده مسیر بهینه را با تجربه پیدا می‌کند.
              </p>
            </div>
          `;
        } else {
          critiqueHtml = `
            <div style="background: #ecfdf5; border-right: 4px solid #10b981; padding: 12px; border-radius: 8px; margin-top: 10px;">
              <strong style="color: #047857;">🎉 آفرین! استراتژی در این نقشه موفق شد و سالم خارج شد.</strong>
              <p style="font-size: 0.88rem; color: #065f46; margin-top: 6px; line-height: 1.6;">
                حالا در بخش ۲ بروید و ببینید آیا این استراتژی در برابر هوش مصنوعی یادگیرنده هم می‌تواند برنده شود یا خیر!
              </p>
            </div>
          `;
        }
        if (critiqueBox) critiqueBox.innerHTML = critiqueHtml;
        return;
      }

      const st = steps[idx];
      renderer.renderSingleAgentFrame(mapConfig, {
        agent_pos: st.agent_pos,
        enemy_pos: st.enemy_pos,
        coins: st.coins_left,
        diamonds: st.diamonds_left,
        enemy_stunned: st.enemy_stunned,
        stun_timer: st.stun_timer,
      });

      // Update live indicators
      if (livesEl) livesEl.textContent = '❤️'.repeat(Math.max(0, st.lives));
      if (coinsEl) coinsEl.textContent = `${st.coins} 🪙`;
      if (diamondsEl) diamondsEl.textContent = `${st.diamonds} 💎`;
      if (stepEl) stepEl.textContent = `گام ${st.step_index}`;

      if (logBox) {
        logBox.innerHTML = `
          <div style="font-size: 0.88rem; line-height: 1.6;">
            <div><strong>گام ${st.step_index}:</strong> حرکت به سمت <span style="color: #2563eb; font-weight: bold;">${st.action_fa}</span></div>
            <div style="color: #475569; font-size: 0.82rem; margin-top: 2px;">علت تصمیم: ${st.rule_or_reason}</div>
          </div>
        `;
      }
      idx++;
    };

    this.stratTestAnimId = setInterval(drawStep, speed);
  },

  async runDualComparison(seed = null) {
    const btn = document.getElementById('btn-run-dual-comparison');
    const statusBox = document.getElementById('dual-status-banner');
    if (btn) {
      btn.disabled = true;
      btn.textContent = '⏳ در حال اجرای مسابقه روی نقشه یکسان...';
    }
    if (statusBox) {
      statusBox.style.display = 'inline-block';
      statusBox.innerHTML = '🤖 اعزام هر دو عامل به نقشه یکسان با منابع مشترک...';
    }

    try {
      const res = await API.runDualComparison(StrategyUI.getStrategy(), seed);
      if (!res.success) throw new Error('خطا در دریافت نتایج مقایسه');

      this.dualResult = res.result;
      this.displayDualComparison(res.result);
    } catch (err) {
      alert('خطا در اجرای مسابقه مقایسه‌ای: ' + err.message);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = '⚔️ اجرای مجدد مسابقه مقایسه‌ای';
      }
      if (statusBox) {
        statusBox.style.display = 'none';
      }
    }
  },

  displayDualComparison(result) {
    // 1. Fill comparison table
    const tableBody = document.getElementById('dual-comparison-table-body');
    if (tableBody && result.comparison_table) {
      tableBody.innerHTML = result.comparison_table.map(row => `
        <tr>
          <td style="font-weight: 700; color: #334155;">${row.metric}</td>
          <td style="color: #0284c7; font-weight: 700;">${row.strategy}</td>
          <td style="color: #16a34a; font-weight: 800;">${row.rl}</td>
        </tr>
      `).join('');
    }

    // 2. Educational Analysis Card
    const analysisBox = document.getElementById('dual-analysis-card');
    if (analysisBox) {
      analysisBox.style.display = 'block';
      let winnerBadge = '';
      if (result.winner === 'rl') {
        winnerBadge = '<span class="status-pill success" style="font-size: 0.85rem;">برنده: هوش مصنوعی یادگیرنده 🏆</span>';
      } else if (result.winner === 'strategy') {
        winnerBadge = '<span class="status-pill success" style="background: #e0f2fe; color: #0369a1; font-size: 0.85rem;">برنده: استراتژی شرطی شما 👏</span>';
      } else {
        winnerBadge = '<span class="status-pill" style="background: #fef3c7; color: #92400e; font-size: 0.85rem;">نتیجه: مساوی 🤝</span>';
      }

      analysisBox.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; flex-wrap: wrap; gap: 8px;">
          <h4 style="margin: 0; color: #1e293b; font-size: 1.05rem;">🔬 کالبدشکافی و نتیجه مسابقه آموزشی</h4>
          ${winnerBadge}
        </div>
        <p style="line-height: 1.8; color: #334155; font-size: 0.92rem;">${result.analysis_fa}</p>
      `;
    }

    // 3. Start Dual Canvas Playback
    this.startDualPlayback(result);
  },

  startDualPlayback(result) {
    const canvasStrat = document.getElementById('canvas-compare-strat');
    const canvasRL = document.getElementById('canvas-compare-rl');
    const speedSelect = document.getElementById('part2-speed');
    if (!canvasStrat || !canvasRL) return;

    const rendererStrat = new GridCanvasRenderer(canvasStrat);
    const rendererRL = new GridCanvasRenderer(canvasRL);

    const stratSteps = result.strategy_run.steps;
    const rlSteps = result.rl_run.steps;
    const maxSteps = Math.max(stratSteps.length, rlSteps.length);
    const speed = speedSelect ? parseInt(speedSelect.value) || 450 : 450;

    if (this.dualAnimId) clearInterval(this.dualAnimId);

    const agentStart = (result.strategy_run && result.strategy_run.agent_start) || result.map_config.agent_start || [0, 0];
    const enemyStart = (result.strategy_run && result.strategy_run.enemy_start) || result.map_config.enemy_start || [result.map_config.width - 1, result.map_config.height - 1];

    rendererStrat.renderSingleAgentFrame(result.map_config, {
      agent_pos: agentStart,
      enemy_pos: enemyStart,
      coins: result.map_config.coins || [],
      diamonds: result.map_config.diamonds || [],
    });

    rendererRL.renderSingleAgentFrame(result.map_config, {
      agent_pos: agentStart,
      enemy_pos: enemyStart,
      coins: result.map_config.coins || [],
      diamonds: result.map_config.diamonds || [],
    });

    const infoStrat = document.getElementById('info-compare-strat');
    const infoRL = document.getElementById('info-compare-rl');
    if (infoStrat) {
      infoStrat.innerHTML = `<div><strong>موقعیت آغازین (گام ۰):</strong> آماده آغاز رقابت</div>`;
    }
    if (infoRL) {
      infoRL.innerHTML = `<div><strong>موقعیت آغازین (گام ۰):</strong> آماده آغاز رقابت</div>`;
    }

    let step = 0;
    const tick = () => {
      if (step >= maxSteps) {
        clearInterval(this.dualAnimId);
        return;
      }

      const sStep = stratSteps[Math.min(step, stratSteps.length - 1)];
      const rStep = rlSteps[Math.min(step, rlSteps.length - 1)];

      if (sStep) {
        rendererStrat.renderSingleAgentFrame(result.map_config, {
          agent_pos: sStep.agent_pos,
          enemy_pos: sStep.enemy_pos,
          coins: sStep.coins_left,
          diamonds: sStep.diamonds_left,
          enemy_stunned: sStep.enemy_stunned,
          stun_timer: sStep.stun_timer,
        });
      }

      if (rStep) {
        rendererRL.renderSingleAgentFrame(result.map_config, {
          agent_pos: rStep.agent_pos,
          enemy_pos: rStep.enemy_pos,
          coins: rStep.coins_left,
          diamonds: rStep.diamonds_left,
          enemy_stunned: rStep.enemy_stunned,
          stun_timer: rStep.stun_timer,
        });
      }

      if (infoStrat && sStep) {
        infoStrat.innerHTML = `
          <div><strong>گام ${sStep.step_index}:</strong> حرکت به سمت <strong>${sStep.action_fa}</strong></div>
          <div style="font-size: 0.78rem; color: #64748b; margin-top: 2px;">علت: ${sStep.rule_or_reason}</div>
          <div style="margin-top: 4px; font-weight: bold; color: #0284c7;">جان: ${'❤️'.repeat(Math.max(0, sStep.lives))} | سکه: ${sStep.coins} 🪙 | الماس: ${sStep.diamonds} 💎</div>
        `;
      }
      if (infoRL && rStep) {
        infoRL.innerHTML = `
          <div><strong>گام ${rStep.step_index}:</strong> حرکت به سمت <strong>${rStep.action_fa}</strong></div>
          <div style="font-size: 0.78rem; color: #64748b; margin-top: 2px;">علت: ${rStep.rule_or_reason}</div>
          <div style="margin-top: 4px; font-weight: bold; color: #16a34a;">جان: ${'❤️'.repeat(Math.max(0, rStep.lives))} | سکه: ${rStep.coins} 🪙 | الماس: ${rStep.diamonds} 💎</div>
        `;
      }

      step++;
    };

    this.dualAnimId = setInterval(tick, speed);
  }
};
