import RiggedSprite from '../characters/RiggedSprite.js';
import { idlePose, walkPose } from '../characters/animations.js';

/** Laufgeschwindigkeit in Pixeln pro Sekunde (≈ 2,5 Kacheln/s). */
export const SPEED = 80;
/** Weg in Pixeln für einen ganzen Laufzyklus (2 Schritte) – passt zur Schrittweite. */
export const STRIDE = 40;

// Bewegungswinkel → Blickrichtung (8 Sektoren à 45°, 0° = rechts, y zeigt nach unten)
const SECTORS = ['E', 'SE', 'S', 'SW', 'W', 'NW', 'N', 'NE'];

/** Blickrichtung zu einem Bewegungsvektor. */
export function directionFor(dx, dy) {
  const sector = Math.round(Math.atan2(dy, dx) / (Math.PI / 4));
  return SECTORS[((sector % 8) + 8) % 8];
}

/**
 * Die eigene Spielfigur: liest WASD/Pfeiltasten, bewegt sich mit Kollision,
 * dreht sich in Laufrichtung und spielt Lauf- bzw. Atem-Animation.
 */
export default class Player {
  /**
   * @param {Phaser.Scene} scene
   * @param {number} x Fußpunkt x
   * @param {number} y Fußpunkt y
   * @param {import('./collision.js').CollisionWorld} collision
   * @param {object} rigData Inhalt von vampire.rig.json
   */
  constructor(scene, x, y, collision, rigData) {
    this.scene = scene;
    this.collision = collision;
    this.x = x;
    this.y = y;
    this.phase = 0;
    this.moving = false;
    this.sprite = new RiggedSprite(scene, x, y, 'vampire', rigData, 'S');
    this.keys = scene.input.keyboard.addKeys({
      up: 'W', down: 'S', left: 'A', right: 'D',
      up2: 'UP', down2: 'DOWN', left2: 'LEFT', right2: 'RIGHT',
    });
    this.sync();
  }

  /** Eingabe als Vektor (-1/0/1 je Achse). */
  readInput() {
    const k = this.keys;
    const right = k.right.isDown || k.right2.isDown;
    const left = k.left.isDown || k.left2.isDown;
    const down = k.down.isDown || k.down2.isDown;
    const up = k.up.isDown || k.up2.isDown;
    return { x: (right ? 1 : 0) - (left ? 1 : 0), y: (down ? 1 : 0) - (up ? 1 : 0) };
  }

  update(time) {
    const input = this.readInput();
    // Echte Zeit seit dem letzten Bild (Phasers geglättetes `delta` hinkt nach
    // Rucklern hinterher); große Pausen nicht als Sprung umsetzen
    const raw = this.scene.game.loop.rawDelta;
    const dt = Math.min(Math.max(raw, 0), 100) / 1000;
    this.moving = false;

    if (input.x || input.y) {
      const len = Math.hypot(input.x, input.y); // diagonal nicht schneller
      const dx = (input.x / len) * SPEED * dt;
      const dy = (input.y / len) * SPEED * dt;
      this.sprite.setDirection(this.facing(directionFor(input.x, input.y), time));

      const next = this.collision.move(this.x, this.y, dx, dy);
      const moved = Math.hypot(next.x - this.x, next.y - this.y);
      this.x = next.x;
      this.y = next.y;
      if (moved > 0.01) {
        this.moving = true;
        this.phase = (this.phase + moved / STRIDE) % 1;
      }
    }

    if (!input.x && !input.y) this.holdSince = null;

    if (this.moving) {
      this.sprite.setPose(walkPose(this.sprite.direction, this.phase));
    } else {
      this.phase = 0.999; // nächster Schritt beginnt wieder mit dem rechten Bein
      this.sprite.setPose(idlePose(time));
    }
    this.sync();
  }

  /**
   * Blickrichtung mit kurzer Toleranz: Lässt man zwei Tasten (z. B. S+A) los,
   * geht nie beide genau gleichzeitig hoch. Damit die Figur dann nicht für
   * einen Moment nach Westen schaut, bleibt die Schrägrichtung 90 ms erhalten.
   */
  facing(wanted, time) {
    const current = this.sprite.direction;
    if (current.length === 2 && wanted.length === 1 && current.includes(wanted)) {
      this.holdSince ??= time;
      if (time - this.holdSince < 90) return current;
    } else {
      this.holdSince = null;
    }
    return wanted;
  }

  /** Anzeige auf ganze Pixel setzen (pixelgenau) und nach Fußpunkt sortieren. */
  sync() {
    this.sprite.setPosition(Math.round(this.x), Math.round(this.y));
    this.sprite.setDepth(this.sprite.y);
  }
}
