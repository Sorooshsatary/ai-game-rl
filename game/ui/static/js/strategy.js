/**
 * Strategy Builder UI Manager
 */
const StrategyUI = {
  presets: [],
  currentStrategy: {
    name: "استراتژی من",
    coin_priority: 7.0,
    diamond_priority: 6.0,
    converter_urgency: 8.0,
    enemy_fear: 8.0,
    exit_eagerness: 6.0,
    rules: {
      flee_adjacent_enemy: true,
      deposit_before_coins: true,
      diamond_only_if_safe: true,
      exit_if_one_life: true,
      exit_if_coins_cleared: true
    }
  },

  async init() {
    try {
      this.presets = await API.getPresets();
      this.renderPresets();
      this.bindInputs();
    } catch (err) {
      console.error("Failed to load presets:", err);
    }
  },

  renderPresets() {
    const container = document.getElementById('preset-chips');
    if (!container) return;
    container.innerHTML = '';

    this.presets.forEach(p => {
      const chip = document.createElement('button');
      chip.className = `preset-chip ${p.id === 'balanced' ? 'active' : ''}`;
      chip.textContent = p.name;
      chip.addEventListener('click', () => {
        document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        this.loadStrategy(p);
      });
      container.appendChild(chip);
    });
  },

  loadStrategy(strategyData) {
    this.currentStrategy = JSON.parse(JSON.stringify(strategyData));

    // Update sliders
    ['coin_priority', 'diamond_priority', 'converter_urgency', 'enemy_fear', 'exit_eagerness'].forEach(key => {
      const slider = document.getElementById(`slider-${key}`);
      const valDisplay = document.getElementById(`val-${key}`);
      if (slider && valDisplay) {
        slider.value = this.currentStrategy[key];
        valDisplay.textContent = this.currentStrategy[key];
      }
    });

    // Update rules checkboxes
    if (this.currentStrategy.rules) {
      Object.keys(this.currentStrategy.rules).forEach(ruleKey => {
        const checkbox = document.getElementById(`rule-${ruleKey}`);
        if (checkbox) {
          checkbox.checked = this.currentStrategy.rules[ruleKey];
        }
      });
    }
  },

  bindInputs() {
    ['coin_priority', 'diamond_priority', 'converter_urgency', 'enemy_fear', 'exit_eagerness'].forEach(key => {
      const slider = document.getElementById(`slider-${key}`);
      const valDisplay = document.getElementById(`val-${key}`);
      if (slider && valDisplay) {
        slider.addEventListener('input', (e) => {
          const val = parseFloat(e.target.value);
          valDisplay.textContent = val;
          this.currentStrategy[key] = val;
        });
      }
    });

    ['flee_adjacent_enemy', 'deposit_before_coins', 'diamond_only_if_safe', 'exit_if_one_life', 'exit_if_coins_cleared'].forEach(ruleKey => {
      const checkbox = document.getElementById(`rule-${ruleKey}`);
      if (checkbox) {
        checkbox.addEventListener('change', (e) => {
          if (!this.currentStrategy.rules) this.currentStrategy.rules = {};
          this.currentStrategy.rules[ruleKey] = e.target.checked;
        });
      }
    });
  },

  getStrategy() {
    return this.currentStrategy;
  }
};
