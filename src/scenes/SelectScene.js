import Phaser from 'phaser';
import RiggedSprite from '../characters/RiggedSprite.js';
import { idlePose, walkPose } from '../characters/animations.js';
import { CHARACTERS, chooseCharacter, currentCharacter, rigKey } from '../characters/roster.js';
import { SPEED, STRIDE } from '../world/Player.js';

// Farben und Schriften wie die Startkarte des Artefakts (tools/build-artifact.mjs)
const NIGHT = 0x120f18;
const DUSK = 0x1c1a22;
const BLOOD = 0xb11c26;
const BONE = '#f6e9df';
const MIST = '#b3a6b2';
const FONT_TITLE = '"Pirata One", Georgia, serif';
const FONT_UI = '"Pixelify Sans", ui-monospace, monospace';
const FONTS = ['32px "Pirata One"', '16px "Pixelify Sans"'];

const CELL = 64; // Platz pro Figur in Originalpixeln (Figur ist 62×62)

/**
 * Figurenwahl: alle spielbaren Figuren nebeneinander. Die gewählte läuft auf
 * der Stelle, die anderen atmen ruhig. ←/→ bzw. A/D wählen, Enter oder
 * Leertaste startet; mit der Maus genügt ein Klick auf die Figur.
 */
export default class SelectScene extends Phaser.Scene {
  constructor() {
    super('Select');
  }

  create() {
    this.cameras.main.setBackgroundColor(NIGHT);
    const hud = document.getElementById('hud');
    if (hud) hud.textContent = '';
    this.index = CHARACTERS.indexOf(currentCharacter(this.registry));

    const { width, height } = this.scale.gameSize;
    const n = CHARACTERS.length;
    // Ganzzahlige Vergrößerung, damit die Pixel gleich groß bleiben
    const s = Phaser.Math.Clamp(Math.floor(Math.min(
      (width - 48) / (n * (CELL + 16)),
      (height - 230) / (CELL + 14),
    )), 1, 6);
    const cardW = (CELL + 10) * s;
    const cardH = (CELL + 8) * s;
    const gap = Math.max(24, 6 * s);
    const left = Math.round(width / 2 - (n * cardW + (n - 1) * gap) / 2);
    const top = Math.round(Math.max(96, (height - cardH) / 2 - 10));

    this.add.text(width / 2, top - 30, 'Wähle deine Figur', {
      fontFamily: FONT_TITLE, fontSize: `${Math.max(32, Math.min(64, 11 * s))}px`, color: BONE,
    }).setOrigin(0.5, 1);

    this.frames = this.add.graphics();
    this.cards = CHARACTERS.map((character, i) => {
      const x = left + i * (cardW + gap);
      const cx = x + cardW / 2;
      // Schatten unter den Füßen
      this.add.ellipse(cx, top + (CELL + 1) * s, 30 * s, 6 * s, 0x000000, 0.45);
      const fig = new RiggedSprite(this, Math.round(cx), Math.round(top + (CELL + 1) * s), character.file,
        this.cache.json.get(rigKey(character)), 'S');
      fig.setScale(s);
      const name = this.add.text(cx, top + cardH + 14, character.name, {
        fontFamily: FONT_TITLE, fontSize: `${Math.max(26, 7 * s)}px`, color: BONE,
      }).setOrigin(0.5, 0);
      const zone = this.add.zone(x, top, cardW, cardH + 14 + name.height).setOrigin(0)
        .setInteractive({ useHandCursor: true });
      zone.on('pointerover', () => this.select(i));
      zone.on('pointerdown', () => {
        this.select(i);
        this.begin();
      });
      return { x, w: cardW, h: cardH, fig, name, motion: character.motion, offset: i * 350 };
    });
    this.top = top;

    this.add.text(width / 2, Math.min(height - 24, top + cardH + 90),
      '← → oder A D: Figur wählen   ·   Enter oder Leertaste: spielen', {
        fontFamily: FONT_UI, fontSize: '16px', color: MIST,
      }).setOrigin(0.5, 1);

    const keys = this.input.keyboard;
    for (const k of ['LEFT', 'A']) keys.on(`keydown-${k}`, () => this.select(this.index - 1));
    for (const k of ['RIGHT', 'D']) keys.on(`keydown-${k}`, () => this.select(this.index + 1));
    for (const k of ['ENTER', 'SPACE']) keys.on(`keydown-${k}`, () => this.begin());
    this.scale.once('resize', () => this.scene.restart());

    this.select(this.index);
    this.waitForFonts();
  }

  /** Auswahl wechseln (rundum) und den Rahmen neu zeichnen. */
  select(i) {
    this.index = (i + CHARACTERS.length) % CHARACTERS.length;
    const g = this.frames;
    g.clear();
    this.cards.forEach((card, k) => {
      const chosen = k === this.index;
      g.fillStyle(DUSK, chosen ? 1 : 0.55);
      g.fillRoundedRect(card.x, this.top, card.w, card.h, 6);
      g.lineStyle(chosen ? 3 : 1, chosen ? BLOOD : 0xf6e9df, chosen ? 1 : 0.14);
      g.strokeRoundedRect(card.x, this.top, card.w, card.h, 6);
      card.name.setColor(chosen ? BONE : MIST);
    });
  }

  /** Gewählte Figur übernehmen und in die Welt wechseln. */
  begin() {
    chooseCharacter(this.registry, CHARACTERS[this.index]);
    this.scene.start('World');
  }

  update(time) {
    const phase = (time / 1000) * (SPEED / STRIDE);
    this.cards.forEach((card, k) => {
      card.fig.setPose(k === this.index ? walkPose('S', phase, card.motion) : idlePose(time + card.offset));
    });
  }

  /**
   * Im Artefakt kommen die Schriften aus dem Netz und sind beim ersten
   * Zeichnen evtl. noch nicht da. Dann einmal neu aufbauen, sobald sie geladen sind.
   */
  waitForFonts() {
    const fonts = document.fonts;
    if (this.fontsRequested || !fonts || FONTS.every((f) => fonts.check(f))) return;
    this.fontsRequested = true;
    Promise.all(FONTS.map((f) => fonts.load(f))).then(() => {
      if (this.scene.isActive()) this.scene.restart();
    }).catch(() => {});
  }
}
