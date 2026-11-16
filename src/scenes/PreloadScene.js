import Phaser from 'phaser';

/** Lädt alle Grafiken einmal und startet dann die gewünschte Szene. */
export default class PreloadScene extends Phaser.Scene {
  constructor() {
    super('Preload');
  }

  preload() {
    this.load.image('tiles', 'assets/tilesets/tiles.png');
    this.load.spritesheet('trees', 'assets/sprites/trees.png', { frameWidth: 64, frameHeight: 96 });
    this.load.tilemapTiledJSON('world', 'assets/maps/world.json');
    this.load.atlas('vampire', 'assets/characters/vampire.png', 'assets/characters/vampire.json');
    this.load.json('vampire-rig', 'assets/characters/vampire.rig.json');
  }

  create() {
    // Adresse …/#figur öffnet direkt die Figuren-Ansicht
    this.scene.start(window.location.hash === '#figur' ? 'Character' : 'World');
  }
}
