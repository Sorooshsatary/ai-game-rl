/**
 * Canvas Renderer for single agent and multi-agent arena
 */
class GridCanvasRenderer {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement.getContext('2d');
  }

  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  drawGrid(width, height) {
    const cellSize = this.canvas.width / width;
    this.ctx.save();

    for (let r = 0; r < height; r++) {
      for (let c = 0; c < width; c++) {
        // Checkerboard light pattern
        this.ctx.fillStyle = (r + c) % 2 === 0 ? '#f8fafc' : '#f1f5f9';
        this.ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);

        // Soft border
        this.ctx.strokeStyle = '#e2e8f0';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(c * cellSize, r * cellSize, cellSize, cellSize);
      }
    }
    this.ctx.restore();
  }

  drawItem(x, y, emoji, cellSize, glowColor = null) {
    const cx = x * cellSize + cellSize / 2;
    const cy = y * cellSize + cellSize / 2;

    this.ctx.save();
    if (glowColor) {
      this.ctx.shadowColor = glowColor;
      this.ctx.shadowBlur = 12;
    }
    this.ctx.font = `${Math.floor(cellSize * 0.65)}px "Segoe UI Emoji", sans-serif`;
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText(emoji, cx, cy);
    this.ctx.restore();
  }

  renderSingleAgentFrame(mapConfig, stateSnapshot) {
    const width = mapConfig.width || 8;
    const height = mapConfig.height || 8;
    const cellSize = this.canvas.width / width;

    this.clear();
    this.drawGrid(width, height);

    // 1. Converter
    if (mapConfig.converter) {
      const [cx, cy] = mapConfig.converter;
      this.ctx.fillStyle = '#f3e8ff';
      this.ctx.fillRect(cx * cellSize, cy * cellSize, cellSize, cellSize);
      this.drawItem(cx, cy, '🏪', cellSize, '#a855f7');
    }

    // 2. Exit
    if (mapConfig.exit) {
      const [ex, ey] = mapConfig.exit;
      this.ctx.fillStyle = '#dcfce7';
      this.ctx.fillRect(ex * cellSize, ey * cellSize, cellSize, cellSize);
      this.drawItem(ex, ey, '🚪', cellSize, '#22c55e');
    }

    // 3. Coins remaining
    // If stateSnapshot has nearest coin or items left, we can draw from remaining or active list
    if (stateSnapshot.coins) {
      for (const [cx, cy] of stateSnapshot.coins) {
        this.drawItem(cx, cy, '🪙', cellSize, '#fbbf24');
      }
    } else if (mapConfig.coins) {
      // Fallback
      for (const [cx, cy] of mapConfig.coins) {
        this.drawItem(cx, cy, '🪙', cellSize, '#fbbf24');
      }
    }

    // 4. Diamonds remaining
    if (stateSnapshot.diamonds) {
      for (const [dx, dy] of stateSnapshot.diamonds) {
        this.drawItem(dx, dy, '💎', cellSize, '#38bdf8');
      }
    } else if (mapConfig.diamonds) {
      for (const [dx, dy] of mapConfig.diamonds) {
        this.drawItem(dx, dy, '💎', cellSize, '#38bdf8');
      }
    }

    // 5. Enemy
    if (stateSnapshot.enemy_pos) {
      const [ex, ey] = stateSnapshot.enemy_pos;
      this.drawItem(ex, ey, '👾', cellSize, '#ef4444');
    }

    // 6. Agent
    if (stateSnapshot.agent_pos) {
      const [ax, ay] = stateSnapshot.agent_pos;
      // Draw colored halo under agent
      const cx = ax * cellSize + cellSize / 2;
      const cy = ay * cellSize + cellSize / 2;
      this.ctx.save();
      this.ctx.beginPath();
      this.ctx.arc(cx, cy, cellSize * 0.42, 0, 2 * Math.PI);
      this.ctx.fillStyle = 'rgba(79, 70, 229, 0.2)';
      this.ctx.fill();
      this.ctx.lineWidth = 3;
      this.ctx.strokeStyle = '#4f46e5';
      this.ctx.stroke();
      this.ctx.restore();

      this.drawItem(ax, ay, '🤖', cellSize, '#4f46e5');
    }
  }

  renderArenaFrame(mapConfig, frame) {
    const width = mapConfig.width || 10;
    const height = mapConfig.height || 10;
    const cellSize = this.canvas.width / width;

    this.clear();
    this.drawGrid(width, height);

    // Converter
    if (mapConfig.converter) {
      const [cx, cy] = mapConfig.converter;
      this.ctx.fillStyle = '#f3e8ff';
      this.ctx.fillRect(cx * cellSize, cy * cellSize, cellSize, cellSize);
      this.drawItem(cx, cy, '🏪', cellSize, '#a855f7');
    }

    // Exit
    if (mapConfig.exit) {
      const [ex, ey] = mapConfig.exit;
      this.ctx.fillStyle = '#dcfce7';
      this.ctx.fillRect(ex * cellSize, ey * cellSize, cellSize, cellSize);
      this.drawItem(ex, ey, '🚪', cellSize, '#22c55e');
    }

    // Coins
    if (frame.coins) {
      for (const [cx, cy] of frame.coins) {
        this.drawItem(cx, cy, '🪙', cellSize, '#fbbf24');
      }
    }

    // Diamonds
    if (frame.diamonds) {
      for (const [dx, dy] of frame.diamonds) {
        this.drawItem(dx, dy, '💎', cellSize, '#38bdf8');
      }
    }

    // Enemy
    if (frame.enemy) {
      this.drawItem(frame.enemy.x, frame.enemy.y, '👾', cellSize, '#ef4444');
    }

    // Agents
    if (frame.agents) {
      for (const ag of frame.agents) {
        if (!ag.is_alive && !ag.has_exited) {
          // Dead marker
          this.drawItem(ag.x, ag.y, '💀', cellSize);
          continue;
        }
        if (ag.has_exited) {
          // Escaped marker
          continue;
        }

        const cx = ag.x * cellSize + cellSize / 2;
        const cy = ag.y * cellSize + cellSize / 2;

        this.ctx.save();
        this.ctx.beginPath();
        this.ctx.arc(cx, cy, cellSize * 0.42, 0, 2 * Math.PI);
        this.ctx.fillStyle = ag.color || '#4f46e5';
        this.ctx.fill();
        this.ctx.strokeStyle = '#ffffff';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();

        // Agent initials or robot
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = `bold ${Math.floor(cellSize * 0.45)}px sans-serif`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        const initial = ag.name ? ag.name.charAt(0) : 'A';
        this.ctx.fillText(initial, cx, cy);
        this.ctx.restore();
      }
    }
  }
}
