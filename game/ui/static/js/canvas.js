/**
 * High-Quality Vector Canvas Renderer for Educational RL Game
 * Beautiful custom graphics for Robot, Monster, Coins, Diamonds, Portals, and Walls.
 */
class GridCanvasRenderer {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement.getContext('2d');
    if (this.ctx) {
      this.ctx.direction = 'ltr';
    }
  }

  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  drawGrid(width, height) {
    const cellSize = this.canvas.width / width;
    this.ctx.save();

    for (let r = 0; r < height; r++) {
      for (let c = 0; c < width; c++) {
        const isAlt = (r + c) % 2 === 1;
        // High-tech cyber arena tiles
        const tileGrad = this.ctx.createLinearGradient(c * cellSize, r * cellSize, (c + 1) * cellSize, (r + 1) * cellSize);
        if (isAlt) {
          tileGrad.addColorStop(0, '#f8fafc');
          tileGrad.addColorStop(1, '#f1f5f9');
        } else {
          tileGrad.addColorStop(0, '#ffffff');
          tileGrad.addColorStop(1, '#f8fafc');
        }
        this.ctx.fillStyle = tileGrad;
        this.ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);

        // Subtle tile borders
        this.ctx.strokeStyle = '#e2e8f0';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(c * cellSize + 0.5, r * cellSize + 0.5, cellSize - 1, cellSize - 1);

        // Tech corner crosses (+)
        const crossX = c * cellSize;
        const crossY = r * cellSize;
        this.ctx.strokeStyle = '#cbd5e1';
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.moveTo(crossX - 2.5, crossY);
        this.ctx.lineTo(crossX + 2.5, crossY);
        this.ctx.moveTo(crossX, crossY - 2.5);
        this.ctx.lineTo(crossX, crossY + 2.5);
        this.ctx.stroke();

        // Subtle coordinate indicator in corner
        if (r === 0) {
          this.ctx.fillStyle = 'rgba(148, 163, 184, 0.45)';
          this.ctx.font = 'bold 8px monospace';
          this.ctx.textAlign = 'right';
          this.ctx.fillText(`${c + 1}`, (c + 1) * cellSize - 3, 10);
        }
        if (c === 0) {
          this.ctx.fillStyle = 'rgba(148, 163, 184, 0.45)';
          this.ctx.font = 'bold 8px monospace';
          this.ctx.textAlign = 'left';
          this.ctx.fillText(String.fromCharCode(65 + r), 3, (r + 1) * cellSize - 3);
        }
      }
    }

    // Outer frame with indigo cyber border
    this.ctx.strokeStyle = '#818cf8';
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(1, 1, this.canvas.width - 2, this.canvas.height - 2);

    // Corner tech brackets
    const bLen = 14;
    this.ctx.strokeStyle = '#4f46e5';
    this.ctx.lineWidth = 3;
    // Top-left
    this.ctx.beginPath();
    this.ctx.moveTo(1, bLen); this.ctx.lineTo(1, 1); this.ctx.lineTo(bLen, 1);
    // Top-right
    this.ctx.moveTo(this.canvas.width - bLen, 1); this.ctx.lineTo(this.canvas.width - 1, 1); this.ctx.lineTo(this.canvas.width - 1, bLen);
    // Bottom-left
    this.ctx.moveTo(1, this.canvas.height - bLen); this.ctx.lineTo(1, this.canvas.height - 1); this.ctx.lineTo(bLen, this.canvas.height - 1);
    // Bottom-right
    this.ctx.moveTo(this.canvas.width - bLen, this.canvas.height - 1); this.ctx.lineTo(this.canvas.width - 1, this.canvas.height - 1); this.ctx.lineTo(this.canvas.width - 1, this.canvas.height - bLen);
    this.ctx.stroke();

    this.ctx.restore();
  }

  drawWall(c, r, cellSize) {
    const x = c * cellSize;
    const y = r * cellSize;
    const p = 3;
    const w = cellSize - p * 2;
    const h = cellSize - p * 2;
    const rCorner = 6;

    this.ctx.save();
    // Drop shadow
    this.ctx.fillStyle = 'rgba(15, 23, 42, 0.12)';
    this.ctx.beginPath();
    this.ctx.roundRect(x + p + 2, y + p + 3, w, h, rCorner);
    this.ctx.fill();

    // Wall block 3D body gradient
    const grad = this.ctx.createLinearGradient(x + p, y + p, x + p, y + p + h);
    grad.addColorStop(0, '#475569');
    grad.addColorStop(0.5, '#334155');
    grad.addColorStop(1, '#1e293b');
    this.ctx.fillStyle = grad;
    this.ctx.beginPath();
    this.ctx.roundRect(x + p, y + p, w, h, rCorner);
    this.ctx.fill();

    // Top bevel highlight
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    this.ctx.lineWidth = 1.5;
    this.ctx.beginPath();
    this.ctx.roundRect(x + p + 1, y + p + 1, w - 2, h - 2, rCorner);
    this.ctx.stroke();

    // Corner rivets
    this.ctx.fillStyle = '#64748b';
    const dotR = 1.8;
    this.ctx.beginPath();
    this.ctx.arc(x + p + 6, y + p + 6, dotR, 0, Math.PI * 2);
    this.ctx.arc(x + p + w - 6, y + p + 6, dotR, 0, Math.PI * 2);
    this.ctx.arc(x + p + 6, y + p + h - 6, dotR, 0, Math.PI * 2);
    this.ctx.arc(x + p + w - 6, y + p + h - 6, dotR, 0, Math.PI * 2);
    this.ctx.fill();

    // Center seam
    this.ctx.strokeStyle = 'rgba(148, 163, 184, 0.35)';
    this.ctx.lineWidth = 1.5;
    this.ctx.beginPath();
    this.ctx.moveTo(x + p + w * 0.25, y + p + h * 0.5);
    this.ctx.lineTo(x + p + w * 0.75, y + p + h * 0.5);
    this.ctx.stroke();

    this.ctx.restore();
  }

  drawExit(x, y, cellSize) {
    const cx = x * cellSize + cellSize / 2;
    const cy = y * cellSize + cellSize / 2;
    const r = cellSize * 0.42;

    this.ctx.save();
    // Portal floor energy glow
    const glowGrad = this.ctx.createRadialGradient(cx, cy, r * 0.2, cx, cy, r * 1.2);
    glowGrad.addColorStop(0, 'rgba(16, 185, 129, 0.4)');
    glowGrad.addColorStop(1, 'rgba(16, 185, 129, 0.0)');
    this.ctx.fillStyle = glowGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r * 1.2, 0, Math.PI * 2);
    this.ctx.fill();

    // Base frame
    this.ctx.fillStyle = '#065f46';
    this.ctx.beginPath();
    this.ctx.roundRect(cx - r, cy - r, r * 2, r * 2, 8);
    this.ctx.fill();
    this.ctx.strokeStyle = '#34d399';
    this.ctx.lineWidth = 2;
    this.ctx.stroke();

    // Inner glowing vortex core
    const portalGrad = this.ctx.createRadialGradient(cx, cy, 2, cx, cy, r * 0.75);
    portalGrad.addColorStop(0, '#ecfdf5');
    portalGrad.addColorStop(0.5, '#10b981');
    portalGrad.addColorStop(1, '#047857');
    this.ctx.fillStyle = portalGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r * 0.72, 0, Math.PI * 2);
    this.ctx.fill();

    // Exit text label & icon
    this.ctx.fillStyle = '#ffffff';
    this.ctx.font = `bold ${Math.floor(cellSize * 0.28)}px sans-serif`;
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText('EXIT', cx, cy - 3);

    this.ctx.fillStyle = '#a7f3d0';
    this.ctx.font = `bold ${Math.floor(cellSize * 0.22)}px sans-serif`;
    this.ctx.fillText('🏁', cx, cy + 9);

    this.ctx.restore();
  }

  drawConverter(x, y, cellSize) {
    const cx = x * cellSize + cellSize / 2;
    const cy = y * cellSize + cellSize / 2;
    const r = cellSize * 0.42;

    this.ctx.save();
    // Violet glow
    const glowGrad = this.ctx.createRadialGradient(cx, cy, r * 0.2, cx, cy, r * 1.2);
    glowGrad.addColorStop(0, 'rgba(168, 85, 247, 0.45)');
    glowGrad.addColorStop(1, 'rgba(168, 85, 247, 0.0)');
    this.ctx.fillStyle = glowGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r * 1.2, 0, Math.PI * 2);
    this.ctx.fill();

    // Base pedestal
    this.ctx.fillStyle = '#4c1d95';
    this.ctx.beginPath();
    this.ctx.roundRect(cx - r, cy - r, r * 2, r * 2, 8);
    this.ctx.fill();
    this.ctx.strokeStyle = '#c084fc';
    this.ctx.lineWidth = 2;
    this.ctx.stroke();

    // Rotating energy ring
    this.ctx.strokeStyle = 'rgba(216, 180, 254, 0.7)';
    this.ctx.lineWidth = 1.8;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r * 0.68, 0, Math.PI * 2);
    this.ctx.stroke();

    // High-tech Converter symbol
    this.ctx.fillStyle = '#f5d0fe';
    this.ctx.font = `bold ${Math.floor(cellSize * 0.26)}px sans-serif`;
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText('💎➔🪙', cx, cy);

    this.ctx.restore();
  }

  drawCoin(x, y, cellSize) {
    const cx = x * cellSize + cellSize / 2;
    const cy = y * cellSize + cellSize / 2;
    const r = cellSize * 0.30;

    this.ctx.save();
    // Drop shadow
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.14)';
    this.ctx.beginPath();
    this.ctx.ellipse(cx, cy + r * 0.85, r * 0.9, r * 0.28, 0, 0, Math.PI * 2);
    this.ctx.fill();

    // Outer gold rim
    const rimGrad = this.ctx.createLinearGradient(cx - r, cy - r, cx + r, cy + r);
    rimGrad.addColorStop(0, '#fde047');
    rimGrad.addColorStop(0.5, '#eab308');
    rimGrad.addColorStop(1, '#ca8a04');
    this.ctx.fillStyle = rimGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r, 0, Math.PI * 2);
    this.ctx.fill();

    // Inner face
    const faceGrad = this.ctx.createRadialGradient(cx - r * 0.3, cy - r * 0.3, 1, cx, cy, r * 0.82);
    faceGrad.addColorStop(0, '#fef08a');
    faceGrad.addColorStop(0.6, '#facc15');
    faceGrad.addColorStop(1, '#eab308');
    this.ctx.fillStyle = faceGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r * 0.82, 0, Math.PI * 2);
    this.ctx.fill();

    // Inner engraved ring
    this.ctx.strokeStyle = '#ca8a04';
    this.ctx.lineWidth = 1;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r * 0.64, 0, Math.PI * 2);
    this.ctx.stroke();

    // Golden star in center
    this.ctx.fillStyle = '#b45309';
    this.ctx.font = `bold ${Math.floor(r * 0.9)}px sans-serif`;
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText('★', cx, cy + 0.5);

    // Specular crescent glint
    this.ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    this.ctx.beginPath();
    this.ctx.ellipse(cx - r * 0.35, cy - r * 0.35, r * 0.28, r * 0.14, -Math.PI / 4, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.restore();
  }

  drawDiamond(x, y, cellSize) {
    const cx = x * cellSize + cellSize / 2;
    const cy = y * cellSize + cellSize / 2;
    const s = cellSize * 0.32;

    this.ctx.save();
    // Cyan glow
    this.ctx.shadowColor = '#38bdf8';
    this.ctx.shadowBlur = 8;

    // Drop shadow
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.14)';
    this.ctx.beginPath();
    this.ctx.ellipse(cx, cy + s * 1.1, s * 0.85, s * 0.26, 0, 0, Math.PI * 2);
    this.ctx.fill();

    const topY = cy - s * 0.8;
    const midY = cy - s * 0.2;
    const botY = cy + s * 0.9;
    const leftX = cx - s * 0.9;
    const rightX = cx + s * 0.9;
    const tableLeftX = cx - s * 0.5;
    const tableRightX = cx + s * 0.5;

    // Lower pavilion
    const pavGrad = this.ctx.createLinearGradient(cx, midY, cx, botY);
    pavGrad.addColorStop(0, '#0284c7');
    pavGrad.addColorStop(1, '#0369a1');
    this.ctx.fillStyle = pavGrad;
    this.ctx.beginPath();
    this.ctx.moveTo(leftX, midY);
    this.ctx.lineTo(rightX, midY);
    this.ctx.lineTo(cx, botY);
    this.ctx.closePath();
    this.ctx.fill();

    // Upper crown
    const crownGrad = this.ctx.createLinearGradient(cx, topY, cx, midY);
    crownGrad.addColorStop(0, '#bae6fd');
    crownGrad.addColorStop(0.5, '#38bdf8');
    crownGrad.addColorStop(1, '#0284c7');
    this.ctx.fillStyle = crownGrad;
    this.ctx.beginPath();
    this.ctx.moveTo(tableLeftX, topY);
    this.ctx.lineTo(tableRightX, topY);
    this.ctx.lineTo(rightX, midY);
    this.ctx.lineTo(leftX, midY);
    this.ctx.closePath();
    this.ctx.fill();

    // Facet lines
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.75)';
    this.ctx.lineWidth = 1.2;
    this.ctx.beginPath();
    this.ctx.moveTo(tableLeftX, topY);
    this.ctx.lineTo(tableRightX, topY);
    this.ctx.moveTo(tableLeftX, topY);
    this.ctx.lineTo(cx - s * 0.2, midY);
    this.ctx.lineTo(tableRightX, topY);
    this.ctx.moveTo(cx - s * 0.2, midY);
    this.ctx.lineTo(cx, botY);
    this.ctx.stroke();

    // Border
    this.ctx.strokeStyle = '#0284c7';
    this.ctx.lineWidth = 1.5;
    this.ctx.beginPath();
    this.ctx.moveTo(tableLeftX, topY);
    this.ctx.lineTo(tableRightX, topY);
    this.ctx.lineTo(rightX, midY);
    this.ctx.lineTo(cx, botY);
    this.ctx.lineTo(leftX, midY);
    this.ctx.closePath();
    this.ctx.stroke();

    // Specular glint
    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.arc(cx + s * 0.3, topY + s * 0.22, 2.5, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.restore();
  }

  drawRobot(x, y, cellSize, theme = 'default') {
    const cx = x * cellSize + cellSize / 2;
    const cy = y * cellSize + cellSize / 2;
    const s = cellSize * 0.42;

    let primary = '#4f46e5';   // Indigo
    let secondary = '#6366f1';
    let accent = '#38bdf8';    // Glowing cyan eyes

    if (theme === 'rl' || theme === 'green') {
      primary = '#059669';     // Emerald
      secondary = '#10b981';
      accent = '#34d399';
    } else if (theme === 'gold') {
      primary = '#d97706';
      secondary = '#f59e0b';
      accent = '#fef08a';
    } else if (theme === 'red') {
      primary = '#dc2626';
      secondary = '#ef4444';
      accent = '#fca5a5';
    }

    this.ctx.save();

    // 1. Soft Floor Shadow
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.18)';
    this.ctx.beginPath();
    this.ctx.ellipse(cx, cy + s * 0.95, s * 0.75, s * 0.25, 0, 0, Math.PI * 2);
    this.ctx.fill();

    // 2. Hover thruster base
    this.ctx.fillStyle = '#334155';
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.42, cy + s * 0.65, s * 0.84, s * 0.24, 4);
    this.ctx.fill();

    // Thruster cyan glow
    const thrusterGrad = this.ctx.createRadialGradient(cx, cy + s * 0.78, 1, cx, cy + s * 0.78, s * 0.38);
    thrusterGrad.addColorStop(0, accent);
    thrusterGrad.addColorStop(1, 'rgba(0,0,0,0)');
    this.ctx.fillStyle = thrusterGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy + s * 0.78, s * 0.35, 0, Math.PI * 2);
    this.ctx.fill();

    // 3. Robot Torso
    const bodyGrad = this.ctx.createLinearGradient(cx - s * 0.5, cy + s * 0.08, cx + s * 0.5, cy + s * 0.68);
    bodyGrad.addColorStop(0, '#ffffff');
    bodyGrad.addColorStop(0.3, primary);
    bodyGrad.addColorStop(1, secondary);
    this.ctx.fillStyle = bodyGrad;
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.48, cy + s * 0.1, s * 0.96, s * 0.58, 6);
    this.ctx.fill();
    this.ctx.strokeStyle = '#1e1b4b';
    this.ctx.lineWidth = 1.2;
    this.ctx.stroke();

    // Chest Glowing Energy Core
    this.ctx.fillStyle = accent;
    this.ctx.shadowColor = accent;
    this.ctx.shadowBlur = 6;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy + s * 0.38, s * 0.15, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;

    // Robot arms
    this.ctx.fillStyle = '#64748b';
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.64, cy + s * 0.22, s * 0.14, s * 0.36, 3);
    this.ctx.roundRect(cx + s * 0.50, cy + s * 0.22, s * 0.14, s * 0.36, 3);
    this.ctx.fill();

    // 4. Antenna
    this.ctx.strokeStyle = '#64748b';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.moveTo(cx, cy - s * 0.6);
    this.ctx.lineTo(cx, cy - s * 0.85);
    this.ctx.stroke();

    // Golden antenna orb
    this.ctx.fillStyle = '#f59e0b';
    this.ctx.shadowColor = '#fbbf24';
    this.ctx.shadowBlur = 8;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy - s * 0.88, s * 0.11, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;

    // 5. Head
    const headGrad = this.ctx.createLinearGradient(cx - s * 0.55, cy - s * 0.62, cx + s * 0.55, cy + s * 0.05);
    headGrad.addColorStop(0, '#f8fafc');
    headGrad.addColorStop(0.5, '#e2e8f0');
    headGrad.addColorStop(1, '#cbd5e1');
    this.ctx.fillStyle = headGrad;
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.56, cy - s * 0.62, s * 1.12, s * 0.66, 8);
    this.ctx.fill();
    this.ctx.strokeStyle = '#475569';
    this.ctx.lineWidth = 1.2;
    this.ctx.stroke();

    // Side ear pads
    this.ctx.fillStyle = primary;
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.66, cy - s * 0.44, s * 0.11, s * 0.32, 2);
    this.ctx.roundRect(cx + s * 0.55, cy - s * 0.44, s * 0.11, s * 0.32, 2);
    this.ctx.fill();

    // 6. Glossy Visor Screen
    this.ctx.fillStyle = '#0f172a';
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.42, cy - s * 0.52, s * 0.84, s * 0.44, 6);
    this.ctx.fill();

    // Visor reflection shine
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
    this.ctx.lineWidth = 1;
    this.ctx.beginPath();
    this.ctx.arc(cx - s * 0.15, cy - s * 0.40, s * 0.22, -Math.PI / 4, Math.PI / 4);
    this.ctx.stroke();

    // 7. Cute Glowing Expressive Eyes
    this.ctx.fillStyle = accent;
    this.ctx.shadowColor = accent;
    this.ctx.shadowBlur = 8;
    const eyeR = s * 0.085;
    const eyeY = cy - s * 0.30;
    this.ctx.beginPath();
    this.ctx.arc(cx - s * 0.18, eyeY, eyeR, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.beginPath();
    this.ctx.arc(cx + s * 0.18, eyeY, eyeR, 0, Math.PI * 2);
    this.ctx.fill();

    // Eye catchlights
    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.arc(cx - s * 0.20, eyeY - s * 0.025, eyeR * 0.4, 0, Math.PI * 2);
    this.ctx.arc(cx + s * 0.16, eyeY - s * 0.025, eyeR * 0.4, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.restore();
  }

  drawEnemy(x, y, cellSize) {
    const cx = x * cellSize + cellSize / 2;
    const cy = y * cellSize + cellSize / 2;
    const s = cellSize * 0.42;

    this.ctx.save();

    // 0. Threat Perception Radar Zone (Soft translucent red danger field)
    const auraR = cellSize * 2.8;
    const auraGrad = this.ctx.createRadialGradient(cx, cy, s * 0.4, cx, cy, auraR);
    auraGrad.addColorStop(0, 'rgba(239, 68, 68, 0.12)');
    auraGrad.addColorStop(0.7, 'rgba(239, 68, 68, 0.04)');
    auraGrad.addColorStop(1, 'rgba(239, 68, 68, 0)');
    this.ctx.fillStyle = auraGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, auraR, 0, Math.PI * 2);
    this.ctx.fill();

    // Dotted detection circle line
    this.ctx.strokeStyle = 'rgba(239, 68, 68, 0.22)';
    this.ctx.lineWidth = 1;
    this.ctx.setLineDash([4, 4]);
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, auraR, 0, Math.PI * 2);
    this.ctx.stroke();
    this.ctx.setLineDash([]);

    // 1. Spooky Floor Shadow
    this.ctx.fillStyle = 'rgba(153, 27, 27, 0.25)';
    this.ctx.beginPath();
    this.ctx.ellipse(cx, cy + s * 0.95, s * 0.78, s * 0.25, 0, 0, Math.PI * 2);
    this.ctx.fill();

    // 2. Horns
    this.ctx.fillStyle = '#7f1d1d';
    // Left horn
    this.ctx.beginPath();
    this.ctx.moveTo(cx - s * 0.42, cy - s * 0.2);
    this.ctx.quadraticCurveTo(cx - s * 0.72, cy - s * 0.7, cx - s * 0.38, cy - s * 0.78);
    this.ctx.quadraticCurveTo(cx - s * 0.28, cy - s * 0.5, cx - s * 0.18, cy - s * 0.38);
    this.ctx.closePath();
    this.ctx.fill();
    // Right horn
    this.ctx.beginPath();
    this.ctx.moveTo(cx + s * 0.42, cy - s * 0.2);
    this.ctx.quadraticCurveTo(cx + s * 0.72, cy - s * 0.7, cx + s * 0.38, cy - s * 0.78);
    this.ctx.quadraticCurveTo(cx + s * 0.28, cy - s * 0.5, cx + s * 0.18, cy - s * 0.38);
    this.ctx.closePath();
    this.ctx.fill();

    // 3. Menacing Body
    const bodyGrad = this.ctx.createRadialGradient(cx, cy - s * 0.1, s * 0.1, cx, cy, s * 0.8);
    bodyGrad.addColorStop(0, '#ef4444');
    bodyGrad.addColorStop(0.6, '#dc2626');
    bodyGrad.addColorStop(1, '#991b1b');
    this.ctx.fillStyle = bodyGrad;
    this.ctx.shadowColor = '#ef4444';
    this.ctx.shadowBlur = 10;
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.62, cy - s * 0.44, s * 1.24, s * 1.12, [18, 18, 22, 22]);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;

    // 4. Glowing Yellow Eyes
    this.ctx.fillStyle = '#fef08a';
    this.ctx.shadowColor = '#fbbf24';
    this.ctx.shadowBlur = 8;
    const eyeW = s * 0.20;
    const eyeH = s * 0.24;
    this.ctx.beginPath();
    this.ctx.ellipse(cx - s * 0.26, cy - s * 0.08, eyeW, eyeH, -0.15, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.beginPath();
    this.ctx.ellipse(cx + s * 0.26, cy - s * 0.08, eyeW, eyeH, 0.15, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;

    // Dark pupils
    this.ctx.fillStyle = '#7f1d1d';
    this.ctx.beginPath();
    this.ctx.ellipse(cx - s * 0.24, cy - s * 0.08, eyeW * 0.4, eyeH * 0.65, 0, 0, Math.PI * 2);
    this.ctx.ellipse(cx + s * 0.24, cy - s * 0.08, eyeW * 0.4, eyeH * 0.65, 0, 0, Math.PI * 2);
    this.ctx.fill();

    // 5. Grinning mouth & sharp teeth
    this.ctx.fillStyle = '#450a0a';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy + s * 0.28, s * 0.32, 0.1 * Math.PI, 0.9 * Math.PI);
    this.ctx.closePath();
    this.ctx.fill();

    // Teeth
    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.moveTo(cx - s * 0.18, cy + s * 0.3);
    this.ctx.lineTo(cx - s * 0.09, cy + s * 0.44);
    this.ctx.lineTo(cx, cy + s * 0.3);
    this.ctx.moveTo(cx, cy + s * 0.3);
    this.ctx.lineTo(cx + s * 0.09, cy + s * 0.44);
    this.ctx.lineTo(cx + s * 0.18, cy + s * 0.3);
    this.ctx.closePath();
    this.ctx.fill();

    this.ctx.restore();
  }

  renderSingleAgentFrame(mapConfig, stateSnapshot, agentTheme = 'default') {
    const width = mapConfig.width || 8;
    const height = mapConfig.height || 8;
    const cellSize = this.canvas.width / width;

    this.clear();
    this.drawGrid(width, height);

    // 1. Walls
    if (mapConfig.walls) {
      for (const [wx, wy] of mapConfig.walls) {
        this.drawWall(wx, wy, cellSize);
      }
    }

    // 2. Exit Portal
    if (mapConfig.exit) {
      const [ex, ey] = mapConfig.exit;
      this.drawExit(ex, ey, cellSize);
    }

    // 3. Converter
    if (mapConfig.converter) {
      const [cx, cy] = mapConfig.converter;
      this.drawConverter(cx, cy, cellSize);
    }

    // 4. Coins remaining
    const coins = stateSnapshot.coins || mapConfig.coins || [];
    for (const [cx, cy] of coins) {
      this.drawCoin(cx, cy, cellSize);
    }

    // 5. Diamonds remaining
    const diamonds = stateSnapshot.diamonds || mapConfig.diamonds || [];
    for (const [dx, dy] of diamonds) {
      this.drawDiamond(dx, dy, cellSize);
    }

    // 6. Enemy
    if (stateSnapshot.enemy_pos) {
      const [ex, ey] = stateSnapshot.enemy_pos;
      this.drawEnemy(ex, ey, cellSize);
    }

    // 7. Agent Robot
    if (stateSnapshot.agent_pos) {
      const [ax, ay] = stateSnapshot.agent_pos;
      this.drawRobot(ax, ay, cellSize, agentTheme);
    }
  }

  renderArenaFrame(mapConfig, frame) {
    const width = mapConfig.width || 10;
    const height = mapConfig.height || 10;
    const cellSize = this.canvas.width / width;

    this.clear();
    this.drawGrid(width, height);

    // Walls
    if (mapConfig.walls) {
      for (const [wx, wy] of mapConfig.walls) {
        this.drawWall(wx, wy, cellSize);
      }
    }

    // Exit
    if (mapConfig.exit) {
      const [ex, ey] = mapConfig.exit;
      this.drawExit(ex, ey, cellSize);
    }

    // Converter
    if (mapConfig.converter) {
      const [cx, cy] = mapConfig.converter;
      this.drawConverter(cx, cy, cellSize);
    }

    // Coins
    if (frame.coins) {
      for (const [cx, cy] of frame.coins) {
        this.drawCoin(cx, cy, cellSize);
      }
    }

    // Diamonds
    if (frame.diamonds) {
      for (const [dx, dy] of frame.diamonds) {
        this.drawDiamond(dx, dy, cellSize);
      }
    }

    // Enemy
    if (frame.enemy) {
      this.drawEnemy(frame.enemy.x, frame.enemy.y, cellSize);
    }

    // Agents
    if (frame.agents) {
      const themes = ['default', 'rl', 'gold', 'red'];
      frame.agents.forEach((ag, idx) => {
        if (!ag.is_alive && !ag.has_exited) {
          // Defeated marker
          const cx = ag.x * cellSize + cellSize / 2;
          const cy = ag.y * cellSize + cellSize / 2;
          this.ctx.save();
          this.ctx.font = `${Math.floor(cellSize * 0.55)}px sans-serif`;
          this.ctx.textAlign = 'center';
          this.ctx.textBaseline = 'middle';
          this.ctx.fillText('💀', cx, cy);
          this.ctx.restore();
          return;
        }
        if (ag.has_exited) return;

        const theme = themes[idx % themes.length];
        this.drawRobot(ag.x, ag.y, cellSize, theme);
      });
    }
  }
}

