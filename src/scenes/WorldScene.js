import Phaser from 'phaser';
import Player from '../world/Player.js';
import { CollisionWorld } from '../world/collision.js';

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
      const img = this.add.image(obj.x, obj.y, 'trees', prop(obj, 'variant', 0));
      img.setOrigin(TREE.baseX / TREE.width, TREE.baseY / TREE.height);
      img.setDepth(obj.y);
      // Umriss der Baumkrone (ohne Stamm und Schatten), fürs Durchsichtig-Werden
      const left = obj.x - TREE.baseX;
      const top = obj.y - TREE.baseY;
      return { img, base: obj.y, x0: left + 4, x1: left + TREE.width - 4, y0: top + 2, y1: top + 62 };
    });

    // Kollision aus derselben Karte (Baumstämme + Wiesenrand)
    const collision = CollisionWorld.fromTiledMap(this.cache.tilemap.get('world').data);

    // Die Vampirin startet auf der Wiese, nahe am nördlichen Waldrand
    this.player = new Player(this, 17 * TILE, 9 * TILE, collision,
      this.cache.json.get('vampire-rig'));

    this.input.keyboard.on('keydown-F', () => this.scene.start('Character'));
    setHud('WASD / Pfeiltasten: laufen · F: Figuren-Ansicht');

    // Kamera folgt der Figur (auf ganze Pixel gerundet, ohne Nachziehen = kein Zittern)
    const cam = this.cameras.main;
    cam.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
    cam.startFollow(this.player.sprite, true);
    cam.setFollowOffset(0, 28); // Körpermitte statt Füße in die Bildmitte
    this.updateZoom();
    this.scale.on('resize', this.updateZoom, this);
    this.events.once('shutdown', () => this.scale.off('resize', this.updateZoom, this));
  }

  update(time, delta) {
    this.player.update(time, delta);
    this.fadeTreesInFront(delta);
  }

  /**
   * Bäume, die vor der Figur stehen und sie verdecken, werden halbdurchsichtig,
   * damit man die Figur im Wald nicht aus den Augen verliert.
   */
  fadeTreesInFront(delta) {
    const { x, y } = this.player.sprite;
    // ungefährer Körper der Figur (Fußpunkt unten Mitte)
    const body = { x0: x - 14, x1: x + 14, y0: y - 56, y1: y - 2 };
    const k = Math.min(1, delta / 120); // weiches Ein-/Ausblenden
    for (const t of this.trees) {
      const covers = t.base > y && t.x0 < body.x1 && t.x1 > body.x0 && t.y0 < body.y1 && t.y1 > body.y0;
      const target = covers ? 0.4 : 1;
      if (t.img.alpha !== target) {
        const a = t.img.alpha + (target - t.img.alpha) * k;
        t.img.setAlpha(Math.abs(a - target) < 0.02 ? target : a);
      }
    }
  }

  /**
   * Ganzzahliger Zoom, damit alle Pixel gleich groß bleiben: etwa 20×12 Kacheln
   * sichtbar, aber nie mehr als die Karte groß ist (sonst schwarze Ränder).
   */
  updateZoom() {
    const { width, height } = this.scale.gameSize;
    const ideal = Math.round(Math.min(width / (20 * TILE), height / (12 * TILE)));
    const fill = Math.ceil(Math.max(width / this.map.widthInPixels, height / this.map.heightInPixels));
    this.cameras.main.setZoom(Math.max(1, ideal, fill));
  }
}
