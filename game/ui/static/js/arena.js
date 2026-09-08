/**
 * Multi-Agent Competition Arena UI Manager
 */
const ArenaUI = {
  currentMatch: null,
  currentFrameIndex: 0,
  isPlaying: false,
  timer: null,
  renderer: null,
  speedMs: 350,

  init() {
    const canvas = document.getElementById('arena-canvas');
    if (canvas) {
      this.renderer = new GridCanvasRenderer(canvas);
    }

    const btnStart = document.getElementById('btn-start-arena');
    if (btnStart) {
      btnStart.addEventListener('click', () => this.runCompetitionMatch());
    }

    const btnPlay = document.getElementById('btn-arena-play');
    if (btnPlay) {
      btnPlay.addEventListener('click', () => this.togglePlay());
    }

    const scrubber = document.getElementById('arena-scrubber');
    if (scrubber) {
      scrubber.addEventListener('input', (e) => this.jumpToFrame(parseInt(e.target.value)));
    }
  },

  async runCompetitionMatch() {
    const btn = document.getElementById('btn-start-arena');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '⚔️ در حال ساخت نقشه ندیده و شروع مسابقه...';

    try {
      this.currentMatch = await API.runCompetition();
      this.currentFrameIndex = 0;

      const scrubber = document.getElementById('arena-scrubber');
      if (scrubber) {
        scrubber.max = Math.max(0, this.currentMatch.frames.length - 1);
        scrubber.value = 0;
      }

      this.renderLeaderboard(this.currentMatch.leaderboard);
      this.renderFrame();
      this.play();
    } catch (err) {
      alert("خطا در اجرای مسابقه: " + err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalText;
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
    if (!this.currentMatch || this.currentMatch.frames.length === 0) return;
    this.isPlaying = true;
    const btn = document.getElementById('btn-arena-play');
    if (btn) btn.textContent = '⏸ توقف مسابقه';

    this.timer = setInterval(() => {
      if (this.currentFrameIndex < this.currentMatch.frames.length - 1) {
        this.currentFrameIndex++;
        const scrubber = document.getElementById('arena-scrubber');
        if (scrubber) scrubber.value = this.currentFrameIndex;
        this.renderFrame();
      } else {
        this.pause();
      }
    }, this.speedMs);
  },

  pause() {
    this.isPlaying = false;
    if (this.timer) clearInterval(this.timer);
    const btn = document.getElementById('btn-arena-play');
    if (btn) btn.textContent = '▶ پخش مسابقه';
  },

  jumpToFrame(idx) {
    if (!this.currentMatch) return;
    this.currentFrameIndex = Math.max(0, Math.min(idx, this.currentMatch.frames.length - 1));
    this.renderFrame();
  },

  renderFrame() {
    if (!this.currentMatch) return;
    const frame = this.currentMatch.frames[this.currentFrameIndex];

    // Render Canvas
    this.renderer.renderArenaFrame(this.currentMatch.map_config, frame);

    // Frame counter
    document.getElementById('arena-step-label').textContent = `گام ${frame.step} از ${this.currentMatch.total_steps}`;

    // Update live event log
    const eventFeed = document.getElementById('arena-events-feed');
    if (eventFeed && frame.events) {
      frame.events.forEach(ev => {
        const item = document.createElement('div');
        item.className = 'event-feed-item';
        item.textContent = `[گام ${frame.step}] ${ev}`;
        eventFeed.prepend(item);
      });
    }
  },

  renderLeaderboard(entries) {
    const tbody = document.getElementById('leaderboard-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    entries.forEach((e) => {
      const tr = document.createElement('tr');
      if (e.rank === 1) tr.className = 'rank-1';

      let badgeClass = 'default';
      if (e.rank === 1) badgeClass = 'gold';
      else if (e.rank === 2) badgeClass = 'silver';
      else if (e.rank === 3) badgeClass = 'bronze';

      tr.innerHTML = `
        <td><span class="rank-badge ${badgeClass}">${e.rank}</span></td>
        <td><strong>${e.agent_name}</strong></td>
        <td><span style="font-size: 1.1rem; font-weight: 800; color: #f59e0b;">🪙 ${e.coins_exited}</span></td>
        <td>${'❤️'.repeat(e.lives)}</td>
        <td>${e.steps}</td>
        <td><span class="status-pill ${e.has_exited ? 'success' : 'danger'}">${e.status_fa}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }
};
