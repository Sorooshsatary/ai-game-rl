/**
 * Admin Panel UI Controller
 */
const AdminUI = {
  users: [],
  currentConfig: null,

  init() {
    this.bindEvents();
  },

  bindEvents() {
    // Form: Create user
    const formCreateUser = document.getElementById('form-create-user');
    if (formCreateUser) {
      formCreateUser.addEventListener('submit', (e) => {
        e.preventDefault();
        this.submitCreateUser();
      });
    }

    // Form: Save system config
    const formConfig = document.getElementById('form-admin-config');
    if (formConfig) {
      formConfig.addEventListener('submit', (e) => {
        e.preventDefault();
        this.submitSaveConfig();
      });
    }

    // Button: Reset config to default
    const btnResetConfig = document.getElementById('btn-reset-admin-config');
    if (btnResetConfig) {
      btnResetConfig.addEventListener('click', () => this.confirmResetConfig());
    }
  },

  async loadData() {
    await Promise.all([this.loadUsers(), this.loadConfig()]);
  },

  async loadUsers() {
    const tbody = document.getElementById('admin-users-tbody');
    if (!tbody) return;

    try {
      this.users = await API.adminGetUsers();
      this.renderUsers();
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="5" style="color: #ef4444; text-align: center;">خطا در دریافت کاربران: ${err.message}</td></tr>`;
    }
  },

  renderUsers() {
    const tbody = document.getElementById('admin-users-tbody');
    if (!tbody) return;

    if (!this.users || this.users.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #64748b;">هیچ کاربری یافت نشد.</td></tr>';
      return;
    }

    const currentUserId = AuthUI.currentUser ? AuthUI.currentUser.id : null;

    tbody.innerHTML = this.users.map(u => {
      const isSelf = u.id === currentUserId;
      const roleFa = u.role === 'admin' ? 'مدیر سیستم' : 'دانش‌آموز';
      const roleBadgeClass = u.role === 'admin' ? 'badge-admin' : 'badge-user';
      const toggleRoleTarget = u.role === 'admin' ? 'user' : 'admin';
      const toggleRoleLabel = u.role === 'admin' ? 'تبدیل به کاربر عادی' : 'ارتقا به مدیر';

      return `
        <tr>
          <td style="font-weight: bold; color: #334155;">#${u.id}</td>
          <td>
            <strong>${u.username}</strong>
            ${isSelf ? '<span style="color: #6366f1; font-size: 0.75rem; margin-right: 6px;">(حساب شما)</span>' : ''}
          </td>
          <td>
            <span class="role-badge ${roleBadgeClass}">${roleFa}</span>
          </td>
          <td style="color: #64748b; font-size: 0.85rem;">${u.created_at || '-'}</td>
          <td>
            <div style="display: flex; gap: 6px; align-items: center;">
              <button
                class="btn btn-secondary"
                style="padding: 4px 10px; font-size: 0.8rem;"
                onclick="AdminUI.changeRole(${u.id}, '${toggleRoleTarget}')"
                ${isSelf && u.role === 'admin' ? 'disabled title="نمی‌توانید دسترسی مدیر را از خود سلب کنید"' : ''}
              >
                ${toggleRoleLabel}
              </button>
              <button
                class="btn btn-danger-sm"
                style="padding: 4px 10px; font-size: 0.8rem;"
                onclick="AdminUI.deleteUser(${u.id}, '${u.username}')"
                ${isSelf ? 'disabled title="نمی‌توانید حساب خود را حذف کنید"' : ''}
              >
                حذف
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  },

  async submitCreateUser() {
    const userInput = document.getElementById('new-username');
    const passInput = document.getElementById('new-password');
    const roleSelect = document.getElementById('new-role');
    const msgBox = document.getElementById('create-user-msg');

    if (!userInput || !passInput || !roleSelect) return;
    const username = userInput.value.trim();
    const password = passInput.value;
    const role = roleSelect.value;

    if (!username || !password) {
      if (msgBox) {
        msgBox.innerHTML = '<span style="color: #ef4444;">لطفاً تمام فیلدها را پر کنید.</span>';
      }
      return;
    }

    try {
      await API.adminCreateUser(username, password, role);
      userInput.value = '';
      passInput.value = '';
      if (msgBox) {
        msgBox.innerHTML = '<span style="color: #10b981;">✅ کاربر جدید با موفقیت اضافه شد.</span>';
        setTimeout(() => { msgBox.innerHTML = ''; }, 4000);
      }
      await this.loadUsers();
    } catch (err) {
      if (msgBox) {
        msgBox.innerHTML = `<span style="color: #ef4444;">❌ ${err.message}</span>`;
      }
    }
  },

  async changeRole(userId, newRole) {
    const roleFa = newRole === 'admin' ? 'مدیر سیستم' : 'کاربر عادی';
    if (!confirm(`آیا از تغییر سطح دسترسی این کاربر به «${roleFa}» اطمینان دارید؟`)) {
      return;
    }

    try {
      await API.adminUpdateUserRole(userId, newRole);
      await this.loadUsers();
    } catch (err) {
      alert('خطا در تغییر سطح دسترسی: ' + err.message);
    }
  },

  async deleteUser(userId, username) {
    if (!confirm(`آیا از حذف کامل حساب کاربری «${username}» مطمئن هستید؟ این عملیات غیرقابل بازگشت است.`)) {
      return;
    }

    try {
      await API.adminDeleteUser(userId);
      await this.loadUsers();
    } catch (err) {
      alert('خطا در حذف کاربر: ' + err.message);
    }
  },

  async loadConfig() {
    try {
      this.currentConfig = await API.adminGetConfig();
      this.populateConfigForm(this.currentConfig);
    } catch (err) {
      console.error("خطا در بارگذاری تنظیمات:", err);
    }
  },

  populateConfigForm(cfg) {
    if (!cfg) return;

    // Environment
    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.value = val;
    };

    setVal('cfg-grid-width', cfg.grid_width || 8);
    setVal('cfg-grid-height', cfg.grid_height || 8);
    setVal('cfg-num-coins', cfg.num_coins || 5);
    setVal('cfg-num-diamonds', cfg.num_diamonds || 2);
    setVal('cfg-initial-lives', cfg.initial_lives || 3);
    setVal('cfg-max-steps', cfg.max_steps || 100);
    setVal('cfg-diamond-multiplier', cfg.diamond_multiplier || 2);

    // Rewards
    const rew = cfg.rewards || {};
    setVal('cfg-rew-coin', rew.coin ?? 10.0);
    setVal('cfg-rew-convert', rew.convert ?? 20.0);
    setVal('cfg-rew-diamond', rew.diamond ?? 0.5);
    setVal('cfg-rew-lose-life', rew.lose_life ?? -15.0);
    setVal('cfg-rew-death', rew.death ?? -50.0);
    setVal('cfg-rew-exit', rew.exit ?? 5.0);
    setVal('cfg-rew-step', rew.step ?? -0.1);

    // RL
    const rl = cfg.rl || {};
    setVal('cfg-rl-alpha', rl.alpha ?? 0.2);
    setVal('cfg-rl-gamma', rl.gamma ?? 0.9);
    setVal('cfg-rl-episodes', rl.episodes ?? 30);
  },

  async submitSaveConfig() {
    const getVal = (id) => {
      const el = document.getElementById(id);
      return el ? parseFloat(el.value) : 0;
    };

    const payload = {
      grid_width: parseInt(document.getElementById('cfg-grid-width').value),
      grid_height: parseInt(document.getElementById('cfg-grid-height').value),
      num_coins: parseInt(document.getElementById('cfg-num-coins').value),
      num_diamonds: parseInt(document.getElementById('cfg-num-diamonds').value),
      initial_lives: parseInt(document.getElementById('cfg-initial-lives').value),
      max_steps: parseInt(document.getElementById('cfg-max-steps').value),
      diamond_multiplier: parseInt(document.getElementById('cfg-diamond-multiplier').value) || 2,
      rewards: {
        coin: getVal('cfg-rew-coin'),
        convert: getVal('cfg-rew-convert'),
        diamond: getVal('cfg-rew-diamond'),
        lose_life: getVal('cfg-rew-lose-life'),
        death: getVal('cfg-rew-death'),
        exit: getVal('cfg-rew-exit'),
        step: getVal('cfg-rew-step'),
      },
      rl: {
        alpha: getVal('cfg-rl-alpha'),
        gamma: getVal('cfg-rl-gamma'),
        episodes: parseInt(document.getElementById('cfg-rl-episodes').value),
      }
    };

    const statusBox = document.getElementById('config-save-status');
    const submitBtn = document.getElementById('btn-save-admin-config');

    if (submitBtn) submitBtn.disabled = true;

    try {
      const res = await API.adminSaveConfig(payload);
      if (statusBox) {
        statusBox.style.display = 'block';
        statusBox.className = 'explanation-banner';
        statusBox.style.background = '#ecfdf5';
        statusBox.style.borderRightColor = '#10b981';
        statusBox.innerHTML = `✅ ${res.message}`;
        setTimeout(() => { statusBox.style.display = 'none'; }, 4000);
      }
      // Re-render initial maps with new config dimensions
      if (typeof ComparisonUI !== 'undefined' && ComparisonUI.renderInitialMaps) {
        ComparisonUI.renderInitialMaps();
      }
    } catch (err) {
      if (statusBox) {
        statusBox.style.display = 'block';
        statusBox.className = 'explanation-banner';
        statusBox.style.background = '#fef2f2';
        statusBox.style.borderRightColor = '#ef4444';
        statusBox.innerHTML = `❌ خطا در ذخیره: ${err.message}`;
      }
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  },

  async confirmResetConfig() {
    if (!confirm('آیا مطمئن هستید که می‌خواهید تمام پارامترها به مقادیر اولیه کارخانه بازگردانده شوند؟')) {
      return;
    }

    try {
      const res = await API.adminResetConfig();
      this.populateConfigForm(res.config);
      const statusBox = document.getElementById('config-save-status');
      if (statusBox) {
        statusBox.style.display = 'block';
        statusBox.className = 'explanation-banner';
        statusBox.style.background = '#ecfdf5';
        statusBox.style.borderRightColor = '#10b981';
        statusBox.innerHTML = `✅ ${res.message}`;
        setTimeout(() => { statusBox.style.display = 'none'; }, 4000);
      }
      if (typeof ComparisonUI !== 'undefined' && ComparisonUI.renderInitialMaps) {
        ComparisonUI.renderInitialMaps();
      }
    } catch (err) {
      alert('خطا در بازنشانی: ' + err.message);
    }
  }
};
