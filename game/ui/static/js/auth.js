/**
 * Authentication UI Controller
 */
const AuthUI = {
  currentUser: null,

  async init() {
    this.bindEvents();
    await this.checkAuthStatus();
  },

  bindEvents() {
    const btnOpenLogin = document.getElementById('btn-open-login');
    if (btnOpenLogin) {
      btnOpenLogin.addEventListener('click', () => this.openLoginModal());
    }

    const btnCloseLogin = document.getElementById('btn-close-login');
    if (btnCloseLogin) {
      btnCloseLogin.addEventListener('click', () => this.closeLoginModal());
    }

    const modalOverlay = document.getElementById('modal-login');
    if (modalOverlay) {
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) this.closeLoginModal();
      });
    }

    const formLogin = document.getElementById('form-login');
    if (formLogin) {
      formLogin.addEventListener('submit', (e) => {
        e.preventDefault();
        this.submitLogin();
      });
    }

    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
      btnLogout.addEventListener('click', () => this.logout());
    }
  },

  async checkAuthStatus() {
    try {
      const data = await API.getMe();
      if (data.authenticated && data.user) {
        this.currentUser = data.user;
      } else {
        this.currentUser = null;
      }
    } catch {
      this.currentUser = null;
    }
    this.renderUserHeader();
  },

  renderUserHeader() {
    const userBadge = document.getElementById('user-badge');
    const btnOpenLogin = document.getElementById('btn-open-login');
    const btnLogout = document.getElementById('btn-logout');
    const tabAdminBtn = document.getElementById('tab-btn-admin');

    if (this.currentUser) {
      const roleFa = this.currentUser.role === 'admin' ? 'مدیر سیستم' : 'دانش‌آموز';
      const roleColor = this.currentUser.role === 'admin' ? '#f59e0b' : '#38bdf8';
      if (userBadge) {
        userBadge.style.display = 'inline-flex';
        userBadge.innerHTML = `
          <span>👤 ${this.currentUser.username}</span>
          <span style="background: ${roleColor}; color: #000; font-size: 0.72rem; padding: 2px 8px; border-radius: 12px; font-weight: 800;">${roleFa}</span>
        `;
      }
      if (btnOpenLogin) btnOpenLogin.style.display = 'none';
      if (btnLogout) btnLogout.style.display = 'inline-block';

      // Show Admin Tab only for admin role
      if (tabAdminBtn) {
        if (this.currentUser.role === 'admin') {
          tabAdminBtn.style.display = 'inline-flex';
          if (typeof AdminUI !== 'undefined' && AdminUI.loadData) {
            AdminUI.loadData();
          }
        } else {
          tabAdminBtn.style.display = 'none';
        }
      }
    } else {
      if (userBadge) {
        userBadge.style.display = 'none';
      }
      if (btnOpenLogin) btnOpenLogin.style.display = 'inline-block';
      if (btnLogout) btnLogout.style.display = 'none';
      if (tabAdminBtn) tabAdminBtn.style.display = 'none';
    }

    // Refresh preset visibility based on current user role and admin flag
    if (typeof StrategyUI !== 'undefined' && StrategyUI.updatePresetVisibility) {
      StrategyUI.updatePresetVisibility();
    }
  },

  openLoginModal() {
    const modal = document.getElementById('modal-login');
    const errBox = document.getElementById('login-error-msg');
    if (errBox) errBox.style.display = 'none';
    if (modal) modal.classList.add('active');
    const userInput = document.getElementById('login-username');
    if (userInput) userInput.focus();
  },

  closeLoginModal() {
    const modal = document.getElementById('modal-login');
    if (modal) modal.classList.remove('active');
  },

  normalizeDigits(str) {
    if (!str) return '';
    const fa = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    const ar = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
    let res = str;
    for (let i = 0; i < 10; i++) {
      res = res.replaceAll(fa[i], i.toString()).replaceAll(ar[i], i.toString());
    }
    return res.trim();
  },

  async submitLogin() {
    const userInput = document.getElementById('login-username');
    const passInput = document.getElementById('login-password');
    const errBox = document.getElementById('login-error-msg');
    const submitBtn = document.getElementById('btn-submit-login');

    if (!userInput || !passInput) return;
    const username = this.normalizeDigits(userInput.value);
    const password = this.normalizeDigits(passInput.value);

    if (!username || !password) {
      if (errBox) {
        errBox.textContent = 'لطفاً نام کاربری و رمز عبور را وارد کنید.';
        errBox.style.display = 'block';
      }
      return;
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = '⏳ در حال بررسی...';
    }

    try {
      const res = await API.login(username, password);
      this.currentUser = res.user;
      this.renderUserHeader();
      this.closeLoginModal();
      userInput.value = '';
      passInput.value = '';
      if (this.currentUser.role === 'admin' && typeof switchTab === 'function') {
        switchTab('admin');
      }
    } catch (err) {
      if (errBox) {
        errBox.textContent = err.message || 'خطا در ورود به حساب کاربری';
        errBox.style.display = 'block';
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'ورود به حساب کاربری';
      }
    }
  },

  async logout() {
    await API.logout();
    this.currentUser = null;
    this.renderUserHeader();
    if (typeof switchTab === 'function') {
      switchTab('strategy');
    }
  }
};
