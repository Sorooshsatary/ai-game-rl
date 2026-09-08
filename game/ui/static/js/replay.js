/**
 * Replay Theater and Decision Inspector
 */
const ReplayUI = {
  currentReplay: null,
  currentStepIndex: 0,
  isPlaying: false,
  playTimer: null,
  playbackSpeedMs: 600,
  renderer: null,

  init() {
    const canvas = document.getElementById('replay-canvas');
    if (canvas) {
      this.renderer = new GridCanvasRenderer(canvas);
    }

    const sel = document.getElementById('replay-episode-select');
    if (sel) {
      sel.addEventListener('change', (e) => this.loadEpisode(parseInt(e.target.value)));
    }

    const scrubber = document.getElementById('replay-scrubber');
    if (scrubber) {
      scrubber.addEventListener('input', (e) => this.jumpToStep(parseInt(e.target.value)));
    }

    const btnPlay = document.getElementById('btn-replay-play');
    if (btnPlay) {
      btnPlay.addEventListener('click', () => this.togglePlay());
    }

    const btnNext = document.getElementById('btn-replay-next');
    if (btnNext) {
      btnNext.addEventListener('click', () => this.stepForward());
    }

    const btnPrev = document.getElementById('btn-replay-prev');
    if (btnPrev) {
      btnPrev.addEventListener('click', () => this.stepBackward());
    }

    const selSpeed = document.getElementById('replay-speed');
    if (selSpeed) {
      selSpeed.addEventListener('change', (e) => {
        this.playbackSpeedMs = parseInt(e.target.value);
        if (this.isPlaying) {
          this.pause();
          this.play();
        }
      });
    }
  },

  populateEpisodeSelector(episodeIds) {
    const sel = document.getElementById('replay-episode-select');
    if (!sel) return;
    sel.innerHTML = '';

    episodeIds.forEach(id => {
      const opt = document.createElement('option');
      opt.value = id;
      opt.textContent = `اپیزود ${id}`;
      sel.appendChild(opt);
    });

    if (episodeIds.length > 0) {
      // Auto load last episode
      const lastEp = episodeIds[episodeIds.length - 1];
      sel.value = lastEp;
      this.loadEpisode(lastEp);
    }
  },

  async loadEpisode(episodeId) {
    this.pause();
    try {
      this.currentReplay = await API.getReplay(episodeId);
      this.currentStepIndex = 0;

      const scrubber = document.getElementById('replay-scrubber');
      if (scrubber) {
        scrubber.max = Math.max(0, this.currentReplay.steps.length - 1);
        scrubber.value = 0;
      }

      this.renderCurrentStep();
    } catch (err) {
      console.error("Failed to load replay:", err);
    }
  },

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  },

  play() {
    if (!this.currentReplay || this.currentReplay.steps.length === 0) return;
    this.isPlaying = true;
    const btn = document.getElementById('btn-replay-play');
    if (btn) btn.textContent = '⏸ توقف';

    this.playTimer = setInterval(() => {
      if (this.currentStepIndex < this.currentReplay.steps.length - 1) {
        this.stepForward();
      } else {
        this.pause();
      }
    }, this.playbackSpeedMs);
  },

  pause() {
    this.isPlaying = false;
    if (this.playTimer) clearInterval(this.playTimer);
    const btn = document.getElementById('btn-replay-play');
    if (btn) btn.textContent = '▶ پخش';
  },

  stepForward() {
    if (!this.currentReplay) return;
    if (this.currentStepIndex < this.currentReplay.steps.length - 1) {
      this.currentStepIndex++;
      this.updateScrubber();
      this.renderCurrentStep();
    }
  },

  stepBackward() {
    if (!this.currentReplay) return;
    if (this.currentStepIndex > 0) {
      this.currentStepIndex--;
      this.updateScrubber();
      this.renderCurrentStep();
    }
  },

  jumpToStep(index) {
    if (!this.currentReplay) return;
    this.currentStepIndex = Math.max(0, Math.min(index, this.currentReplay.steps.length - 1));
    this.renderCurrentStep();
  },

  updateScrubber() {
    const scrubber = document.getElementById('replay-scrubber');
    if (scrubber) scrubber.value = this.currentStepIndex;
  },

  renderCurrentStep() {
    if (!this.currentReplay || this.currentReplay.steps.length === 0) return;

    const step = this.currentReplay.steps[this.currentStepIndex];
    const totalSteps = this.currentReplay.steps.length;

    // Render Canvas
    this.renderer.renderSingleAgentFrame(this.currentReplay.map_config, step.state_snapshot);

    // Update Decision Inspector
    document.getElementById('inspector-step-counter').textContent = `گام ${step.step_index} از ${totalSteps}`;
    document.getElementById('inspector-agent-lives').textContent = '❤️'.repeat(step.state_snapshot.lives || 0);
    document.getElementById('inspector-agent-coins').textContent = step.state_snapshot.coins_held || 0;
    document.getElementById('inspector-agent-diamonds').textContent = step.state_snapshot.diamonds_held || 0;
    document.getElementById('inspector-enemy-dist').textContent = `${step.state_snapshot.distances?.enemy || '-'} خانه`;

    // Action & Reward
    document.getElementById('inspector-selected-action').textContent = step.selected_action_fa;
    document.getElementById('inspector-action-type').textContent = step.was_exploratory ? '🎲 کاوش تصادفی' : '🧠 بر اساس ارزش آموخته‌شده';
    document.getElementById('inspector-step-reward').textContent = `${step.reward > 0 ? '+' : ''}${step.reward}`;

    // Side by side Q comparison
    this.renderQValuesList('inspector-prior-list', step.prior_q_values, step.selected_action);
    this.renderQValuesList('inspector-learned-list', step.learned_q_values, step.selected_action);

    // Explanation Banner
    document.getElementById('inspector-explanation').textContent = step.explanation_fa;
  },

  renderQValuesList(containerId, qValues, selectedAction) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    const sorted = Object.entries(qValues).sort((a, b) => b[1] - a[1]);
    const maxVal = sorted[0][1];

    const faActionMap = {
      'UP': 'بالا',
      'DOWN': 'پایین',
      'LEFT': 'چپ',
      'RIGHT': 'راست'
    };

    sorted.forEach(([act, val]) => {
      const isSelected = act === selectedAction;
      const isBest = Math.abs(val - maxVal) < 1e-4;

      const item = document.createElement('div');
      item.className = `action-badge ${isSelected ? 'best' : 'other'}`;
      item.style.display = 'flex';
      item.style.justifyContent = 'space-between';
      item.innerHTML = `
        <span>${faActionMap[act] || act}</span>
        <strong>${val.toFixed(1)}</strong>
      `;
      container.appendChild(item);
    });
  }
};
