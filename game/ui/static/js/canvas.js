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
    // Escape trapdoor floor glow
    const glowGrad = this.ctx.createRadialGradient(cx, cy, r * 0.2, cx, cy, r * 1.25);
    glowGrad.addColorStop(0, 'rgba(16, 185, 129, 0.45)');
    glowGrad.addColorStop(1, 'rgba(16, 185, 129, 0.0)');
    this.ctx.fillStyle = glowGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r * 1.25, 0, Math.PI * 2);
    this.ctx.fill();

    // Steel escape hatch frame
    this.ctx.fillStyle = '#064e3b';
    this.ctx.beginPath();
    this.ctx.roundRect(cx - r, cy - r, r * 2, r * 2, 8);
    this.ctx.fill();
    this.ctx.strokeStyle = '#34d399';
    this.ctx.lineWidth = 2.2;
    this.ctx.stroke();

    // Escape hatch doorway
    const doorGrad = this.ctx.createRadialGradient(cx, cy, 2, cx, cy, r * 0.75);
    doorGrad.addColorStop(0, '#ecfdf5');
    doorGrad.addColorStop(0.5, '#10b981');
    doorGrad.addColorStop(1, '#047857');
    this.ctx.fillStyle = doorGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r * 0.72, 0, Math.PI * 2);
    this.ctx.fill();

    // Escape icon and text
    this.ctx.fillStyle = '#ffffff';
    this.ctx.font = `bold ${Math.floor(cellSize * 0.24)}px sans-serif`;
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText('فرار 🏃', cx, cy - 3);

    this.ctx.fillStyle = '#a7f3d0';
    this.ctx.font = `bold ${Math.floor(cellSize * 0.20)}px sans-serif`;
    this.ctx.fillText('EXIT', cx, cy + 10);

    this.ctx.restore();
  }

  drawConverter(x, y, cellSize) {
    const cx = x * cellSize + cellSize / 2;
    const cy = y * cellSize + cellSize / 2;
    const r = cellSize * 0.42;

    this.ctx.save();
    // Warm golden treasure aura
    const glowGrad = this.ctx.createRadialGradient(cx, cy, r * 0.2, cx, cy, r * 1.25);
    glowGrad.addColorStop(0, 'rgba(245, 158, 11, 0.50)');
    glowGrad.addColorStop(1, 'rgba(245, 158, 11, 0.0)');
    this.ctx.fillStyle = glowGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r * 1.25, 0, Math.PI * 2);
    this.ctx.fill();

    // Drop shadow
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
    this.ctx.beginPath();
    this.ctx.ellipse(cx, cy + r * 0.9, r * 0.95, r * 0.3, 0, 0, Math.PI * 2);
    this.ctx.fill();

    // Treasure Chest Body (Dark Mahagony Wood)
    const chestW = r * 1.7;
    const chestH = r * 1.3;
    const chestX = cx - chestW / 2;
    const chestY = cy - chestH / 2 + 2;

    const woodGrad = this.ctx.createLinearGradient(chestX, chestY, chestX, chestY + chestH);
    woodGrad.addColorStop(0, '#92400e');
    woodGrad.addColorStop(0.5, '#78350f');
    woodGrad.addColorStop(1, '#451a03');
    this.ctx.fillStyle = woodGrad;
    this.ctx.beginPath();
    this.ctx.roundRect(chestX, chestY, chestW, chestH, 6);
    this.ctx.fill();
    this.ctx.strokeStyle = '#292524';
    this.ctx.lineWidth = 1.5;
    this.ctx.stroke();

    // Gold Brass Banding Straps (Left & Right)
    const strapGrad = this.ctx.createLinearGradient(chestX, chestY, chestX, chestY + chestH);
    strapGrad.addColorStop(0, '#fef08a');
    strapGrad.addColorStop(0.5, '#f59e0b');
    strapGrad.addColorStop(1, '#b45309');
    this.ctx.fillStyle = strapGrad;
    // Left band
    this.ctx.fillRect(chestX + chestW * 0.15, chestY, chestW * 0.16, chestH);
    // Right band
    this.ctx.fillRect(chestX + chestW * 0.69, chestY, chestW * 0.16, chestH);

    // Chest Lid Rim
    this.ctx.fillStyle = '#d97706';
    this.ctx.fillRect(chestX, chestY + chestH * 0.35, chestW, chestH * 0.12);

    // Center Gold Lock Plate with Keyhole
    const lockW = chestW * 0.32;
    const lockH = chestH * 0.38;
    const lockX = cx - lockW / 2;
    const lockY = chestY + chestH * 0.32;
    this.ctx.fillStyle = '#fde047';
    this.ctx.beginPath();
    this.ctx.roundRect(lockX, lockY, lockW, lockH, 4);
    this.ctx.fill();
    this.ctx.strokeStyle = '#78350f';
    this.ctx.lineWidth = 1.2;
    this.ctx.stroke();

    // Keyhole
    this.ctx.fillStyle = '#1c1917';
    this.ctx.beginPath();
    this.ctx.arc(cx, lockY + lockH * 0.38, lockW * 0.16, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.beginPath();
    this.ctx.moveTo(cx - lockW * 0.09, lockY + lockH * 0.40);
    this.ctx.lineTo(cx + lockW * 0.09, lockY + lockH * 0.40);
    this.ctx.lineTo(cx + lockW * 0.12, lockY + lockH * 0.78);
    this.ctx.lineTo(cx - lockW * 0.12, lockY + lockH * 0.78);
    this.ctx.closePath();
    this.ctx.fill();

    // Top text tag: 🗝️➔💰
    this.ctx.fillStyle = '#ffffff';
    this.ctx.font = `bold ${Math.floor(cellSize * 0.22)}px sans-serif`;
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText('🗝️➔💰', cx, cy - r * 0.82);

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
    const s = cellSize * 0.36;

    this.ctx.save();
    // Warm golden sparkle glow
    this.ctx.shadowColor = '#f59e0b';
    this.ctx.shadowBlur = 10;

    // Drop shadow
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.18)';
    this.ctx.beginPath();
    this.ctx.ellipse(cx, cy + s * 1.05, s * 0.8, s * 0.24, 0, 0, Math.PI * 2);
    this.ctx.fill();

    // Slanted angle for sleek aesthetic key
    this.ctx.translate(cx, cy);
    this.ctx.rotate(-Math.PI / 4);

    // 1. Key Bow (Handle Ring with ornate head)
    const bowR = s * 0.42;
    const bowY = -s * 0.50;

    const goldGrad = this.ctx.createLinearGradient(-bowR, -bowR, bowR, bowR);
    goldGrad.addColorStop(0, '#fef08a');
    goldGrad.addColorStop(0.4, '#f59e0b');
    goldGrad.addColorStop(0.8, '#d97706');
    goldGrad.addColorStop(1, '#b45309');

    // Outer bow ring
    this.ctx.fillStyle = goldGrad;
    this.ctx.beginPath();
    this.ctx.arc(0, bowY, bowR, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.strokeStyle = '#78350f';
    this.ctx.lineWidth = 1.2;
    this.ctx.stroke();

    // Inner hollow of bow
    this.ctx.fillStyle = '#1e293b';
    this.ctx.beginPath();
    this.ctx.arc(0, bowY, bowR * 0.48, 0, Math.PI * 2);
    this.ctx.fill();

    // Decorative gemstone in ring center
    this.ctx.fillStyle = '#38bdf8';
    this.ctx.beginPath();
    this.ctx.arc(0, bowY, bowR * 0.28, 0, Math.PI * 2);
    this.ctx.fill();

    // 2. Key Stem (Shaft)
    const stemW = s * 0.18;
    const stemH = s * 1.10;
    this.ctx.fillStyle = goldGrad;
    this.ctx.beginPath();
    this.ctx.roundRect(-stemW / 2, bowY + bowR * 0.8, stemW, stemH, 3);
    this.ctx.fill();
    this.ctx.strokeStyle = '#78350f';
    this.ctx.lineWidth = 1.0;
    this.ctx.stroke();

    // 3. Key Bit (Lock teeth at bottom)
    const bitY = bowY + bowR * 0.8 + stemH * 0.65;
    const bitW = s * 0.32;
    const bitH = s * 0.16;

    // Tooth 1
    this.ctx.fillRect(stemW / 2 - 1, bitY, bitW, bitH);
    // Tooth 2 (lower)
    this.ctx.fillRect(stemW / 2 - 1, bitY + bitH * 1.3, bitW * 0.75, bitH);

    // Specular glint on bow
    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.arc(-bowR * 0.35, bowY - bowR * 0.35, 2.2, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.restore();
  }

  drawRobot(x, y, cellSize, theme = 'default', heading = 'RIGHT') {
    const cx = x * cellSize + cellSize / 2;
    const cy = y * cellSize + cellSize / 2;
    const s = cellSize * 0.42;

    // Thief theme accents:
    // Default: Sleek dark burglar with indigo stealth trim
    // RL: Master burglar with emerald stealth trim
    let trimColor = '#6366f1';
    let eyeColor = '#38bdf8';
    let sackGlow = '#f59e0b';

    if (theme === 'rl' || theme === 'green') {
      trimColor = '#10b981';
      eyeColor = '#34d399';
      sackGlow = '#10b981';
    } else if (theme === 'gold') {
      trimColor = '#f59e0b';
      eyeColor = '#fef08a';
      sackGlow = '#f59e0b';
    } else if (theme === 'red') {
      trimColor = '#ef4444';
      eyeColor = '#fca5a5';
      sackGlow = '#ef4444';
    }

    this.ctx.save();

    // 1. Soft Floor Shadow
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.22)';
    this.ctx.beginPath();
    this.ctx.ellipse(cx, cy + s * 0.95, s * 0.76, s * 0.25, 0, 0, Math.PI * 2);
    this.ctx.fill();

    // 2. Swag / Loot Bag on back (bulging with coins & loot)
    const bagX = cx - s * 0.42;
    const bagY = cy + s * 0.20;
    const bagR = s * 0.34;
    const bagGrad = this.ctx.createRadialGradient(bagX, bagY, 2, bagX, bagY, bagR);
    bagGrad.addColorStop(0, '#d97706');
    bagGrad.addColorStop(0.7, '#92400e');
    bagGrad.addColorStop(1, '#451a03');
    this.ctx.fillStyle = bagGrad;
    this.ctx.beginPath();
    this.ctx.arc(bagX, bagY, bagR, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.strokeStyle = '#292524';
    this.ctx.lineWidth = 1.2;
    this.ctx.stroke();

    // Dollar/Loot symbol on sack
    this.ctx.fillStyle = '#fde047';
    this.ctx.font = `bold ${Math.floor(s * 0.28)}px sans-serif`;
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText('$', bagX, bagY);

    // 3. Thief Torso / Stealth Outfit
    const torsoGrad = this.ctx.createLinearGradient(cx - s * 0.4, cy, cx + s * 0.4, cy + s * 0.65);
    torsoGrad.addColorStop(0, '#334155');
    torsoGrad.addColorStop(0.5, '#1e293b');
    torsoGrad.addColorStop(1, '#0f172a');
    this.ctx.fillStyle = torsoGrad;
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.42, cy + s * 0.12, s * 0.84, s * 0.58, 6);
    this.ctx.fill();
    this.ctx.strokeStyle = trimColor;
    this.ctx.lineWidth = 1.5;
    this.ctx.stroke();

    // Stealth belt with gold buckle
    this.ctx.fillStyle = '#020617';
    this.ctx.fillRect(cx - s * 0.42, cy + s * 0.52, s * 0.84, s * 0.12);
    this.ctx.fillStyle = '#f59e0b';
    this.ctx.fillRect(cx - s * 0.12, cy + s * 0.50, s * 0.24, s * 0.16);

    // 4. Thief Head & Knit Beanie (کلاه مشکی سارق)
    const headGrad = this.ctx.createRadialGradient(cx, cy - s * 0.35, 2, cx, cy - s * 0.35, s * 0.55);
    headGrad.addColorStop(0, '#475569');
    headGrad.addColorStop(0.6, '#1e293b');
    headGrad.addColorStop(1, '#0f172a');
    this.ctx.fillStyle = headGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy - s * 0.35, s * 0.52, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.strokeStyle = '#020617';
    this.ctx.lineWidth = 1.2;
    this.ctx.stroke();

    // Beanie cuff trim
    this.ctx.fillStyle = trimColor;
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.46, cy - s * 0.56, s * 0.92, s * 0.16, 4);
    this.ctx.fill();

    // 5. Black Domino Eye Mask (نقاب سیاه دزدی دور چشم)
    this.ctx.fillStyle = '#020617';
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.44, cy - s * 0.38, s * 0.88, s * 0.24, 6);
    this.ctx.fill();
    this.ctx.strokeStyle = '#000000';
    this.ctx.lineWidth = 1.5;
    this.ctx.stroke();

    // Heading shift for thief eyes
    let lookDx = 0;
    let lookDy = 0;
    if (heading === 'LEFT') lookDx = -s * 0.08;
    else if (heading === 'RIGHT') lookDx = s * 0.08;
    else if (heading === 'UP') lookDy = -s * 0.06;
    else if (heading === 'DOWN') lookDy = s * 0.06;

    // 6. Expressive, Sharp Cunning Eyes (چشم‌های تیزبین و درخشان سارق)
    const eyeR = s * 0.08;
    const eyeY = cy - s * 0.26 + lookDy;

    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.arc(cx - s * 0.18 + lookDx, eyeY, eyeR * 1.1, 0, Math.PI * 2);
    this.ctx.arc(cx + s * 0.18 + lookDx, eyeY, eyeR * 1.1, 0, Math.PI * 2);
    this.ctx.fill();

    // Glowing Pupils looking towards heading
    this.ctx.fillStyle = eyeColor;
    this.ctx.shadowColor = eyeColor;
    this.ctx.shadowBlur = 6;
    this.ctx.beginPath();
    this.ctx.arc(cx - s * 0.18 + lookDx * 1.2, eyeY, eyeR * 0.65, 0, Math.PI * 2);
    this.ctx.arc(cx + s * 0.18 + lookDx * 1.2, eyeY, eyeR * 0.65, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;

    // 7. Directional Chevron on Beanie
    this.ctx.fillStyle = '#fde047';
    this.ctx.font = `bold ${Math.floor(s * 0.24)}px sans-serif`;
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    const arrowMap = { UP: '▲', DOWN: '▼', LEFT: '◀', RIGHT: '▶' };
    this.ctx.fillText(arrowMap[heading] || '▶', cx, cy - s * 0.70);

    this.ctx.restore();
  }

  drawEnemy(x, y, cellSize, isStunned = false, heading = 'RIGHT') {
    const cx = x * cellSize + cellSize / 2;
    const cy = y * cellSize + cellSize / 2;
    const s = cellSize * 0.42;

    this.ctx.save();

    // 0. Police Inspection / Siren Radar Zone (Only if active and not stunned)
    if (!isStunned) {
      const auraR = cellSize * 2.8;
      const auraGrad = this.ctx.createRadialGradient(cx, cy, s * 0.4, cx, cy, auraR);
      auraGrad.addColorStop(0, 'rgba(59, 130, 246, 0.15)');
      auraGrad.addColorStop(0.5, 'rgba(239, 68, 68, 0.08)');
      auraGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      this.ctx.fillStyle = auraGrad;
      this.ctx.beginPath();
      this.ctx.arc(cx, cy, auraR, 0, Math.PI * 2);
      this.ctx.fill();

      // Flashing Police inspection perimeter line
      this.ctx.strokeStyle = 'rgba(59, 130, 246, 0.35)';
      this.ctx.lineWidth = 1.2;
      this.ctx.setLineDash([5, 5]);
      this.ctx.beginPath();
      this.ctx.arc(cx, cy, auraR, 0, Math.PI * 2);
      this.ctx.stroke();
      this.ctx.setLineDash([]);
    } else {
      // Gentle yellow dizzy aura
      const auraR = cellSize * 1.5;
      const auraGrad = this.ctx.createRadialGradient(cx, cy, s * 0.4, cx, cy, auraR);
      auraGrad.addColorStop(0, 'rgba(250, 204, 21, 0.28)');
      auraGrad.addColorStop(1, 'rgba(250, 204, 21, 0)');
      this.ctx.fillStyle = auraGrad;
      this.ctx.beginPath();
      this.ctx.arc(cx, cy, auraR, 0, Math.PI * 2);
      this.ctx.fill();
    }

    // 1. Floor Shadow
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.22)';
    this.ctx.beginPath();
    this.ctx.ellipse(cx, cy + s * 0.95, s * 0.78, s * 0.25, 0, 0, Math.PI * 2);
    this.ctx.fill();

    // 2. Police Uniform Torso (Deep Navy Blue Officer Suit)
    const suitGrad = this.ctx.createLinearGradient(cx - s * 0.5, cy, cx + s * 0.5, cy + s * 0.75);
    suitGrad.addColorStop(0, '#1e3a8a');
    suitGrad.addColorStop(0.5, '#1e40af');
    suitGrad.addColorStop(1, '#172554');
    this.ctx.fillStyle = suitGrad;
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.52, cy + s * 0.08, s * 1.04, s * 0.65, 8);
    this.ctx.fill();
    this.ctx.strokeStyle = '#0f172a';
    this.ctx.lineWidth = 1.5;
    this.ctx.stroke();

    // White shirt collar & gold tie
    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.moveTo(cx - s * 0.18, cy + s * 0.08);
    this.ctx.lineTo(cx, cy + s * 0.28);
    this.ctx.lineTo(cx + s * 0.18, cy + s * 0.08);
    this.ctx.fill();
    // Gold tie
    this.ctx.fillStyle = '#f59e0b';
    this.ctx.beginPath();
    this.ctx.moveTo(cx - s * 0.06, cy + s * 0.20);
    this.ctx.lineTo(cx + s * 0.06, cy + s * 0.20);
    this.ctx.lineTo(cx + s * 0.08, cy + s * 0.48);
    this.ctx.lineTo(cx, cy + s * 0.55);
    this.ctx.lineTo(cx - s * 0.08, cy + s * 0.48);
    this.ctx.closePath();
    this.ctx.fill();

    // Shiny Golden Police Badge / Shield on chest
    this.ctx.fillStyle = '#fbbf24';
    this.ctx.shadowColor = '#f59e0b';
    this.ctx.shadowBlur = 4;
    this.ctx.beginPath();
    const badgeX = cx - s * 0.32;
    const badgeY = cy + s * 0.22;
    const badgeS = s * 0.14;
    this.ctx.arc(badgeX, badgeY, badgeS, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;
    this.ctx.fillStyle = '#78350f';
    this.ctx.font = `bold ${Math.floor(s * 0.18)}px sans-serif`;
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText('★', badgeX, badgeY + 0.5);

    // 3. Police Head & Peaked Visor Cap (کلاه فرم پلیس با نشان نظامی)
    const headGrad = this.ctx.createRadialGradient(cx, cy - s * 0.30, 2, cx, cy - s * 0.30, s * 0.48);
    headGrad.addColorStop(0, '#fde047');
    headGrad.addColorStop(0.5, '#facc15');
    headGrad.addColorStop(1, '#ca8a04');
    // Officer face
    this.ctx.fillStyle = '#fed7aa';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy - s * 0.28, s * 0.42, 0, Math.PI * 2);
    this.ctx.fill();

    // Peaked Cap Crown (کلاه سرمه‌ای)
    const capGrad = this.ctx.createLinearGradient(cx - s * 0.55, cy - s * 0.70, cx + s * 0.55, cy - s * 0.35);
    capGrad.addColorStop(0, '#1d4ed8');
    capGrad.addColorStop(0.7, '#1e3a8a');
    capGrad.addColorStop(1, '#0f172a');
    this.ctx.fillStyle = capGrad;
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.56, cy - s * 0.72, s * 1.12, s * 0.40, [14, 14, 2, 2]);
    this.ctx.fill();

    // Black Glossy Cap Visor (لبه براق کلاه)
    this.ctx.fillStyle = '#020617';
    this.ctx.beginPath();
    this.ctx.roundRect(cx - s * 0.60, cy - s * 0.42, s * 1.20, s * 0.14, 4);
    this.ctx.fill();

    // Gold Eagle / Star Crest on Cap
    this.ctx.fillStyle = '#fbbf24';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy - s * 0.52, s * 0.11, 0, Math.PI * 2);
    this.ctx.fill();

    // 4. Emergency Police Siren on Top of Hat (چراغ گردان آژیر پلیس قرمز و آبی 🚨)
    if (!isStunned) {
      // Siren mount
      this.ctx.fillStyle = '#334155';
      this.ctx.fillRect(cx - s * 0.18, cy - s * 0.82, s * 0.36, s * 0.10);

      // Flashing Blue Beacon (Left)
      const blueGrad = this.ctx.createRadialGradient(cx - s * 0.10, cy - s * 0.90, 1, cx - s * 0.10, cy - s * 0.90, s * 0.24);
      blueGrad.addColorStop(0, '#60a5fa');
      blueGrad.addColorStop(0.5, '#2563eb');
      blueGrad.addColorStop(1, '#1d4ed8');
      this.ctx.fillStyle = blueGrad;
      this.ctx.shadowColor = '#3b82f6';
      this.ctx.shadowBlur = 10;
      this.ctx.beginPath();
      this.ctx.roundRect(cx - s * 0.20, cy - s * 0.98, s * 0.18, s * 0.18, 4);
      this.ctx.fill();

      // Flashing Red Beacon (Right)
      const redGrad = this.ctx.createRadialGradient(cx + s * 0.10, cy - s * 0.90, 1, cx + s * 0.10, cy - s * 0.90, s * 0.24);
      redGrad.addColorStop(0, '#f87171');
      redGrad.addColorStop(0.5, '#dc2626');
      redGrad.addColorStop(1, '#991b1b');
      this.ctx.fillStyle = redGrad;
      this.ctx.shadowColor = '#ef4444';
      this.ctx.shadowBlur = 10;
      this.ctx.beginPath();
      this.ctx.roundRect(cx + s * 0.02, cy - s * 0.98, s * 0.18, s * 0.18, 4);
      this.ctx.fill();
      this.ctx.shadowBlur = 0;
    } else {
      // Dimmed siren when stunned
      this.ctx.fillStyle = '#475569';
      this.ctx.fillRect(cx - s * 0.18, cy - s * 0.88, s * 0.36, s * 0.16);
    }

    // 5. Eyes / Glasses (Serious Cop Aviators or Dizzy X X)
    if (isStunned) {
      // Dizzy 'X X' yellow eyes
      this.ctx.strokeStyle = '#eab308';
      this.ctx.lineWidth = 2.5;
      const eyeOffset = s * 0.22;
      const eyeY = cy - s * 0.24;
      const d = s * 0.09;

      this.ctx.beginPath();
      this.ctx.moveTo(cx - eyeOffset - d, eyeY - d);
      this.ctx.lineTo(cx - eyeOffset + d, eyeY + d);
      this.ctx.moveTo(cx - eyeOffset + d, eyeY - d);
      this.ctx.lineTo(cx - eyeOffset - d, eyeY + d);
      this.ctx.moveTo(cx + eyeOffset - d, eyeY - d);
      this.ctx.lineTo(cx + eyeOffset + d, eyeY + d);
      this.ctx.moveTo(cx + eyeOffset + d, eyeY - d);
      this.ctx.lineTo(cx + eyeOffset - d, eyeY + d);
      this.ctx.stroke();

      // Dizzy spinning stars
      this.ctx.font = `${Math.floor(cellSize * 0.40)}px sans-serif`;
      this.ctx.textAlign = 'center';
      this.ctx.textBaseline = 'middle';
      this.ctx.fillText('💫', cx, cy - s * 1.05);
    } else {
      // Direction offsets for cop eyes
      let eLookDx = 0;
      let eLookDy = 0;
      if (heading === 'LEFT') eLookDx = -s * 0.07;
      else if (heading === 'RIGHT') eLookDx = s * 0.07;
      else if (heading === 'UP') eLookDy = -s * 0.06;
      else if (heading === 'DOWN') eLookDy = s * 0.06;

      // Dark Aviator sunglasses / stern eyes
      this.ctx.fillStyle = '#0f172a';
      this.ctx.beginPath();
      this.ctx.roundRect(cx - s * 0.36, cy - s * 0.34, s * 0.32, s * 0.20, 5);
      this.ctx.roundRect(cx + s * 0.04, cy - s * 0.34, s * 0.32, s * 0.20, 5);
      this.ctx.fill();
      this.ctx.strokeStyle = '#f59e0b';
      this.ctx.lineWidth = 1;
      this.ctx.stroke();

      // Aviator glasses bridge
      this.ctx.beginPath();
      this.ctx.moveTo(cx - s * 0.04, cy - s * 0.28);
      this.ctx.lineTo(cx + s * 0.04, cy - s * 0.28);
      this.ctx.stroke();

      // White reflection glint in glasses shifted towards heading
      this.ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
      this.ctx.beginPath();
      this.ctx.arc(cx - s * 0.20 + eLookDx, cy - s * 0.26 + eLookDy, 2.4, 0, Math.PI * 2);
      this.ctx.arc(cx + s * 0.20 + eLookDx, cy - s * 0.26 + eLookDy, 2.4, 0, Math.PI * 2);
      this.ctx.fill();

      // Direction indicator arrow on cap
      this.ctx.fillStyle = '#fbbf24';
      this.ctx.font = `bold ${Math.floor(s * 0.24)}px sans-serif`;
      this.ctx.textAlign = 'center';
      this.ctx.textBaseline = 'middle';
      const arrowMap = { UP: '▲', DOWN: '▼', LEFT: '◀', RIGHT: '▶' };
      this.ctx.fillText(arrowMap[heading] || '▶', cx, cy - s * 0.65);
    }

    // 6. Police Whistle / Stern Mouth
    this.ctx.strokeStyle = '#78350f';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.moveTo(cx - s * 0.12, cy - s * 0.08);
    this.ctx.lineTo(cx + s * 0.12, cy - s * 0.08);
    this.ctx.stroke();

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
      const isStunned = !!(stateSnapshot.enemy_stunned || (stateSnapshot.stun_timer && stateSnapshot.stun_timer > 0));
      const enemyHeading = stateSnapshot.enemy_heading || (mapConfig.enemy && mapConfig.enemy.patrol_direction) || 'RIGHT';
      this.drawEnemy(ex, ey, cellSize, isStunned, enemyHeading);
    }

    // 7. Agent Robot
    if (stateSnapshot.agent_pos) {
      const [ax, ay] = stateSnapshot.agent_pos;
      const agentHeading = stateSnapshot.agent_heading || stateSnapshot.action || 'RIGHT';
      this.drawRobot(ax, ay, cellSize, agentTheme, agentHeading);
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
      const isStunned = !!(frame.enemy.is_stunned || (frame.enemy.stun_timer && frame.enemy.stun_timer > 0));
      const enemyHeading = frame.enemy.patrol_direction || 'RIGHT';
      this.drawEnemy(frame.enemy.x, frame.enemy.y, cellSize, isStunned, enemyHeading);
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

        this.drawRobot(ag.x, ag.y, cellSize, themes[idx % themes.length], ag.heading || 'RIGHT');
      });
    }
  }
}

