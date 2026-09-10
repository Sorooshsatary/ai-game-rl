/**
 * Main application coordinator and tab router
 */
document.addEventListener('DOMContentLoaded', async () => {
  // Tab switcher
  window.switchTab = function(tabId) {
    // If attempting to switch to Part 2 while locked for the current user
    if (tabId === 'comparison' && typeof ComparisonUI !== 'undefined' && ComparisonUI.isLockedForCurrentUser && ComparisonUI.isLockedForCurrentUser()) {
      const modal = document.getElementById('modal-part2-locked');
      if (modal) {
        modal.classList.add('active');
      } else {
        alert('🔒 بخش دوم در حال حاضر توسط مدرس یا مدیر قفل شده است. لطفاً ابتدا در بخش ۱ استراتژی شاه‌دزد خود را طراحی و ارزیابی کنید.');
      }
      return;
    }

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
