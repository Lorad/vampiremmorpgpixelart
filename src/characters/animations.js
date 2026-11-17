/**
 * Animationen für das Skelett der Figuren.
 *
 * Eine Pose ist ein Objekt { knochen: { angle, x, y } } (Winkel in Grad,
 * Verschiebung in Pixeln, jeweils relativ zur Grundpose). Fehlende Knochen
 * bleiben in der Grundpose.
 *
 * Gehen und Sprinten sind zwei "Gangarten" mit derselben Bewegungslogik und
 * unterschiedlichen Werten (siehe WALK und RUN).
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

/** Gehen: ruhige Schritte, Körper sinkt bei weit gestellten Beinen um 1 px. */
const WALK = {
  legSwing: 22, // Hüftdrehung nach vorne in der Seitenansicht (Grad)
  legBack: 22, // Hüftdrehung nach hinten (Grad)
  knee: 30, // Kniebeugung beim Durchschwingen (Grad)
  frontStep: 1.4, // Schritt vor/zurück in Front-/Rückansicht (px)
  lift: 1, // Fuß anheben beim Durchschwingen (px)
  diagStep: { x: 2, y: 1.6 }, // Schritt entlang der Diagonale (px)
  armSwing: 18, // Schulterdrehung in der Seitenansicht (Grad)
  elbow: 0, // dauerhaft angewinkelter Unterarm (Grad)
  elbowSwing: 12, // zusätzliches Einknicken beim Vorschwingen (Grad)
  handRaise: 0, // Hände dauerhaft höher (px, Front-/Schrägansicht)
  diagArm: { x: 2, y: 1.6 },
  lean: 0, // Oberkörper in Laufrichtung geneigt (px)
  hairTrail: 1, // Haare wehen nach hinten (px)
  sway: 0.8, // Rock schwingt seitlich (px)
  run: false,
};

/**
 * Sprinten: weite Schritte, angewinkelte Arme, Oberkörper nach vorne geneigt,
 * mit Flugphase (der ganze Körper hebt zwischen zwei Schritten kurz ab).
 */
const RUN = {
  legSwing: 32,
  legBack: 16, // nach hinten weniger, sonst sticht das Bein hinten aus dem Rock
  knee: 40,
  frontStep: 2.2,
  lift: 2,
  diagStep: { x: 3, y: 2.4 },
  armSwing: 30,
  elbow: 40,
  elbowSwing: 20,
  handRaise: 1,
  diagArm: { x: 3, y: 2.4 },
  lean: 1,
  hairTrail: 2,
  sway: 1.4,
  run: true,
};

/**
 * Höhe von Becken und Oberkörper im Zyklus.
 * Gehen: Oberkörper 1 px tiefer, wenn die Beine weit auseinander stehen.
 * Sprinten: Flugphase (Becken 1 px höher) bei weit gestellten Beinen,
 * beim Aufsetzen federt der Oberkörper 1 px ein.
 */
function bounce(phase, gait) {
  const a = Math.abs(Math.sin(phase * TAU));
  if (!gait.run) return { pelvis: 0, torso: a > 0.9 ? 1 : 0 };
  return { pelvis: a > 0.9 ? -1 : 0, torso: a < 0.3 ? 1 : 0 };
}

/** Gehen. `phase` läuft von 0 bis 1 (2 Schritte); bei 0,25 ist das rechte Bein vorne. */
export function walkPose(direction, phase) {
  return gaitPose(direction, phase, WALK);
}

/** Sprinten (gleiche Phase wie beim Gehen, damit der Wechsel nahtlos ist). */
export function runPose(direction, phase) {
  return gaitPose(direction, phase, RUN);
}

function gaitPose(direction, phase, g) {
  const { side, front } = VIEW[direction];
  const p = Math.floor((((phase % 1) + 1) % 1) * WALK_FRAMES) / WALK_FRAMES;
  const s = Math.sin(p * TAU); // > 0: rechtes Bein vorne
  const c = Math.cos(p * TAU); // > 0: rechtes Bein schwingt gerade nach vorne
  const dir = Math.sign(side);
  const diagonal = side !== 0 && front !== 0;

  const now = bounce(p, g);
  const before = bounce(p - 1 / WALK_FRAMES, g);
  const sway = Math.round(g.sway * s);

  const pose = {
    torso: { x: g.lean * dir, y: now.torso },
    // Haare federn einen Takt verzögert nach und wehen beim Seitwärtslaufen nach hinten
    hair_back: {
      x: -dir * g.hairTrail,
      y: (before.pelvis + before.torso) - (now.pelvis + now.torso),
    },
    // Arme schwingen gegengleich zu den Beinen
    ...(diagonal ? diagonalArms(side, front, s, g) : straightArms(side, front, s, g)),
    ...(diagonal ? diagonalLegs(side, front, s, c, g) : straightLegs(side, front, s, c, g)),
    // Der Rock schwingt mit den Schritten
    skirt_front: { x: sway },
    skirt_back: { x: sway },
  };
  if (now.pelvis) pose.pelvis = { y: now.pelvis };
  return pose;
}

/**
 * Arme geradeaus: In der Seitenansicht (Ost/West) pendeln sie an der Schulter,
 * der Unterarm knickt beim Vorschwingen ein (beim Sprinten dauerhaft
 * angewinkelt). In Front-/Rückansicht hebt sich die Hand beim Vorschwingen.
 */
function straightArms(side, front, s, g) {
  const raised = (forward) => (front !== 0 ? -g.handRaise - (forward ? 1 : 0) : 0);
  return {
    upper_arm_R: { angle: side * g.armSwing * s },
    forearm_R: {
      angle: -side * (g.elbow + g.elbowSwing * Math.max(0, -s)),
      y: raised(s < -0.7),
    },
    upper_arm_L: { angle: -side * g.armSwing * s },
    forearm_L: {
      angle: -side * (g.elbow + g.elbowSwing * Math.max(0, s)),
      y: raised(s > 0.7),
    },
  };
}

/**
 * Schritt entlang der Laufrichtung im Bild für die Schrägansichten.
 * amount: +1 = ganz vorne, -1 = ganz hinten.
 */
function diagonalStep(side, front, size) {
  const toRight = Math.sign(side); // +1: vorne ist im Bild rechts
  const toCamera = Math.sign(front); // +1: vorne ist im Bild unten
  return (amount) => ({
    x: Math.round(size.x * amount) * toRight,
    y: Math.round(size.y * amount) * toCamera,
  });
}

/**
 * Arme schräg: Statt seitlich an der Schulter zu pendeln, schwingen Unterarm
 * und Hand entlang der Laufrichtung vor und zurück (bei Südost nach rechts
 * unten bzw. links oben). Der Oberarm geht nur halb mit, damit die Schulter
 * an ihrem Platz bleibt. Ohne Drehung bleiben die Ärmel pixelgenau.
 */
function diagonalArms(side, front, s, g) {
  const step = diagonalStep(side, front, g.diagArm);
  const arm = (amount) => {
    const hand = step(amount);
    const elbow = step(amount / 2);
    return [elbow, { x: hand.x - elbow.x, y: hand.y - elbow.y - g.handRaise }];
  };
  const [upperR, foreR] = arm(-s); // rechter Arm ist vorne, wenn das linke Bein vorne ist
  const [upperL, foreL] = arm(s);
  return { upper_arm_R: upperR, forearm_R: foreR, upper_arm_L: upperL, forearm_L: foreL };
}

/**
 * Beine geradeaus: In der Seitenansicht (Ost/West) schwingen sie an der Hüfte
 * und das Knie knickt beim Durchschwingen ein. In Front-/Rückansicht wird der
 * Fuß nach vorne/hinten gesetzt (im Bild tiefer/höher) und angehoben.
 */
function straightLegs(side, front, s, c, g) {
  // amount > 0: Bein vorne, < 0: hinten (nach hinten schwingt es weniger weit)
  const swing = (amount) => -side * (amount > 0 ? g.legSwing : g.legBack) * amount;
  const thighR = swing(s);
  const thighL = swing(-s);
  const shinR = side * g.knee * Math.max(0, c);
  const shinL = side * g.knee * Math.max(0, -c);
  const stepR = Math.round(front * g.frontStep * s) - (front !== 0 && c > 0.5 ? g.lift : 0);
  const stepL = Math.round(-front * g.frontStep * s) - (front !== 0 && c < -0.5 ? g.lift : 0);
  return {
    thigh_R: { angle: thighR, y: stepR },
    shin_R: { angle: shinR },
    foot_R: { angle: -(thighR + shinR) }, // Fuß bleibt waagerecht
    thigh_L: { angle: thighL, y: stepL },
    shin_L: { angle: shinL },
    foot_L: { angle: -(thighL + shinL) },
  };
}

/**
 * Beine schräg (Südost, Südwest, Nordost, Nordwest): Eine Drehung in der
 * Bildebene würde den Fuß nur seitlich schwingen lassen. Stattdessen wird das
 * ganze Bein entlang der Laufrichtung vor- und zurückgesetzt – bei Südost
 * also nach rechts unten bzw. links oben – und beim Durchschwingen angehoben.
 * Ohne Drehung bleiben die Füße exakt in ihrer Richtung und pixelgenau.
 */
function diagonalLegs(side, front, s, c, g) {
  const step = diagonalStep(side, front, g.diagStep);
  // Der Oberschenkel geht nur halb mit (sonst blitzt im Rockschlitz viel Haut
  // auf), Schienbein und Stiefel machen den Rest des Schritts.
  const leg = (amount, lift) => {
    const total = step(amount);
    const thigh = step(amount / 2);
    return [thigh, { x: total.x - thigh.x, y: total.y - thigh.y - lift }];
  };
  const [thighR, shinR] = leg(s, c > 0.5 ? g.lift : 0);
  const [thighL, shinL] = leg(-s, c < -0.5 ? g.lift : 0);
  return { thigh_R: thighR, shin_R: shinR, thigh_L: thighL, shin_L: shinL };
}

/** Stehen: ruhiges Atmen (Oberkörper alle 0,7 s um 1 px auf und ab). */
export function idlePose(timeMs, period = 1400) {
  const down = Math.floor(timeMs / (period / 2)) % 2 === 1;
  return { torso: { y: down ? 1 : 0 } };
}
