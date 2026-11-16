import Phaser from 'phaser';
import CharacterRig from '../characters/CharacterRig.js';
import { startIdle } from '../characters/idle.js';

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

/** Zeigt die Vampirin in allen 8 Richtungen und ihre Skelett-Teile. */
export default class CharacterScene extends Phaser.Scene {
  constructor() {
    super('Character');
  }

  create() {
    this.cameras.main.setBackgroundColor('#2b2430');
    this.rig = this.cache.json.get('vampire-rig');
    this.selected = this.selected ?? 'S';

    const { width, height } = this.scale.gameSize;
    const wide = width >= height;
    // Ganzzahlige Vergrößerung, damit die Pixel gleich groß bleiben
    const compassW = wide ? width * 0.5 : width;
    const compassH = wide ? height - 70 : height * 0.55;
    const s = Math.max(1, Math.floor(Math.min(compassW / (3 * CELL), compassH / (3 * CELL + 30))));
    this.s = s;

    this.add.text(16, 12, 'Vampirin – 8 Richtungen & Skelett-Teile', { ...TEXT, fontSize: '16px' });
    this.add.text(16, 34, 'Klick auf eine Figur: Teile anzeigen · F: zurück zur Welt', {
      ...TEXT, color: '#a99aa6',
    });
    this.input.keyboard.on('keydown-F', () => this.scene.start('World'));
    const hud = document.getElementById('hud');
    if (hud) hud.textContent = '';

    const ox = 16;
    const oy = 64;
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        const dir = COMPASS[r][c];
        if (!dir) continue;
        const cx = ox + (c + 0.5) * CELL * s;
        const top = oy + r * (CELL * s + 26);
        const fig = new CharacterRig(this, Math.round(cx), Math.round(top + 61 * s), 'vampire',
          this.rig, dir);
        fig.setScale(s);
        startIdle(this, fig, { delay: (r * 3 + c) * 170 });
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
    const px = wide ? ox + 3 * CELL * s + 32 : 16;
    const py = wide ? 64 : oy + 3 * (CELL * s + 26) + 10;
    const areaW = (wide ? width - px : width) - 16;
    this.add.text(px, py, `Teile (${DIR_NAMES[this.selected]}), von hinten nach vorne:`, TEXT);
    const dir = this.rig.directions[this.selected];
    const ps = s;
    let x = px;
    let y = py + 24;
    let rowH = 0;
    for (const name of dir.order) {
      const part = dir.parts[name];
      const w = Math.max(part.w * ps, 118);
      const h = part.h * ps + 18;
      if (x + w > px + areaW) {
        x = px;
        y += rowH + 10;
        rowH = 0;
      }
      this.add.rectangle(x, y + 16, part.w * ps, part.h * ps, 0x3a3140).setOrigin(0);
      this.add.image(x, y + 16, 'vampire', part.frame).setOrigin(0).setScale(ps);
      this.add.text(x, y, PART_NAMES[name] ?? name, { ...TEXT, fontSize: '11px', color: '#c9b8c4' });
      x += w + 12;
      rowH = Math.max(rowH, h);
    }

    this.scale.once('resize', () => this.scene.restart());
  }
}
