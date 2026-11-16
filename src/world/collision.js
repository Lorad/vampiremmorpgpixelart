/**
 * Bewegung und Kollision – reines JavaScript ohne Phaser, damit später auch
 * ein Spielserver genau dieselbe Logik verwenden kann.
 *
 * Alles wird über kleine Rechtecke am Boden gerechnet (3/4-Ansicht):
 * - die Füße einer Figur (FEET),
 * - der Stammfuß eines Baumes (TRUNK),
 * - Sperr-Rechtecke aus der Kartenebene "collision".
 * Positionen sind immer Fußpunkte (Mitte unten).
 */

/** Fußbox einer Figur (Breite/Höhe in Pixeln, über dem Fußpunkt). */
export const FEET = { w: 14, h: 6 };
/** Kollisionsbox eines Baumstamms (über dem Stammfuß). */
export const TRUNK = { w: 14, h: 8 };
/** So weit (in Pixeln) wird an Ecken seitlich ausgewichen. */
const CORNER_ASSIST = 5;

/** Rechteck einer Box mit Fußpunkt (x, y). */
export function boxAt(x, y, size) {
  return { x: x - size.w / 2, y: y - size.h, w: size.w, h: size.h };
}

export function overlaps(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

export class CollisionWorld {
  /** @param {{x:number,y:number,w:number,h:number}[]} rects Sperr-Rechtecke */
  constructor(rects) {
    this.rects = rects;
  }

  /** Baut die Kollisionswelt aus einer Karte im Tiled-JSON-Format. */
  static fromTiledMap(map) {
    const rects = [];
    for (const layer of map.layers) {
      if (layer.type !== 'objectgroup') continue;
      for (const obj of layer.objects) {
        if (layer.name === 'trees') rects.push(boxAt(obj.x, obj.y, TRUNK));
        if (layer.name === 'collision') {
          rects.push({ x: obj.x, y: obj.y, w: obj.width, h: obj.height });
        }
      }
    }
    return new CollisionWorld(rects);
  }

  /** Ist die Fußbox an Position (x, y) frei? */
  isFree(x, y, size = FEET) {
    const box = boxAt(x, y, size);
    for (const r of this.rects) if (overlaps(box, r)) return false;
    return true;
  }

  /**
   * Bewegt eine Figur um (dx, dy) und rutscht an Hindernissen entlang:
   * erst waagerecht, dann senkrecht, in Schritten von höchstens 1 Pixel
   * (so bleibt man bündig vor einem Hindernis stehen). Läuft man genau
   * gegen eine Ecke, weicht die Figur seitlich aus und gleitet vorbei.
   */
  move(x, y, dx, dy, size = FEET) {
    let px = x;
    let py = y;
    const step = (ax, ay) => {
      const n = Math.ceil(Math.max(Math.abs(ax), Math.abs(ay)));
      for (let i = 0; i < n; i++) {
        const nx = px + ax / n;
        const ny = py + ay / n;
        if (!this.isFree(nx, ny, size)) return false;
        px = nx;
        py = ny;
      }
      return true;
    };

    const okX = step(dx, 0);
    const okY = step(0, dy);
    if (!okX && dy === 0) this.cornerAssist(Math.sign(dx), 0, size, px, py, (a, b) => { px = a; py = b; });
    if (!okY && dx === 0) this.cornerAssist(0, Math.sign(dy), size, px, py, (a, b) => { px = a; py = b; });
    return { x: px, y: py };
  }

  cornerAssist(sx, sy, size, px, py, set) {
    for (let k = 1; k <= CORNER_ASSIST; k++) {
      for (const d of [-1, 1]) {
        const ox = sy !== 0 ? d * k : 0; // senkrecht unterwegs → nach links/rechts ausweichen
        const oy = sx !== 0 ? d * k : 0; // waagerecht unterwegs → nach oben/unten ausweichen
        const nudgeX = px + Math.sign(ox);
        const nudgeY = py + Math.sign(oy);
        if (this.isFree(px + ox + sx, py + oy + sy, size) && this.isFree(nudgeX, nudgeY, size)) {
          set(nudgeX, nudgeY);
          return;
        }
      }
    }
  }
}
