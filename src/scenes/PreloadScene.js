import Phaser from 'phaser';
import { asset } from '../assets.js';

/** Lädt alle Grafiken einmal und startet dann die gewünschte Szene. */
export default class PreloadScene extends Phaser.Scene {
  constructor() {
    super('Preload');
  }

  preload() {
    this.load.image('tiles', asset('assets/tilesets/tiles.png'));
    this.load.spritesheet('trees', asset('assets/sprites/trees.png'), { frameWidth: 64, frameHeight: 96 });
    this.load.tilemapTiledJSON('world', asset('assets/maps/world.json'));
    this.load.atlas('vampire', asset('assets/characters/vampire.png'),
      asset('assets/characters/vampire.json'));
    this.load.json('vampire-rig', asset('assets/characters/vampire.rig.json'));
  }

  create() {
    // Adresse …/#figur öffnet direkt die Figuren-Ansicht
    this.scene.start(window.location.hash === '#figur' ? 'Character' : 'World');
  }
}
