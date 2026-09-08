/**
 * Main application coordinator and tab router
 */
document.addEventListener('DOMContentLoaded', async () => {
  // Tab switcher
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  window.switchTab = function(tabId) {
    tabBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tabId);
    });

    tabContents.forEach(content => {
      content.classList.toggle('active', content.id === `tab-${tabId}`);
    });
  };

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      window.switchTab(btn.dataset.tab);
    });
  });

  // Initialize UI components
  await StrategyUI.init();
  TrainingUI.init();
  ReplayUI.init();
  ArenaUI.init();
});
