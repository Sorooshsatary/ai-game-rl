/**
 * Main application coordinator and tab router
 */
document.addEventListener('DOMContentLoaded', async () => {
  // Tab switcher
  window.switchTab = function(tabId) {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tabId);
    });

    tabContents.forEach(content => {
      content.classList.toggle('active', content.id === `tab-${tabId}`);
    });

    // If switching to admin tab, reload admin data
    if (tabId === 'admin' && typeof AdminUI !== 'undefined' && AdminUI.loadData) {
      AdminUI.loadData();
    }
  };

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      window.switchTab(btn.dataset.tab);
    });
  });

  // Initialize UI components
  await StrategyUI.init();
  TrainingUI.init();
  await ComparisonUI.init();

  if (typeof AdminUI !== 'undefined' && AdminUI.init) {
    AdminUI.init();
  }

  if (typeof AuthUI !== 'undefined' && AuthUI.init) {
    await AuthUI.init();
  }

  if (typeof ReplayUI !== 'undefined' && ReplayUI.init) {
    ReplayUI.init();
  }
  if (typeof ArenaUI !== 'undefined' && ArenaUI.init) {
    ArenaUI.init();
  }
});
