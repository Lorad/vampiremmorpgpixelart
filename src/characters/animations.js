/**
 * Animationen für das Skelett der Figuren.
 *
 * Eine Pose ist ein Objekt { knochen: { angle, x, y } } (Winkel in Grad,
 * Verschiebung in Pixeln, jeweils relativ zur Grundpose). Fehlende Knochen
 * bleiben in der Grundpose.
 */

const TAU = Math.PI * 2;

/** Bilder pro Laufzyklus (2 Schritte). Feste Bilder statt fließender Bewegung = Pixel-Look. */
export const WALK_FRAMES = 8;

/**
 * Wie stark die Bewegung in jeder Richtung seitlich (im Bild links/rechts)
 * bzw. in die Tiefe (zur Kamera hin / von ihr weg) wirkt.
 * side: +1 = Blick nach rechts, -1 = nach links. front: +1 = zur Kamera, -1 = weg.
 */
const VIEW = {
  E: { side: 1, front: 0 },
  W: { side: -1, front: 0 },
  S: { side: 0, front: 1 },
  N: { side: 0, front: -1 },
  SE: { side: 0.6, front: 0.6 },
  SW: { side: -0.6, front: 0.6 },
  NE: { side: 0.6, front: -0.6 },
  NW: { side: -0.6, front: -0.6 },
};

/** Körper 1 px tiefer, wenn beide Beine weit auseinander stehen. */
const bob = (phase) => (Math.abs(Math.sin(phase * TAU)) > 0.9 ? 1 : 0);

/**
 * Laufzyklus. `phase` läuft von 0 bis 1 (ein ganzer Zyklus = 2 Schritte).
 * Bei phase 0,25 ist das rechte Bein vorne, bei 0,75 das linke.
 */
export function walkPose(direction, phase) {
  const { side, front } = VIEW[direction];
  const p = Math.floor((((phase % 1) + 1) % 1) * WALK_FRAMES) / WALK_FRAMES;
  const s = Math.sin(p * TAU); // > 0: rechtes Bein vorne
  const c = Math.cos(p * TAU); // > 0: rechtes Bein schwingt gerade nach vorne
  const dir = Math.sign(side);
  const sideAmount = Math.abs(side);

  // Beine: in der Seitenansicht schwingen sie (Drehung an der Hüfte, Knie
  // knickt beim Durchschwingen ein), in Front-/Rückansicht wird der Fuß
  // nach vorne/hinten gesetzt (im Bild tiefer/höher) und kurz angehoben.
  const thighR = -side * 22 * s;
  const thighL = side * 22 * s;
  const shinR = dir * sideAmount * 30 * Math.max(0, c);
  const shinL = dir * sideAmount * 30 * Math.max(0, -c);
  const stepR = Math.round(front * 1.4 * s) - (front !== 0 && c > 0.5 ? 1 : 0);
  const stepL = Math.round(-front * 1.4 * s) - (front !== 0 && c < -0.5 ? 1 : 0);

  const torso = bob(p);
  const sway = Math.round(0.8 * s);

  return {
    torso: { y: torso },
    // Haare federn einen Takt verzögert nach und wehen beim Seitwärtslaufen nach hinten
    hair_back: { x: -dir, y: bob(p - 1 / WALK_FRAMES) - torso },
    // Arme schwingen gegengleich zu den Beinen
    upper_arm_R: { angle: side * 18 * s },
    forearm_R: { angle: -side * 12 * Math.max(0, -s), y: front !== 0 && s < -0.7 ? -1 : 0 },
    upper_arm_L: { angle: -side * 18 * s },
    forearm_L: { angle: -side * 12 * Math.max(0, s), y: front !== 0 && s > 0.7 ? -1 : 0 },
    thigh_R: { angle: thighR, y: stepR },
    shin_R: { angle: shinR },
    foot_R: { angle: -(thighR + shinR) }, // Fuß bleibt waagerecht
    thigh_L: { angle: thighL, y: stepL },
    shin_L: { angle: shinL },
    foot_L: { angle: -(thighL + shinL) },
    // Der Rock schwingt mit den Schritten
    skirt_front: { x: sway },
    skirt_back: { x: sway },
  };
}

/** Stehen: ruhiges Atmen (Oberkörper alle 0,7 s um 1 px auf und ab). */
export function idlePose(timeMs, period = 1400) {
  const down = Math.floor(timeMs / (period / 2)) % 2 === 1;
  return { torso: { y: down ? 1 : 0 } };
}
