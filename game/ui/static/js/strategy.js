/**
 * Enhanced Block-based If-Then Strategy Builder
 * Supports compound AND conditions, distance thresholds, smart actions, and rule reordering.
 */
const StrategyUI = {
  presets: [],
  cachedConfig: null,
  conditions: [
    { id: "enemy_adjacent", name: "⚠️ پلیس در خانه مجاور است (خطر فوری)", hasDistance: false },
    { id: "enemy_dist_le", name: "🚨 فاصله تا پلیس کمتر یا مساوی", hasDistance: true, defaultDist: 2 },
    { id: "one_life", name: "❤️ فقط ۱ جان باقی مانده (خطر دستگیری)", hasDistance: false },
    { id: "has_diamond", name: "🗝️ کلید گنج در کوله‌پشتی داری", hasDistance: false },
    { id: "diamond_exists", name: "💎 کلید گنج در نقشه وجود دارد", hasDistance: false },
    { id: "coin_exists", name: "🪙 سکه در نقشه وجود دارد", hasDistance: false },
    { id: "coins_cleared", name: "🏁 تمام سکه‌های نقشه جمع شده‌اند", hasDistance: false },
    { id: "always", name: "♾️ در هر شرایطی (همیشه)", hasDistance: false }
  ],
  actions: [
    { id: "flee_dodge", name: "🔀 جاخالی دادن و فرار از پلیس" },
    { id: "flee_towards_exit", name: "🚪 فرار از دست پلیس به سمت مسیر خروج" },
    { id: "go_nearest_coin", name: "🪙 حرکت به سمت نزدیک‌ترین سکه" },
    { id: "go_nearest_diamond", name: "🗝️ حرکت به سمت نزدیک‌ترین کلید گنج" },
    { id: "go_converter", name: "🏆 حرکت به سمت صندوق گنج برای باز کردن با کلید" },
    { id: "go_exit", name: "🏁 حرکت به سمت مسیر فرار و درِ خروج" },
    { id: "random_move", name: "🎲 حرکت تصادفی" }
  ],
  easyAnswers: {
    police: 'dodge',
    diamond: 'converter',
    goal: 'coins_first',
    emergency: 'exit_rush'
  },
  currentStrategy: {
    name: "استراتژی شاه‌دزد من",
    if_then_rules: [
      { conditions: [{ type: "enemy_adjacent", value: 1 }], action: "flee_dodge" },
      { conditions: [{ type: "has_diamond", value: 2 }], action: "go_converter" },
      { conditions: [{ type: "coin_exists", value: 2 }], action: "go_nearest_coin" }
    ],
    default_action: "random_move"
  },

  async init() {
    try {
      this.cachedConfig = await API.getConfig();
    } catch (e) {
      console.warn("Could not fetch initial config for StrategyUI:", e);
    }

    this.setupEasyQuestionnaire();

    try {
      this.presets = await API.getPresets();
      this.renderPresets();
      this.renderRulesList();
      await this.updatePresetVisibility();
      await this.applyDifficultyMode();

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
      await this.updatePresetVisibility();
      await this.applyDifficultyMode();
    }
  },

  async applyDifficultyMode() {
    try {
      if (!this.cachedConfig) {
        this.cachedConfig = await API.getConfig();
      }
    } catch (e) {
      // ignore
    }

    const isEasy = (this.cachedConfig && this.cachedConfig.difficulty === 'easy');
    const easyContainer = document.getElementById('strategy-easy-mode');
    const advancedContainer = document.getElementById('strategy-advanced-mode');
    const badge = document.getElementById('strategy-difficulty-badge');
    const title = document.getElementById('strategy-section-title');
    const subtitle = document.getElementById('strategy-section-subtitle');

    if (isEasy) {
      if (easyContainer) easyContainer.style.display = 'block';
      if (advancedContainer) advancedContainer.style.display = 'none';
      if (title) title.textContent = '🎯 تعیین استراتژی شاه‌دزد (حالت آسان)';
      if (subtitle) subtitle.textContent = 'پاسخ به سوالات جهت تنظیم خودکار هوش سارق';
      if (badge) {
        badge.style.display = 'inline-block';
        badge.textContent = '🎯 حالت آسان: پرسش و پاسخ';
        badge.style.background = '#dcfce7';
        badge.style.color = '#15803d';
        badge.style.border = '1px solid #bbf7d0';
      }
      this.compileEasyStrategy();
    } else {
      if (easyContainer) easyContainer.style.display = 'none';
      if (advancedContainer) advancedContainer.style.display = 'block';
      if (title) title.textContent = '💡 چیدمان شروط و فرامین شاه‌دزد';
      if (subtitle) subtitle.textContent = 'اولویت‌ها از بالا به پایین بررسی می‌شوند';
      if (badge) {
        badge.style.display = 'inline-block';
        badge.textContent = '🧩 حالت پیشرفته: بلوک‌های شرطی';
        badge.style.background = '#e0e7ff';
        badge.style.color = '#3730a3';
        badge.style.border = '1px solid #c7d2fe';
      }
      this.renderRulesList();
    }
  },

  setupEasyQuestionnaire() {
    const questions = ['easy_q_police', 'easy_q_diamond', 'easy_q_goal', 'easy_q_emergency'];
    const mapProp = {
      'easy_q_police': 'police',
      'easy_q_diamond': 'diamond',
      'easy_q_goal': 'goal',
      'easy_q_emergency': 'emergency'
    };

    questions.forEach(qName => {
      const inputs = document.querySelectorAll(`input[name="${qName}"]`);
      inputs.forEach(input => {
        input.addEventListener('change', () => {
          const prop = mapProp[qName];
          if (prop && input.checked) {
            this.easyAnswers[prop] = input.value;
            this.compileEasyStrategy();
          }
        });
      });
    });

    const btnResetEasy = document.getElementById('btn-reset-easy-questions');
    if (btnResetEasy) {
      btnResetEasy.addEventListener('click', () => {
        this.easyAnswers = {
          police: 'dodge',
          diamond: 'converter',
          goal: 'coins_first',
          emergency: 'exit_rush'
        };
        // Reset radio buttons in UI
        document.querySelectorAll('input[name="easy_q_police"]').forEach(r => { r.checked = (r.value === 'dodge'); });
        document.querySelectorAll('input[name="easy_q_diamond"]').forEach(r => { r.checked = (r.value === 'converter'); });
        document.querySelectorAll('input[name="easy_q_goal"]').forEach(r => { r.checked = (r.value === 'coins_first'); });
        document.querySelectorAll('input[name="easy_q_emergency"]').forEach(r => { r.checked = (r.value === 'exit_rush'); });
        this.compileEasyStrategy();
      });
    }
  },

  compileEasyStrategy() {
    const ans = this.easyAnswers;
    const rules = [];
    const summaryBullets = [];

    // 1. Police rule
    if (ans.police === 'dodge') {
      rules.push({ conditions: [{ type: 'enemy_adjacent', value: 1 }], action: 'flee_dodge' });
      summaryBullets.push('🚨 <strong>در مواجهه با پلیس:</strong> جاخالی دادن تاکتیکی و چرخش زاویه برای خروج از دید');
    } else if (ans.police === 'flee') {
      rules.push({ conditions: [{ type: 'enemy_adjacent', value: 1 }], action: 'flee_enemy' });
      summaryBullets.push('🏃‍♂️ <strong>در مواجهه با پلیس:</strong> فرار مستقیم و افزایش حداکثری فاصله');
    } else if (ans.police === 'exit') {
      rules.push({ conditions: [{ type: 'enemy_dist_le', value: 2 }], action: 'flee_towards_exit' });
      summaryBullets.push('🚪 <strong>در مواجهه با پلیس:</strong> فرار فوری به سمت درِ خروج نقشه');
    } else if (ans.police === 'collect') {
      rules.push({ conditions: [{ type: 'enemy_adjacent', value: 1 }], action: 'flee_collect' });
      summaryBullets.push('🪙 <strong>در مواجهه با پلیس:</strong> فرار همراه با سرقت فرصت‌طلبانه سکه‌ها');
    }

    // 2. Emergency 1-life rule
    if (ans.emergency === 'exit_rush') {
      rules.push({ conditions: [{ type: 'one_life', value: 1 }], action: 'go_exit' });
      summaryBullets.push('❤️ <strong>هنگام ۱ جان باقی‌مانده:</strong> فرار نجات‌بخش و حرکت فوری به سمت درِ خروج');
    } else {
      summaryBullets.push('⚡ <strong>هنگام ۱ جان باقی‌مانده:</strong> شجاعت تا آخرین نفس و ادامه جمع‌آوری سکه‌ها');
    }

    // 3. Diamond handling rule
    if (ans.diamond === 'converter') {
      rules.push({ conditions: [{ type: 'has_diamond', value: 1 }], action: 'go_converter' });
      summaryBullets.push('🏆 <strong>هنگام حمل کلید گنج:</strong> باز کردن فوری صندوق گنج و دریافت سکه‌های ۲ برابری');
    } else {
      rules.push({ conditions: [{ type: 'has_diamond', value: 1 }], action: 'go_exit' });
      summaryBullets.push('🚪 <strong>هنگام حمل کلید گنج:</strong> خروج مستقیم از نقشه جهت حفظ کلید گران‌بها');
    }

    // 4. Roaming goal rule
    if (ans.goal === 'diamonds_first') {
      rules.push({ conditions: [{ type: 'diamond_exists', value: 1 }], action: 'go_nearest_diamond' });
      rules.push({ conditions: [{ type: 'coin_exists', value: 1 }], action: 'go_nearest_coin' });
      summaryBullets.push('💎 <strong>اولویت در گشت عادی:</strong> ابتدا جستجوی الماس و کلیدها، سپس سکه‌ها');
    } else {
      rules.push({ conditions: [{ type: 'coin_exists', value: 1 }], action: 'go_nearest_coin' });
      rules.push({ conditions: [{ type: 'diamond_exists', value: 1 }], action: 'go_nearest_diamond' });
      summaryBullets.push('🪙 <strong>اولویت در گشت عادی:</strong> ابتدا جمع‌آوری تمام سکه‌های نقشه، سپس الماس‌ها');
    }

    this.currentStrategy.name = 'شاه‌دزد هوشمند (حالت آسان)';
    this.currentStrategy.if_then_rules = rules;

    const summaryContainer = document.getElementById('easy-rules-summary-list');
    if (summaryContainer) {
      summaryContainer.innerHTML = summaryBullets
        .map((b, i) => `<div style="margin-bottom: 5px;">${i + 1}. ${b}</div>`)
        .join('') +
        `<div style="margin-top: 8px; font-size: 0.8rem; color: #4338ca; font-weight: 700;">✅ این قوانین به صورت زنده برای شاه‌دزد فعال شدند و با زدن دکمه «اجرای استراتژی» یا «نبرد هوش مصنوعی» روی نقشه شبیه‌سازی می‌شوند.</div>`;
    }
  },

  async updatePresetVisibility() {
    const wrapper = document.getElementById('presets-wrapper');
    const badge = document.getElementById('preset-admin-badge');
    if (!wrapper) return;

    try {
      if (!this.cachedConfig) {
        this.cachedConfig = await API.getConfig();
      }
    } catch (e) {
      // ignore
    }

    const isFlagEnabled = !!(this.cachedConfig && this.cachedConfig.show_presets);
    const user = (typeof AuthUI !== 'undefined' && AuthUI.currentUser) ? AuthUI.currentUser : null;
    const isAdmin = user && user.role === 'admin';

    if (isAdmin) {
      wrapper.style.display = 'block';
      if (badge) {
        badge.style.display = 'inline-block';
        if (isFlagEnabled) {
          badge.textContent = '👑 فلگ ادمین: روشن برای کاربران عادی';
          badge.style.background = '#dcfce7';
          badge.style.color = '#15803d';
        } else {
          badge.textContent = '👑 پیش‌نمایش مدیر (برای کاربر عادی خاموش است)';
          badge.style.background = '#fef3c7';
          badge.style.color = '#92400e';
        }
      }
    } else if (isFlagEnabled) {
      wrapper.style.display = 'block';
      if (badge) badge.style.display = 'none';
    } else {
      wrapper.style.display = 'none';
    }
  },

  normalizeRule(rawRule) {
    let conditions = [];
    if (rawRule.conditions && Array.isArray(rawRule.conditions) && rawRule.conditions.length > 0) {
      conditions = rawRule.conditions.map(c => {
        if (typeof c === 'string') {
          return this.normalizeConditionString(c);
        }
        return {
          type: c.type || 'always',
          value: Number(c.value !== undefined ? c.value : 2)
        };
      });
    } else if (rawRule.condition) {
      conditions = [this.normalizeConditionString(rawRule.condition)];
    } else {
      conditions = [{ type: 'always', value: 2 }];
    }

    return {
      conditions: conditions,
      action: rawRule.action || 'random_move'
    };
  },

  normalizeConditionString(condStr) {
    if (condStr === 'enemy_near') return { type: 'enemy_dist_le', value: 2 };
    if (condStr === 'enemy_adjacent') return { type: 'enemy_dist_le', value: 1 };
    return { type: condStr, value: 2 };
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
      this.currentStrategy.if_then_rules = preset.if_then_rules.map(r => this.normalizeRule(r));
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
      container.innerHTML = '<div style="color: #64748b; font-size: 0.9rem; padding: 18px; text-align: center; background: #f8fafc; border-radius: 12px; border: 1px dashed #cbd5e1;">هیچ قانونی تعریف نشده است! دکمه «➕ افزودن شرط جدید» را بزنید.</div>';
      return;
    }

    rules.forEach((rule, rIdx) => {
      const card = document.createElement('div');
      card.className = 'rule-card';

      // --- Top Toolbar ---
      const toolbar = document.createElement('div');
      toolbar.className = 'rule-card-toolbar';

      const leftTools = document.createElement('div');
      leftTools.className = 'rule-toolbar-left';

      const badge = document.createElement('span');
      badge.className = 'rule-num-badge';
      badge.textContent = `اولویت ${rIdx + 1}`;
      leftTools.appendChild(badge);

      // Reorder buttons (Move Up / Down)
      const btnUp = document.createElement('button');
      btnUp.type = 'button';
      btnUp.className = 'btn-reorder';
      btnUp.innerHTML = '⬆️';
      btnUp.title = 'افزایش اولویت (انتقال به بالا)';
      btnUp.disabled = (rIdx === 0);
      btnUp.addEventListener('click', () => this.moveUp(rIdx));
      leftTools.appendChild(btnUp);

      const btnDown = document.createElement('button');
      btnDown.type = 'button';
      btnDown.className = 'btn-reorder';
      btnDown.innerHTML = '⬇️';
      btnDown.title = 'کاهش اولویت (انتقال به پایین)';
      btnDown.disabled = (rIdx === rules.length - 1);
      btnDown.addEventListener('click', () => this.moveDown(rIdx));
      leftTools.appendChild(btnDown);

      toolbar.appendChild(leftTools);

      const rightTools = document.createElement('div');
      rightTools.className = 'rule-toolbar-right';

      // Add "AND" sub-condition button
      const btnAddAnd = document.createElement('button');
      btnAddAnd.type = 'button';
      btnAddAnd.className = 'btn-add-subcond';
      btnAddAnd.innerHTML = '➕ و (AND)';
      btnAddAnd.title = 'افزودن شرط تکمیلی همزمان با این قانون';
      btnAddAnd.addEventListener('click', () => this.addSubCondition(rIdx));
      rightTools.appendChild(btnAddAnd);

      // Delete Rule button
      const btnDel = document.createElement('button');
      btnDel.type = 'button';
      btnDel.className = 'btn-del-rule';
      btnDel.innerHTML = '❌ حذف';
      btnDel.title = 'حذف کل این قانون';
      btnDel.addEventListener('click', () => this.deleteRule(rIdx));
      rightTools.appendChild(btnDel);

      toolbar.appendChild(rightTools);
      card.appendChild(toolbar);

      // --- Rule Body ---
      const body = document.createElement('div');
      body.className = 'rule-card-body';

      // Left: Conditions list
      const condsCol = document.createElement('div');
      condsCol.className = 'rule-conditions-col';

      rule.conditions.forEach((cond, cIdx) => {
        const condRow = document.createElement('div');
        condRow.className = 'rule-cond-item';

        // Prefix: "اگر" or "و"
        const prefix = document.createElement('span');
        prefix.className = `rule-cond-prefix ${cIdx > 0 ? 'and-prefix' : ''}`;
        prefix.textContent = cIdx === 0 ? 'اگر' : 'و';
        condRow.appendChild(prefix);

        // Condition Select
        const condSelect = document.createElement('select');
        condSelect.className = 'rule-cond-select';
        this.conditions.forEach(c => {
          const opt = document.createElement('option');
          opt.value = c.id;
          opt.textContent = c.name;
          if (c.id === cond.type) opt.selected = true;
          condSelect.appendChild(opt);
        });

        // Distance wrapper
        const distWrap = document.createElement('div');
        distWrap.className = 'rule-dist-wrap';
        const distInput = document.createElement('input');
        distInput.type = 'number';
        distInput.min = '1';
        distInput.max = '15';
        distInput.value = cond.value || 2;
        distInput.className = 'rule-dist-input';

        const distLabel = document.createElement('span');
        distLabel.className = 'rule-dist-label';
        distLabel.textContent = 'خانه';

        distWrap.appendChild(distInput);
        distWrap.appendChild(distLabel);

        const condDef = this.conditions.find(c => c.id === cond.type);
        distWrap.style.display = (condDef && condDef.hasDistance) ? 'inline-flex' : 'none';

        condSelect.addEventListener('change', (e) => {
          cond.type = e.target.value;
          const updatedDef = this.conditions.find(c => c.id === cond.type);
          if (updatedDef && updatedDef.hasDistance) {
            distWrap.style.display = 'inline-flex';
            if (!cond.value) cond.value = updatedDef.defaultDist;
            distInput.value = cond.value;
          } else {
            distWrap.style.display = 'none';
          }
        });

        distInput.addEventListener('change', (e) => {
          cond.value = Math.max(1, parseInt(e.target.value, 10) || 1);
        });

        condRow.appendChild(condSelect);
        condRow.appendChild(distWrap);

        // If multiple conditions exist in this rule, show a small delete button for this condition
        if (rule.conditions.length > 1) {
          const btnDelSub = document.createElement('button');
          btnDelSub.type = 'button';
          btnDelSub.className = 'btn-del-subcond-icon';
          btnDelSub.innerHTML = '×';
          btnDelSub.title = 'حذف این شرط جزئی';
          btnDelSub.addEventListener('click', () => this.deleteSubCondition(rIdx, cIdx));
          condRow.appendChild(btnDelSub);
        }

        condsCol.appendChild(condRow);
      });

      body.appendChild(condsCol);

      // Right: Arrow & Action
      const actionCol = document.createElement('div');
      actionCol.className = 'rule-action-col';

      const arrow = document.createElement('span');
      arrow.className = 'rule-arrow-symbol';
      arrow.textContent = '➔ آنگاه';
      actionCol.appendChild(arrow);

      const actSelect = document.createElement('select');
      actSelect.className = 'rule-action-select';
      this.actions.forEach(a => {
        const opt = document.createElement('option');
        opt.value = a.id;
        opt.textContent = a.name;
        if (a.id === rule.action) opt.selected = true;
        actSelect.appendChild(opt);
      });
      actSelect.addEventListener('change', (e) => {
        rule.action = e.target.value;
      });
      actionCol.appendChild(actSelect);

      body.appendChild(actionCol);
      card.appendChild(body);
      container.appendChild(card);
    });
  },

  moveUp(idx) {
    if (idx <= 0) return;
    const rules = this.currentStrategy.if_then_rules;
    const temp = rules[idx];
    rules[idx] = rules[idx - 1];
    rules[idx - 1] = temp;
    this.renderRulesList();
  },

  moveDown(idx) {
    const rules = this.currentStrategy.if_then_rules;
    if (idx >= rules.length - 1) return;
    const temp = rules[idx];
    rules[idx] = rules[idx + 1];
    rules[idx + 1] = temp;
    this.renderRulesList();
  },

  addRule() {
    this.currentStrategy.if_then_rules.push({
      conditions: [{ type: "coin_dist_le", value: 3 }],
      action: "go_nearest_coin"
    });
    this.renderRulesList();
    // Scroll to bottom
    const container = document.getElementById('rules-list-container');
    if (container) container.scrollTop = container.scrollHeight;
  },

  deleteRule(idx) {
    this.currentStrategy.if_then_rules.splice(idx, 1);
    this.renderRulesList();
  },

  addSubCondition(ruleIdx) {
    const rule = this.currentStrategy.if_then_rules[ruleIdx];
    if (!rule) return;
    rule.conditions.push({
      type: "enemy_dist_gt",
      value: 2
    });
    this.renderRulesList();
  },

  deleteSubCondition(ruleIdx, condIdx) {
    const rule = this.currentStrategy.if_then_rules[ruleIdx];
    if (!rule) return;
    rule.conditions.splice(condIdx, 1);
    if (rule.conditions.length === 0) {
      rule.conditions.push({ type: "always", value: 2 });
    }
    this.renderRulesList();
  },

  getStrategy() {
    const cleanRules = this.currentStrategy.if_then_rules.map(r => {
      const conds = (r.conditions && r.conditions.length > 0)
        ? r.conditions
        : [{ type: "always", value: 2 }];
      return {
        condition: conds[0].type,
        conditions: conds.map(c => ({ type: c.type, value: Number(c.value) || 2 })),
        action: r.action || "random_move"
      };
    });

    return {
      ...this.currentStrategy,
      if_then_rules: cleanRules
    };
  }
};

