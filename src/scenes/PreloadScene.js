import Phaser from 'phaser';
import { asset } from '../assets.js';
import { CHARACTERS, rigKey } from '../characters/roster.js';

/** Lädt alle Grafiken einmal und startet dann die gewünschte Szene. */
export default class PreloadScene extends Phaser.Scene {
  constructor() {
    super('Preload');
  }

  preload() {
    this.load.image('tiles', asset('assets/tilesets/tiles.png'));
    this.load.spritesheet('trees', asset('assets/sprites/trees.png'), { frameWidth: 64, frameHeight: 96 });
    this.load.tilemapTiledJSON('world', asset('assets/maps/world.json'));
    for (const c of CHARACTERS) {
      this.load.atlas(c.file, asset(`assets/characters/${c.file}.png`),
        asset(`assets/characters/${c.file}.json`));
      this.load.json(rigKey(c), asset(`assets/characters/${c.file}.rig.json`));
    }
  }

  create() {
    // Start mit der Figurenwahl; …/#figur öffnet direkt die Figuren-Ansicht,
    // …/#welt direkt die Welt (mit der zuletzt gewählten Figur)
    const start = { '#figur': 'Character', '#welt': 'World' }[window.location.hash] ?? 'Select';
    this.scene.start(start);
  }
}
