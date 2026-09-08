/**
 * API client for interacting with the RL game backend, Auth & Admin
 */
const API = {
  TOKEN_KEY: 'rl_game_token',

  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  },

  setToken(token) {
    if (token) {
      localStorage.setItem(this.TOKEN_KEY, token);
    } else {
      localStorage.removeItem(this.TOKEN_KEY);
    }
  },

  clearToken() {
    localStorage.removeItem(this.TOKEN_KEY);
  },

  authHeaders(extra = {}) {
    const headers = { 'Content-Type': 'application/json', ...extra };
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  },

  // ----------------- Public Game API -----------------
  async getPresets() {
    const res = await fetch('/api/presets');
    return await res.json();
  },

  async getConfig() {
    const res = await fetch('/api/config');
    return await res.json();
  },

  async train(strategy, episodes = null, mode = 'hybrid', fromScratch = false) {
    const payload = { strategy, mode, from_scratch: fromScratch };
    if (episodes !== null && episodes !== undefined) {
      payload.episodes = episodes;
    }
    const res = await fetch('/api/train', {
      method: 'POST',
      headers: this.authHeaders(),
      body: JSON.stringify(payload)
    });
    return await res.json();
  },

  async retrain(strategy, episodes = 15, fromScratch = false) {
    const res = await fetch('/api/retrain', {
      method: 'POST',
      headers: this.authHeaders(),
      body: JSON.stringify({ strategy, episodes, from_scratch: fromScratch })
    });
    return await res.json();
  },

  async resetTraining() {
    const res = await fetch('/api/train/reset', {
      method: 'POST',
      headers: this.authHeaders(),
    });
    return await res.json();
  },

  async testStrategy(strategy, seed = null) {
    const res = await fetch('/api/strategy/test', {
      method: 'POST',
      headers: this.authHeaders(),
      body: JSON.stringify({ strategy, seed })
    });
    return await res.json();
  },

  async runDualComparison(strategy, seed = null) {
    const res = await fetch('/api/comparison/dual', {
      method: 'POST',
      headers: this.authHeaders(),
      body: JSON.stringify({ strategy, seed })
    });
    return await res.json();
  },

  // ----------------- Authentication API -----------------
  async login(username, password) {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'خطا در ورود به حساب کاربری');
    }
    if (data.token) {
      this.setToken(data.token);
    }
    return data;
  },

  async logout() {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: this.authHeaders()
      });
    } finally {
      this.clearToken();
    }
  },

  async getMe() {
    const token = this.getToken();
    if (!token) return { authenticated: false, user: null };

    try {
      const res = await fetch('/api/auth/me', {
        headers: this.authHeaders()
      });
      if (!res.ok) {
        this.clearToken();
        return { authenticated: false, user: null };
      }
      return await res.json();
    } catch {
      return { authenticated: false, user: null };
    }
  },

  // ----------------- Admin Management API -----------------
  async adminGetUsers() {
    const res = await fetch('/api/admin/users', {
      headers: this.authHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'خطا در دریافت لیست کاربران');
    return data.users;
  },

  async adminCreateUser(username, password, role) {
    const res = await fetch('/api/admin/users', {
      method: 'POST',
      headers: this.authHeaders(),
      body: JSON.stringify({ username, password, role })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'خطا در ایجاد کاربر');
    return data;
  },

  async adminUpdateUserRole(userId, role) {
    const res = await fetch(`/api/admin/users/${userId}/role`, {
      method: 'PUT',
      headers: this.authHeaders(),
      body: JSON.stringify({ role })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'خطا در تغییر سطح دسترسی');
    return data;
  },

  async adminDeleteUser(userId) {
    const res = await fetch(`/api/admin/users/${userId}`, {
      method: 'DELETE',
      headers: this.authHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'خطا در حذف کاربر');
    return data;
  },

  async adminGetConfig() {
    const res = await fetch('/api/admin/config', {
      headers: this.authHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'خطا در دریافت تنظیمات ادمین');
    return data.config;
  },

  async adminSaveConfig(configData) {
    const res = await fetch('/api/admin/config', {
      method: 'POST',
      headers: this.authHeaders(),
      body: JSON.stringify(configData)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'خطا در ذخیره تنظیمات');
    return data;
  },

  async adminResetConfig() {
    const res = await fetch('/api/admin/config/reset', {
      method: 'POST',
      headers: this.authHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'خطا در بازنشانی تنظیمات');
    return data;
  }
};
