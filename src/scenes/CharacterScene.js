import Phaser from 'phaser';
import RiggedSprite from '../characters/RiggedSprite.js';
import { idlePose, walkPose, WALK_FRAMES } from '../characters/animations.js';
import { SPEED, STRIDE } from '../world/Player.js';

const COMPASS = [
  ['NW', 'N', 'NE'],
  ['W', null, 'E'],
  ['SW', 'S', 'SE'],
];
const DIR_NAMES = {
  N: 'Nord', NE: 'Nordost', E: 'Ost', SE: 'Südost',
  S: 'Süd', SW: 'Südwest', W: 'West', NW: 'Nordwest',
};
const PART_NAMES = {
  hair_back: 'Haare hinten', hair_front: 'Haare vorne', head: 'Kopf', torso: 'Oberkörper',
  upper_arm_R: 'Oberarm re.', forearm_R: 'Unterarm re.',
  upper_arm_L: 'Oberarm li.', forearm_L: 'Unterarm li.',
  skirt_front: 'Rock vorne', skirt_back: 'Rock hinten',
  thigh_R: 'Oberschenkel re.', shin_R: 'Schienbein re.', foot_R: 'Fuß re.',
  thigh_L: 'Oberschenkel li.', shin_L: 'Schienbein li.', foot_L: 'Fuß li.',
};
const CELL = 64; // Platz pro Figur (Figur ist 62×62 Pixel)
const TEXT = { fontFamily: 'monospace', fontSize: '13px', color: '#e8dcdc' };

/** Zeigt die Vampirin in allen 8 Richtungen (stehend oder laufend) und ihre Skelett-Teile. */
export default class CharacterScene extends Phaser.Scene {
  constructor() {
    super('Character');
  }

  create() {
    this.cameras.main.setBackgroundColor('#2b2430');
    this.rig = this.cache.json.get('vampire-rig');
    this.selected = this.selected ?? 'S';
    this.walking = this.walking ?? false;
    this.showFrames = this.showFrames ?? false;
    this.figures = [];

    this.input.keyboard.on('keydown-F', () => this.scene.start('World'));
    this.input.keyboard.on('keydown-SPACE', () => {
      this.walking = !this.walking;
    });
    this.input.keyboard.on('keydown-B', () => {
      this.showFrames = !this.showFrames;
      this.scene.restart();
    });
    this.scale.once('resize', () => this.scene.restart());
    const hud = document.getElementById('hud');
    if (hud) hud.textContent = '';

    if (this.showFrames) {
      this.createFrameStrip();
      return;
    }

    const { width, height } = this.scale.gameSize;
    // Ganzzahlige Vergrößerung, damit die Pixel gleich groß bleiben
    const s = Math.max(1, Math.floor(Math.min((width * 0.5) / (3 * CELL), (height - 70) / (3 * CELL + 30))));

    this.add.text(16, 12, 'Vampirin – 8 Richtungen & Skelett-Teile', { ...TEXT, fontSize: '16px' });
    this.add.text(16, 34,
      'Leertaste: Laufen an/aus · B: Einzelbilder · Klick auf Figur: Teile · F: zur Welt', {
        ...TEXT, color: '#a99aa6',
      });

    const ox = 16;
    const oy = 64;
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        const dir = COMPASS[r][c];
        if (!dir) continue;
        const cx = ox + (c + 0.5) * CELL * s;
        const top = oy + r * (CELL * s + 26);
        const fig = new RiggedSprite(this, Math.round(cx), Math.round(top + 61 * s), 'vampire',
          this.rig, dir);
        fig.setScale(s);
        this.figures.push({ fig, offset: (r * 3 + c) * 170 });
        this.add.text(cx, top + CELL * s + 2, DIR_NAMES[dir], {
          ...TEXT, color: dir === this.selected ? '#ff6b7a' : TEXT.color,
        }).setOrigin(0.5, 0);
        const hit = this.add.zone(cx, top + (CELL * s) / 2, CELL * s, CELL * s).setInteractive({
          useHandCursor: true,
        });
        hit.on('pointerdown', () => {
          this.selected = dir;
          this.scene.restart();
        });
      }
    }

    // Teile der gewählten Richtung einzeln (explodierte Ansicht)
    const px = ox + 3 * CELL * s + 32;
    const py = 64;
    const areaW = width - px - 16;
    this.add.text(px, py, `Teile (${DIR_NAMES[this.selected]}), von hinten nach vorne:`, TEXT);
    const dir = this.rig.directions[this.selected];
    let x = px;
    let y = py + 24;
    let rowH = 0;
    for (const name of dir.order) {
      const part = dir.parts[name];
      const w = Math.max(part.w * s, 118);
      const h = part.h * s + 18;
      if (x + w > px + areaW) {
        x = px;
        y += rowH + 10;
        rowH = 0;
      }
      this.add.rectangle(x, y + 16, part.w * s, part.h * s, 0x3a3140).setOrigin(0);
      this.add.image(x, y + 16, 'vampire', part.frame).setOrigin(0).setScale(s);
      this.add.text(x, y, PART_NAMES[name] ?? name, { ...TEXT, fontSize: '11px', color: '#c9b8c4' });
      x += w + 12;
      rowH = Math.max(rowH, h);
    }
  }

  /** Alle Einzelbilder des Laufzyklus: eine Zeile pro Richtung (W/SW/NW sind gespiegelt). */
  createFrameStrip() {
    const rows = ['S', 'SE', 'E', 'NE', 'N'];
    const { width, height } = this.scale.gameSize;
    const labelW = 90;
    const s = Math.max(1, Math.floor(Math.min(
      (width - labelW - 32) / (WALK_FRAMES * CELL),
      (height - 80) / (rows.length * (CELL + 4)),
    )));
    this.add.text(16, 12, 'Laufzyklus – alle Einzelbilder', { ...TEXT, fontSize: '16px' });
    this.add.text(16, 34, 'B: zurück zur Übersicht · F: zur Welt (West-Richtungen = gespiegelt)', {
      ...TEXT, color: '#a99aa6',
    });
    rows.forEach((dir, r) => {
      const top = 64 + r * (CELL + 4) * s;
      this.add.text(16, top + (CELL * s) / 2, DIR_NAMES[dir], TEXT).setOrigin(0, 0.5);
      for (let f = 0; f < WALK_FRAMES; f++) {
        const cx = labelW + 16 + (f + 0.5) * CELL * s;
        this.add.rectangle(cx, top + (CELL * s) / 2, CELL * s - 4, CELL * s - 4, 0x332a39);
        const fig = new RiggedSprite(this, Math.round(cx), Math.round(top + 61 * s), 'vampire',
          this.rig, dir);
        fig.setScale(s);
        fig.setPose(walkPose(dir, (f + 0.5) / WALK_FRAMES));
        if (r === 0) {
          this.add.text(cx, 52, `Bild ${f + 1}`, { ...TEXT, fontSize: '11px', color: '#a99aa6' })
            .setOrigin(0.5, 0);
        }
      }
    });
  }

  update(time) {
    // Laufen auf der Stelle: gleiche Geschwindigkeit wie im Spiel
    const phase = (time / 1000) * (SPEED / STRIDE);
    for (const { fig, offset } of this.figures) {
      fig.setPose(this.walking ? walkPose(fig.direction, phase) : idlePose(time + offset));
    }
  }
}
