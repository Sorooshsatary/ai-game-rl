/**
 * If-Then Block Strategy Builder Manager
 */
const StrategyUI = {
  presets: [],
  conditions: [
    { id: "coin_exists", name: "اگر سکه نزدیک یا در دسترس است" },
    { id: "enemy_near", name: "اگر دشمن داشت به سمتت می‌آمد (فاصله ۲ یا کمتر)" },
    { id: "enemy_adjacent", name: "اگر هیولا در خانه کناری چسبیده است" },
    { id: "has_diamond", name: "اگر الماس در کوله‌پشتی داری" },
    { id: "diamond_exists", name: "اگر الماس در نقشه وجود دارد" },
    { id: "one_life", name: "اگر فقط ۱ جان برایت باقی مانده" },
    { id: "coins_cleared", name: "اگر تمام سکه‌های نقشه جمع شده‌اند" },
    { id: "always", name: "در هر وضعیتی (همیشه)" }
  ],
  actions: [
    { id: "go_nearest_coin", name: "به سمت سکه برو" },
    { id: "flee_enemy", name: "از دست هیولا فرار کن" },
    { id: "go_converter", name: "به سمت تبدیل‌کننده برو" },
    { id: "go_exit", name: "به سمت در خروج برو" },
    { id: "go_nearest_diamond", name: "به سمت الماس برو" },
    { id: "random_move", name: "یک حرکت تصادفی بکن" }
  ],
  currentStrategy: {
    name: "استراتژی من",
    if_then_rules: [
      { condition: "enemy_near", action: "flee_enemy" },
      { condition: "has_diamond", action: "go_converter" },
      { condition: "one_life", action: "go_exit" },
      { condition: "coin_exists", action: "go_nearest_coin" },
      { condition: "diamond_exists", action: "go_nearest_diamond" },
      { condition: "coins_cleared", action: "go_exit" }
    ],
    default_action: "random_move"
  },

  async init() {
    try {
      this.presets = await API.getPresets();
      this.renderPresets();
      this.renderRulesList();

      const btnAdd = document.getElementById('btn-add-rule');
      if (btnAdd) {
        btnAdd.addEventListener('click', () => this.addRule());
      }

      const btnReset = document.getElementById('btn-reset-rules');
      if (btnReset) {
        btnReset.addEventListener('click', () => this.resetRules());
      }
    } catch (err) {
      console.error("Failed to load presets:", err);
      this.renderRulesList();
    }
  },

  renderPresets() {
    const container = document.getElementById('preset-chips');
    if (!container) return;
    container.innerHTML = '';

    this.presets.forEach((p, idx) => {
      const chip = document.createElement('button');
      chip.className = `preset-chip ${p.id === 'balanced' || idx === 0 ? 'active' : ''}`;
      chip.textContent = p.name;
      chip.addEventListener('click', () => {
        document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        this.loadPreset(p);
      });
      container.appendChild(chip);
    });
  },

  loadPreset(preset) {
    if (preset.if_then_rules && preset.if_then_rules.length > 0) {
      this.currentStrategy.if_then_rules = JSON.parse(JSON.stringify(preset.if_then_rules));
    }
    this.currentStrategy.name = preset.name;
    this.renderRulesList();
  },

  resetRules() {
    const balancedPreset = this.presets.find(p => p.id === 'balanced') || this.presets[0];
    if (balancedPreset) {
      this.loadPreset(balancedPreset);
      document.querySelectorAll('.preset-chip').forEach((c, idx) => {
        c.classList.toggle('active', idx === 0);
      });
    }
  },

  renderRulesList() {
    const container = document.getElementById('rules-list-container');
    if (!container) return;
    container.innerHTML = '';

    const rules = this.currentStrategy.if_then_rules;
    if (!rules || rules.length === 0) {
      container.innerHTML = '<div style="color: #64748b; font-size: 0.9rem; padding: 14px; text-align: center;">هیچ شرطی تعریف نشده است! دکمه «➕ افزودن شرط جدید» را بزنید.</div>';
      return;
    }

    rules.forEach((rule, idx) => {
      const row = document.createElement('div');
      row.className = 'rule-row';

      // Priority badge
      const badge = document.createElement('span');
      badge.className = 'rule-num';
      badge.textContent = `شرط ${idx + 1}`;
      row.appendChild(badge);

      // Label "اگر"
      const ifLabel = document.createElement('span');
      ifLabel.className = 'rule-label-text';
      ifLabel.textContent = 'اگر';
      row.appendChild(ifLabel);

      // Condition Select
      const condSelect = document.createElement('select');
      condSelect.className = 'rule-select';
      this.conditions.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = c.name.replace(/^اگر\s*/, '');
        if (c.id === rule.condition) opt.selected = true;
        condSelect.appendChild(opt);
      });
      condSelect.addEventListener('change', (e) => {
        this.currentStrategy.if_then_rules[idx].condition = e.target.value;
      });
      row.appendChild(condSelect);

      // Arrow "➔"
      const arrow = document.createElement('span');
      arrow.className = 'rule-arrow';
      arrow.textContent = '➔';
      row.appendChild(arrow);

      // Label "آنگاه"
      const thenLabel = document.createElement('span');
      thenLabel.className = 'rule-label-text';
      thenLabel.textContent = 'آنگاه';
      row.appendChild(thenLabel);

      // Action Select
      const actSelect = document.createElement('select');
      actSelect.className = 'rule-select';
      this.actions.forEach(a => {
        const opt = document.createElement('option');
        opt.value = a.id;
        opt.textContent = a.name;
        if (a.id === rule.action) opt.selected = true;
        actSelect.appendChild(opt);
      });
      actSelect.addEventListener('change', (e) => {
        this.currentStrategy.if_then_rules[idx].action = e.target.value;
      });
      row.appendChild(actSelect);

      // Delete Button
      const delBtn = document.createElement('button');
      delBtn.className = 'btn-del-rule';
      delBtn.title = 'حذف این شرط';
      delBtn.textContent = '❌';
      delBtn.addEventListener('click', () => {
        this.deleteRule(idx);
      });
      row.appendChild(delBtn);

      container.appendChild(row);
    });
  },

  addRule() {
    this.currentStrategy.if_then_rules.push({
      condition: "coin_exists",
      action: "go_nearest_coin"
    });
    this.renderRulesList();
  },

  deleteRule(idx) {
    this.currentStrategy.if_then_rules.splice(idx, 1);
    this.renderRulesList();
  },

  getStrategy() {
    return this.currentStrategy;
  }
};
