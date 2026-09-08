/**
 * API client for interacting with the RL game backend
 */
const API = {
  async getPresets() {
    const res = await fetch('/api/presets');
    return await res.json();
  },

  async getConfig() {
    const res = await fetch('/api/config');
    return await res.json();
  },

  async train(strategy, episodes = 30) {
    const res = await fetch('/api/train', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ strategy, episodes, from_scratch: true })
    });
    return await res.json();
  },

  async retrain(strategy, episodes = 15, fromScratch = false) {
    const res = await fetch('/api/retrain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ strategy, episodes, from_scratch: fromScratch })
    });
    return await res.json();
  },

  async getReplay(episodeId) {
    const res = await fetch(`/api/replay/${episodeId}`);
    if (!res.ok) throw new Error(`Replay ${episodeId} not found`);
    return await res.json();
  },

  async runCompetition() {
    const res = await fetch('/api/competition', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    return await res.json();
  }
};
