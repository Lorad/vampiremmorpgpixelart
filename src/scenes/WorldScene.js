import Phaser from 'phaser';
import CharacterRig, { DIRECTIONS } from '../characters/CharacterRig.js';
import { startIdle } from '../characters/idle.js';

export const TILE = 32;

const setHud = (text) => {
  const el = document.getElementById('hud');
  if (el) el.textContent = text;
};

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

  create() {
    const map = this.make.tilemap({ key: 'world' });
    const tiles = map.addTilesetImage('tiles', 'tiles');
    this.map = map;

    // Boden liegt immer ganz unten
    map.createLayer('ground', tiles, 0, 0).setDepth(-100000);

    // 3/4-Ansicht: Alles, was "steht" (Bäume, Figuren), wird nach dem
    // Fußpunkt (y) sortiert. Wer weiter unten steht, wird davor gezeichnet.
    this.trees = map.getObjectLayer('trees').objects.map((obj) => {
      const tree = this.add.image(obj.x, obj.y, 'trees', prop(obj, 'variant', 0));
      tree.setOrigin(TREE.baseX / TREE.width, TREE.baseY / TREE.height);
      tree.setDepth(obj.y);
      return tree;
    });

    // Die Vampirin steht auf der Wiese, nahe am nördlichen Waldrand
    const rig = this.cache.json.get('vampire-rig');
    this.vampire = new CharacterRig(this, 17 * TILE, 9 * TILE, 'vampire', rig, 'S');
    this.vampire.setDepth(this.vampire.y);
    startIdle(this, this.vampire);

    // Q / E: Figur drehen (Vorschau der 8 Richtungen)
    const turn = (step) => {
      const i = DIRECTIONS.indexOf(this.vampire.direction);
      this.vampire.setDirection(DIRECTIONS[(i + step + DIRECTIONS.length) % DIRECTIONS.length]);
    };
    this.input.keyboard.on('keydown-Q', () => turn(-1));
    this.input.keyboard.on('keydown-E', () => turn(1));
    this.input.keyboard.on('keydown-F', () => this.scene.start('Character'));
    setHud('Q / E: Figur drehen · F: Figuren-Ansicht');

    const cam = this.cameras.main;
    cam.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
    this.fitCamera();
    this.scale.on('resize', this.fitCamera, this);
    this.events.once('shutdown', () => this.scale.off('resize', this.fitCamera, this));
  }

  /** Ganzzahliger Zoom (gleich große Pixel), Kamera auf der Figur. */
  fitCamera() {
    const cam = this.cameras.main;
    const { width, height } = this.scale.gameSize;
    const zoom = Math.max(1, Math.floor(Math.min(width / (20 * TILE), height / (12 * TILE))));
    cam.setZoom(zoom);
    cam.centerOn(this.vampire.x, this.vampire.y - 30);
  }
}
