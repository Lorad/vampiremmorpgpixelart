/**
 * Animationen für das Skelett der Figuren.
 *
 * Eine Pose ist ein Objekt { knochen: { angle, x, y } } (Winkel in Grad,
 * Verschiebung in Pixeln, jeweils relativ zur Grundpose). Fehlende Knochen
 * bleiben in der Grundpose.
 *
 * Gehen und Sprinten sind zwei "Gangarten" mit derselben Bewegungslogik und
 * unterschiedlichen Werten (siehe WALK und RUN).
 *
 * `style` passt die Bewegung an eine Figur an (siehe characters/roster.js):
 * style.hair = wie stark die Haare nachschwingen (1 = lange Haare der
 * Vampirin, 0 = kurze Haare, die fest am Kopf sitzen).
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
  hairTrail: 1, // Haare wehen nach hinten (px, Seitenansicht)
  hairLift: 0, // Haare wehen nach hinten (px, Front-/Rück-/Schrägansicht)
  sway: 0.8, // Rock schwingt seitlich (px)
  flight: 0, // Flugphase: so weit hebt der ganze Körper ab (px)
  skirtFlutter: 0, // Rock bleibt in der Flugphase zurück (px)
  pump: 1, // vordere Hand zieht hoch (px, Front-/Rück-/Schrägansicht)
  backHand: 0, // hintere Hand geht nach unten (px)
  inward: 0, // vordere Hand geht zur Körpermitte (px, Front-/Rückansicht)
  shoulderLift: 0, // Schulter des vorderen Arms hebt sich mit (px)
  diagPump: 0, // Schrägansicht: vordere Hand zieht hoch (px)
  armDiagY: 1, // Schrägansicht: Hand folgt der Diagonale auch in der Höhe (1) oder nicht (0)
  twist: 0, // Front-/Rückansicht: vorderer Unterarm dreht zur Körpermitte (Grad)
  backOut: 0, // Front-/Rückansicht: hintere Hand geht nach außen (px)
  bodySway: 0, // Front-/Rückansicht: Oberkörper verlagert sich über das Standbein (px)
  run: false,
};

/**
 * Sprinten: weite Schritte, angewinkelte Arme, Oberkörper nach vorne geneigt,
 * mit Flugphase (der ganze Körper hebt zwischen zwei Schritten kurz ab).
 * Damit der Sprint auch von vorne/hinten und schräg deutlich anders aussieht:
 * hohe Knie, die vordere Hand zieht angewinkelt vor die Brust, der Oberkörper
 * verlagert sich über das Standbein, Haare und Rock schwingen nach.
 */
const RUN = {
  legSwing: 32,
  legBack: 16, // nach hinten weniger, sonst sticht das Bein hinten aus dem Rock
  knee: 40,
  frontStep: 2.6,
  lift: 3, // hohe Knie
  diagStep: { x: 3, y: 2.4 },
  armSwing: 30,
  elbow: 40,
  elbowSwing: 20,
  handRaise: 1,
  diagArm: { x: 3, y: 2.4 },
  lean: 1,
  hairTrail: 2,
  hairLift: 1,
  sway: 1.6,
  flight: 2,
  skirtFlutter: 1,
  pump: 4,
  backHand: 1,
  inward: 2,
  shoulderLift: 1,
  diagPump: 3, // die Hand pumpt senkrecht hoch …
  armDiagY: 0, // … statt der Diagonale nach unten zu folgen
  twist: 25,
  backOut: 1,
  bodySway: 1,
  run: true,
};

/**
 * Höhe von Becken und Oberkörper im Zyklus.
 * Gehen: Oberkörper 1 px tiefer, wenn die Beine weit auseinander stehen.
 * Sprinten: Flugphase – der ganze Körper hebt sich in einem weichen Bogen
 * (bis `flight` px) bei weit gestellten Beinen, beim Aufsetzen federt der
 * Oberkörper 1 px ein.
 */
function bounce(phase, gait) {
  const a = Math.abs(Math.sin(phase * TAU));
  if (!gait.run) return { pelvis: 0, torso: a > 0.9 ? 1 : 0 };
  return { pelvis: -Math.round(gait.flight * a * a), torso: a < 0.3 ? 1 : 0 };
}

/** Gehen. `phase` läuft von 0 bis 1 (2 Schritte); bei 0,25 ist das rechte Bein vorne. */
export function walkPose(direction, phase, style) {
  return gaitPose(direction, phase, WALK, style);
}

/** Sprinten (gleiche Phase wie beim Gehen, damit der Wechsel nahtlos ist). */
export function runPose(direction, phase, style) {
  return gaitPose(direction, phase, RUN, style);
}

function gaitPose(direction, phase, g, style = {}) {
  const { side, front } = VIEW[direction];
  const p = Math.floor((((phase % 1) + 1) % 1) * WALK_FRAMES) / WALK_FRAMES;
  const s = Math.sin(p * TAU); // > 0: rechtes Bein vorne
  const c = Math.cos(p * TAU); // > 0: rechtes Bein schwingt gerade nach vorne
  const dir = Math.sign(side);
  const diagonal = side !== 0 && front !== 0;

  const now = bounce(p, g);
  const before = bounce(p - 1 / WALK_FRAMES, g);
  const sway = Math.round(g.sway * s);
  // Front-/Rückansicht: Oberkörper über das Standbein (rechtes Bein ist in Süd links im Bild)
  const shift = (q) => (side === 0 ? -front * Math.round(g.bodySway * Math.sin(q * TAU)) : 0);
  const shiftNow = shift(p);
  const shiftBefore = shift(p - 1 / WALK_FRAMES);

  // Haare federn einen Takt verzögert nach und wehen beim Laufen nach hinten.
  // Von hinten (Nord, Nordost, Nordwest) ist die Haarmasse fast der ganze Kopf:
  // Dort federt sie höchstens 1 px, sonst rutscht sie sichtbar am Ohr vorbei.
  const lag = (before.pelvis + before.torso) - (now.pelvis + now.torso);
  const flex = style.hair ?? 1;
  const hair = {
    x: Math.round(flex * (-dir * g.hairTrail + (shiftBefore - shiftNow))),
    y: Math.round(flex * ((front < 0 ? Math.max(-1, Math.min(1, lag)) : lag) - Math.sign(front) * g.hairLift)),
  };

  const pose = {
    torso: { x: g.lean * dir + shiftNow, y: now.torso },
    hair_back: hair,
    // Arme schwingen gegengleich zu den Beinen
    ...(diagonal ? diagonalArms(side, front, s, g) : straightArms(side, front, s, g)),
    ...(diagonal ? diagonalLegs(side, front, s, c, g) : straightLegs(side, front, s, c, g)),
    // Der Rock schwingt mit den Schritten und bleibt in der Flugphase etwas zurück
    skirt_front: { x: sway, y: now.pelvis <= -2 ? g.skirtFlutter : 0 },
    skirt_back: { x: sway, y: now.pelvis <= -2 ? g.skirtFlutter : 0 },
  };
  // Von hinten liegt die Strähne am Gesichtsrand (hair_front) hinter dem Kopf
  // und gehört zur Haarmasse: Sie muss mitgehen, sonst reißt eine Lücke auf.
  if (front < 0) pose.hair_front = { ...hair };
  if (now.pelvis) pose.pelvis = { y: now.pelvis };
  return pose;
}

/**
 * Arme geradeaus: In der Seitenansicht (Ost/West) pendeln sie an der Schulter,
 * der Unterarm knickt beim Vorschwingen ein (beim Sprinten dauerhaft
 * angewinkelt). In Front-/Rückansicht hebt sich die Hand beim Vorschwingen.
 */
function straightArms(side, front, s, g) {
  // Front-/Rückansicht: vordere Hand zieht im Bogen hoch (beim Sprinten auch
  // zur Körpermitte, der Unterarm dreht dabei ein = angewinkelter Arm vor der
  // Brust), hintere Hand geht nach unten und außen. Der rechte Arm ist im Bild
  // links (Süd) bzw. rechts (Nord) – "zur Mitte" ist also ±front.
  // forward: +1 = Arm ganz vorne, -1 = ganz hinten
  const hand = (forward, inward) => (front === 0 ? {} : {
    angle: -inward * g.twist * Math.max(0, forward),
    x: (Math.round(g.inward * Math.max(0, forward)) - Math.round(g.backOut * Math.max(0, -forward))) * inward,
    y: -g.handRaise - Math.round(g.pump * Math.max(0, forward))
      + Math.round(g.backHand * Math.max(0, -forward)),
  });
  const shoulder = (forward) => (front === 0 ? 0 : -Math.round(g.shoulderLift * Math.max(0, forward)));
  const inward = Math.sign(front);
  return {
    // rechter Arm ist vorne, wenn das linke Bein vorne ist (s < 0)
    upper_arm_R: { angle: side * g.armSwing * s, y: shoulder(-s) },
    forearm_R: { angle: -side * (g.elbow + g.elbowSwing * Math.max(0, -s)), ...hand(-s, inward) },
    upper_arm_L: { angle: -side * g.armSwing * s, y: shoulder(s) },
    forearm_L: { angle: -side * (g.elbow + g.elbowSwing * Math.max(0, s)), ...hand(s, -inward) },
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
  const toRight = Math.sign(side); // +1: vorne ist im Bild rechts
  const toCamera = Math.sign(front); // +1: vorne ist im Bild unten
  const arm = (amount) => {
    const along = (part) => ({
      x: Math.round(g.diagArm.x * amount * part) * toRight,
      y: g.armDiagY * Math.round(g.diagArm.y * amount * part) * toCamera,
    });
    const elbow = along(0.5);
    const hand = along(1);
    // Sprinten: vordere Hand pumpt hoch, hintere geht nach unten
    elbow.y -= Math.round(g.shoulderLift * Math.max(0, amount));
    hand.y += -g.handRaise - Math.round(g.diagPump * Math.max(0, amount))
      + Math.round(g.backHand * Math.max(0, -amount));
    return [elbow, { x: hand.x - elbow.x, y: hand.y - elbow.y }];
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
