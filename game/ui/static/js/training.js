/**
 * Training Center Manager with Charts and Metrics
 */
const TrainingUI = {
  lastSummary: null,

  init() {
    const btnTrain = document.getElementById('btn-start-training');
    if (btnTrain) {
      btnTrain.addEventListener('click', () => this.runTraining(false));
    }

    const btnRetrain = document.getElementById('btn-retrain');
    if (btnRetrain) {
      btnRetrain.addEventListener('click', () => this.runTraining(true));
    }
  },

  async runTraining(isRetrain = false) {
    const btn = isRetrain ? document.getElementById('btn-retrain') : document.getElementById('btn-start-training');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '⏳ در حال یادگیری و کاوش در محیط...';

    const strategy = StrategyUI.getStrategy();
    const epCount = isRetrain ? 15 : 30;

    try {
      const resp = isRetrain 
        ? await API.retrain(strategy, epCount, false)
        : await API.train(strategy, epCount);

      if (resp.success) {
        this.lastSummary = resp.summary;
        this.renderMetrics(resp.summary);
        this.renderCharts(resp.summary.metrics);

        // Update Replay selector
        ReplayUI.populateEpisodeSelector(resp.summary.available_replay_episodes);

        // Show prompt to switch to Replay
        const banner = document.getElementById('train-success-banner');
        if (banner) {
          banner.style.display = 'block';
        }
      }
    } catch (err) {
      alert("خطا در آموزش: " + err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalText;
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
