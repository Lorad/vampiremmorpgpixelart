import Phaser from 'phaser';

/** Reihenfolge im Uhrzeigersinn, beginnend mit "Blick nach unten" (Süden). */
export const DIRECTIONS = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE'];

/**
 * Eine Figur aus Einzelteilen mit Skelett ("Rig").
 *
 * - Jedes Teil (Kopf, Oberarm, …) ist ein eigenes Bild und hängt an einem
 *   Knochen. Knochen haben einen Elternknochen (z. B. Unterarm → Oberarm).
 * - Für jede der 8 Richtungen gibt es eigene Bilder, Gelenkpunkte und eine
 *   eigene Zeichenreihenfolge (von hinten nach vorne).
 * - Knochen lassen sich drehen und verschieben (setBone / setPose). Kinder
 *   bewegen sich automatisch mit (Vorwärtskinematik).
 * - Der Ursprung des Containers ist der Fußpunkt der Figur.
 *
 * Für pixelgenaue Darstellung wird das Rig nicht direkt angezeigt, sondern
 * von RiggedSprite in eine kleine Textur gezeichnet (addToScene = false).
 */
export default class CharacterRig extends Phaser.GameObjects.Container {
  /**
   * @param {Phaser.Scene} scene
   * @param {number} x Fußpunkt x
   * @param {number} y Fußpunkt y
   * @param {string} textureKey Schlüssel des Texturatlas
   * @param {object} rig Inhalt von *.rig.json
   * @param {string} [direction] Start-Blickrichtung
   * @param {{addToScene?: boolean}} [options]
   */
  constructor(scene, x, y, textureKey, rig, direction = 'S', { addToScene = true } = {}) {
    super(scene, x, y);
    this.rig = rig;
    this.direction = null;
    this.version = 0; // zählt jede sichtbare Änderung (für RiggedSprite)
    this.pose = {};
    for (const bone of Object.keys(rig.bones)) this.pose[bone] = { angle: 0, x: 0, y: 0 };

    this.images = {};
    for (const dir of Object.values(rig.directions)) {
      for (const name of Object.keys(dir.parts)) {
        if (this.images[name]) continue;
        const img = new Phaser.GameObjects.Image(scene, 0, 0, textureKey, dir.parts[name].frame);
        this.images[name] = img;
        this.add(img);
      }
    }
    this.setDirection(direction);
    if (addToScene) scene.add.existing(this);
  }

  /** Wechselt die Blickrichtung ('S', 'SE', 'E', …). */
  setDirection(direction) {
    if (direction === this.direction) return this;
    const dir = this.rig.directions[direction];
    if (!dir) throw new Error(`Unbekannte Richtung: ${direction}`);
    this.direction = direction;

    for (const [name, img] of Object.entries(this.images)) {
      const part = dir.parts[name];
      img.setVisible(Boolean(part));
      if (!part) continue;
      img.setFrame(part.frame, true, false);
      // Drehpunkt des Bildes = Gelenk des Teils
      img.setOrigin((part.pivot[0] - part.x) / part.w, (part.pivot[1] - part.y) / part.h);
    }
    for (const name of dir.order) this.bringToTop(this.images[name]);
    this.updatePose();
    return this;
  }

  /** Dreht/verschiebt einen Knochen relativ zur Grundpose (Winkel in Grad). */
  setBone(bone, values) {
    this.applyBone(bone, values);
    this.updatePose();
    return this;
  }

  /**
   * Setzt mehrere Knochen auf einmal, z. B. ein Animationsbild:
   * { torso: { y: 1 }, thigh_R: { angle: -20 }, … }.
   * Knochen, die nicht genannt werden, gehen in die Grundpose zurück.
   */
  setPose(pose = {}) {
    for (const bone of Object.keys(this.pose)) {
      this.applyBone(bone, { angle: 0, x: 0, y: 0, ...pose[bone] });
    }
    this.updatePose();
    return this;
  }

  /** Setzt alle Knochen auf die Grundpose zurück. */
  resetPose() {
    return this.setPose({});
  }

  applyBone(bone, { angle, x, y } = {}) {
    const p = this.pose[bone];
    if (!p) throw new Error(`Unbekannter Knochen: ${bone}`);
    if (angle !== undefined) p.angle = angle;
    if (x !== undefined) p.x = x;
    if (y !== undefined) p.y = y;
  }

  /** Vorwärtskinematik: Gelenkpositionen und Winkel aller Teile berechnen. */
  updatePose() {
    const dir = this.rig.directions[this.direction];
    const { bones, origin } = this.rig;
    const world = {};

    const solve = (bone) => {
      if (world[bone]) return world[bone];
      const parent = bones[bone];
      const pose = this.pose[bone];
      const pivot = dir.pivots[bone];
      if (!parent) {
        world[bone] = { x: pivot[0] + pose.x, y: pivot[1] + pose.y, angle: pose.angle };
        return world[bone];
      }
      const pw = solve(parent);
      const pp = dir.pivots[parent];
      const rad = Phaser.Math.DegToRad(pw.angle);
      const dx = pivot[0] - pp[0] + pose.x;
      const dy = pivot[1] - pp[1] + pose.y;
      world[bone] = {
        x: pw.x + dx * Math.cos(rad) - dy * Math.sin(rad),
        y: pw.y + dx * Math.sin(rad) + dy * Math.cos(rad),
        angle: pw.angle + pose.angle,
      };
      return world[bone];
    };

    for (const [name, img] of Object.entries(this.images)) {
      if (!dir.parts[name]) continue;
      const w = solve(name);
      img.setPosition(w.x - origin.x, w.y - origin.y);
      img.setAngle(w.angle);
    }
    this.version++;
  }
}
