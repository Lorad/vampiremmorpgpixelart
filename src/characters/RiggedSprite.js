import Phaser from 'phaser';
import CharacterRig from './CharacterRig.js';

// Zeichenfläche: Figur (62×62) plus Rand für gedrehte Arme und Beine
const CANVAS_W = 96;
const CANVAS_H = 80;
// Fußpunkt der Figur auf der Zeichenfläche
const FOOT_X = 48;
const FOOT_Y = 72;

/**
 * Zeigt ein CharacterRig pixelgenau an.
 *
 * Das Rig wird in Originalgröße (1 Pixel = 1 Pixel) in eine kleine Textur
 * gezeichnet; erst diese wird von der Kamera vergrößert. So liegen auch
 * gedrehte Arme und Beine im selben Pixelraster wie der Rest der Welt.
 * Neu gezeichnet wird nur, wenn sich Pose oder Richtung ändern.
 */
export default class RiggedSprite extends Phaser.GameObjects.RenderTexture {
  constructor(scene, x, y, textureKey, rigData, direction = 'S') {
    super(scene, x, y, CANVAS_W, CANVAS_H);
    this.rig = new CharacterRig(scene, 0, 0, textureKey, rigData, direction, {
      addToScene: false,
    });
    this.setOrigin(FOOT_X / CANVAS_W, FOOT_Y / CANVAS_H);
    this.poseKey = '';
    this.drawnVersion = -1;
    scene.add.existing(this);
    this.redraw();
  }

  get direction() {
    return this.rig.direction;
  }

  setDirection(direction) {
    this.rig.setDirection(direction);
    return this.redraw();
  }

  /** Setzt eine Pose (siehe CharacterRig#setPose) und zeichnet bei Bedarf neu. */
  setPose(pose) {
    const key = JSON.stringify(pose);
    if (key !== this.poseKey) {
      this.poseKey = key;
      this.rig.setPose(pose);
    }
    return this.redraw();
  }

  redraw() {
    if (this.drawnVersion === this.rig.version) return this;
    this.drawnVersion = this.rig.version;
    this.clear();
    this.draw(this.rig, FOOT_X, FOOT_Y);
    this.render();
    return this;
  }

  destroy(fromScene) {
    this.rig?.destroy();
    super.destroy(fromScene);
  }
}
