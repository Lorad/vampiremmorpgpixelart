import Phaser from 'phaser';

export const TILE = 32;

// Muss zu tools/generate-world.mjs passen
const TREE = { width: 64, height: 96, baseX: 32, baseY: 90 };

/** Liest eine Tiled-Eigenschaft (Tiled speichert sie als Liste). */
function prop(obj, name, fallback) {
  const props = obj.properties;
  if (Array.isArray(props)) return props.find((p) => p.name === name)?.value ?? fallback;
  return props?.[name] ?? fallback;
}

export default class WorldScene extends Phaser.Scene {
  constructor() {
    super('World');
  }

  preload() {
    this.load.image('tiles', 'assets/tilesets/tiles.png');
    this.load.spritesheet('trees', 'assets/sprites/trees.png', {
      frameWidth: TREE.width,
      frameHeight: TREE.height,
    });
    this.load.tilemapTiledJSON('world', 'assets/maps/world.json');
  }

  create() {
    const map = this.make.tilemap({ key: 'world' });
    const tiles = map.addTilesetImage('tiles', 'tiles');
    this.map = map;

    // Boden liegt immer ganz unten
    map.createLayer('ground', tiles, 0, 0).setDepth(-100000);

    // 3/4-Ansicht: Alles, was "steht" (Bäume, später Figuren), wird nach dem
    // Fußpunkt (y) sortiert. Wer weiter unten steht, wird davor gezeichnet.
    this.trees = map.getObjectLayer('trees').objects.map((obj) => {
      const tree = this.add.image(obj.x, obj.y, 'trees', prop(obj, 'variant', 0));
      tree.setOrigin(TREE.baseX / TREE.width, TREE.baseY / TREE.height);
      tree.setDepth(obj.y);
      return tree;
    });

    this.fitCamera();
    this.scale.on('resize', this.fitCamera, this);
  }

  /**
   * Zeigt die ganze Welt. Ganzzahliger Zoom, damit jedes Pixel gleich groß
   * bleibt. Sobald es eine Spielfigur gibt, folgt die Kamera ihr stattdessen.
   */
  fitCamera() {
    const cam = this.cameras.main;
    const { width, height } = this.scale.gameSize;
    const fit = Math.min(width / this.map.widthInPixels, height / this.map.heightInPixels);
    cam.setZoom(fit >= 1 ? Math.floor(fit) : fit);
    cam.centerOn(this.map.widthInPixels / 2, this.map.heightInPixels / 2);
  }
}
