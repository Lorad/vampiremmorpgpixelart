// Erzeugt die Grafiken und die Karte der Welt (3/4-Ansicht, "schräg von oben").
//
//   npm run generate:world
//
// Ausgabe:
//   public/assets/tilesets/tiles.png  – Bodenkacheln (32×32)
//   public/assets/sprites/trees.png   – Bäume als Sprites (64×96 pro Baum)
//   public/assets/maps/world.json     – Karte im Format des Map-Editors "Tiled"
//
// ACHTUNG: Überschreibt diese Dateien. Wer die Karte später von Hand in
// Tiled bearbeitet, sollte dieses Skript nicht mehr ausführen.
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { PixelImage, hex, mulberry32 } from './lib/png.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SEED = 1337;

const TILE = 32;
const MAP_W = 34; // Breite in Kacheln
const MAP_H = 24; // Höhe in Kacheln
// Freie Wiese in der Mitte (in Kacheln), drumherum Wald
const MEADOW = { x0: 4, y0: 5, x1: 30, y1: 21 };

const TREE_W = 64;
const TREE_H = 96;
const TREE_VARIANTS = 3;
// Stammfuß im Baum-Sprite (= Ursprung beim Platzieren, für die Tiefensortierung)
const TREE_BASE = { x: 32, y: 90 };

const C = {
  grassDeep: hex('#2f4a2c'),
  grassDark: hex('#3a5a34'),
  grassBase: hex('#46693c'),
  grassLight: hex('#567b48'),
  grassHi: hex('#6b9152'),
  floorBase: hex('#26361f'),
  floorDark: hex('#1d2a18'),
  floorLight: hex('#30432a'),
  flowerWhite: hex('#e6e2cf'),
  flowerCenter: hex('#d9b24a'),
  roseRed: hex('#a3202d'),
  roseDark: hex('#5e121b'),
  roseHi: hex('#d0414a'),
  leafOutline: hex('#0e2219'),
  leaf: [hex('#183526'), hex('#24503a'), hex('#367048'), hex('#4f8f55')],
  barkOutline: hex('#1a110b'),
  bark: [hex('#2b1d14'), hex('#4a3222'), hex('#6b4a30')],
  shadow: [11, 23, 16, 110],
};

// Index im Tileset (0-basiert)
const TILES = {
  GRASS: 0,
  GRASS_TUFTS: 1,
  GRASS_DENSE: 2,
  GRASS_FLOWERS: 3,
  GRASS_ROSES: 4,
  FOREST_FLOOR: 5,
  // Übergänge Waldboden → Wiese (Waldboden liegt auf der genannten Seite)
  EDGE_N: 6,
  EDGE_S: 7,
  EDGE_W: 8,
  EDGE_E: 9,
};
const TILE_COUNT = 10;

// 4×4-Bayer-Matrix für gleichmäßiges Pixel-Dithering
const BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]];

// ---------------------------------------------------------------- Bodenkacheln

function stamp(img, x, y, pattern, colors) {
  const rows = pattern.split('|');
  const h = rows.length;
  const w = rows[0].length;
  for (let j = 0; j < h; j++) {
    for (let i = 0; i < w; i++) {
      const ch = rows[j][i];
      if (ch !== '.') img.set(x + i - (w >> 1), y + j - (h >> 1), colors[ch]);
    }
  }
}

const GRASS = { base: C.grassBase, dark: C.grassDark, light: C.grassLight, speck: 0.06 };
const FLOOR = { base: C.floorBase, dark: C.floorDark, light: C.floorLight, speck: 0.12 };

/**
 * Zeichnet eine Bodenkachel. `grassAmount(x, y)` (0..1) mischt per Dithering
 * zwischen Waldboden (0) und Gras (1); ohne Angabe ist alles `palette`.
 */
function drawGround(img, ox, oy, rng, { palette = GRASS, grassAmount, tufts = 0, flowers = 0, roses = 0, speck }) {
  const isGrass = (x, y) => !grassAmount || grassAmount(x, y) * 16 > BAYER[y % 4][x % 4];
  for (let y = 0; y < TILE; y++) {
    for (let x = 0; x < TILE; x++) {
      const pal = grassAmount ? (isGrass(x, y) ? GRASS : FLOOR) : palette;
      const s = speck ?? pal.speck;
      const r = rng();
      img.set(ox + x, oy + y, r < s / 2 ? pal.dark : r < s ? pal.light : pal.base);
    }
  }
  // Deko bleibt 3 px vom Rand weg → Kacheln sind nahtlos; nur auf Gras
  const pos = () => {
    for (;;) {
      const x = 3 + Math.floor(rng() * (TILE - 6));
      const y = 3 + Math.floor(rng() * (TILE - 6));
      if (!grassAmount || grassAmount(x, y) > 0.9) return [ox + x, oy + y];
    }
  };
  for (let i = 0; i < tufts; i++) {
    stamp(img, ...pos(), 'h.h.h|l.l.l|ldldl|.d.d.', { h: C.grassHi, l: C.grassLight, d: C.grassDeep });
  }
  for (let i = 0; i < flowers; i++) {
    stamp(img, ...pos(), '.w.|wyw|.w.|.d.', { w: C.flowerWhite, y: C.flowerCenter, d: C.grassDeep });
  }
  for (let i = 0; i < roses; i++) {
    stamp(img, ...pos(), '.r.|rhr|.R.|.d.', { r: C.roseRed, h: C.roseHi, R: C.roseDark, d: C.grassDeep });
  }
}

function buildTileset() {
  const img = new PixelImage(TILE * TILE_COUNT, TILE);
  const rng = mulberry32(SEED);
  const at = (i) => [i * TILE, 0];
  drawGround(img, ...at(TILES.GRASS), rng, { tufts: 1 });
  drawGround(img, ...at(TILES.GRASS_TUFTS), rng, { tufts: 4 });
  drawGround(img, ...at(TILES.GRASS_DENSE), rng, { tufts: 7, speck: 0.1 });
  drawGround(img, ...at(TILES.GRASS_FLOWERS), rng, { tufts: 1, flowers: 3 });
  drawGround(img, ...at(TILES.GRASS_ROSES), rng, { tufts: 1, roses: 2 });
  drawGround(img, ...at(TILES.FOREST_FLOOR), rng, { palette: FLOOR });
  // weicher Übergang über die mittleren ~70 % der Kachel
  const ramp = (t) => Math.min(1, Math.max(0, (t - 0.15) / 0.7));
  const edge = (fn) => ({ grassAmount: fn, tufts: 1 });
  drawGround(img, ...at(TILES.EDGE_N), rng, edge((x, y) => ramp((y + 0.5) / TILE)));
  drawGround(img, ...at(TILES.EDGE_S), rng, edge((x, y) => ramp(1 - (y + 0.5) / TILE)));
  drawGround(img, ...at(TILES.EDGE_W), rng, edge((x) => ramp((x + 0.5) / TILE)));
  drawGround(img, ...at(TILES.EDGE_E), rng, edge((x) => ramp(1 - (x + 0.5) / TILE)));
  return img;
}

// ---------------------------------------------------------------- Bäume

const LIGHT = (() => {
  const v = [-0.55, -0.7, 0.55]; // Licht von links oben
  const l = Math.hypot(...v);
  return v.map((n) => n / l);
})();

function drawTree(img, ox, oy, rng) {
  const put = (x, y, c) => {
    if (x >= 0 && y >= 0 && x < TREE_W && y < TREE_H) img.set(ox + x, oy + y, c);
  };

  // Schatten am Boden
  for (let y = 0; y < TREE_H; y++) {
    for (let x = 0; x < TREE_W; x++) {
      const dx = (x + 0.5 - TREE_BASE.x) / 21;
      const dy = (y + 0.5 - (TREE_BASE.y - 1)) / 5.5;
      if (dx * dx + dy * dy <= 1) put(x, y, C.shadow);
    }
  }

  // Stamm (mit Wurzeln unten)
  const trunkTop = 52;
  for (let y = trunkTop; y <= TREE_BASE.y; y++) {
    const flare = Math.max(0, y - (TREE_BASE.y - 6)); // unten breiter
    const half = 5 + Math.round(flare * 0.8);
    const x0 = TREE_BASE.x - half;
    const x1 = TREE_BASE.x + half - 1;
    for (let x = x0; x <= x1; x++) {
      let c;
      if (x === x0 || x === x1 || y === TREE_BASE.y) c = C.barkOutline;
      else {
        const t = (x - x0) / (x1 - x0);
        c = t < 0.3 ? C.bark[2] : t < 0.72 ? C.bark[1] : C.bark[0];
        if ((x * 7 + Math.floor(y / 3) * 3) % 11 === 0) c = C.bark[0]; // Rinde
      }
      put(x, y, c);
    }
  }

  // Krone: mehrere "Blätterbälle"; der vorderste Ball bestimmt das Pixel
  const cx = 32;
  const cy = 34;
  const balls = [];
  const rim = 8;
  const phase = rng() * Math.PI * 2;
  for (let i = 0; i < rim; i++) {
    const a = phase + (i / rim) * Math.PI * 2;
    balls.push({
      x: cx + Math.cos(a) * (17 + rng() * 2),
      y: cy + Math.sin(a) * (13 + rng() * 2),
      r: 10.5 + rng() * 2,
      z: Math.sin(a) * 4, // unten = näher am Betrachter
    });
  }
  for (let i = 0; i < 4; i++) {
    balls.push({ x: cx + (rng() - 0.5) * 16, y: cy + (rng() - 0.5) * 12, r: 11 + rng() * 2, z: 8 });
  }
  balls.push({ x: cx - 6 + rng() * 3, y: cy - 10 + rng() * 3, r: 8, z: 12 });

  const field = Array.from({ length: TREE_H }, () => new Array(TREE_W).fill(null));
  for (let y = 0; y < TREE_H; y++) {
    for (let x = 0; x < TREE_W; x++) {
      let best = null;
      balls.forEach((b, id) => {
        const dx = x + 0.5 - b.x;
        const dy = y + 0.5 - b.y;
        const d2 = dx * dx + dy * dy;
        if (d2 > b.r * b.r) return;
        const h = Math.sqrt(b.r * b.r - d2);
        const z = b.z + h;
        if (!best || z > best.z) best = { z, id, nx: dx / b.r, ny: dy / b.r, nz: h / b.r };
      });
      field[y][x] = best;
    }
  }

  for (let y = 0; y < TREE_H; y++) {
    for (let x = 0; x < TREE_W; x++) {
      const p = field[y][x];
      if (!p) continue;
      const nb = [[1, 0], [-1, 0], [0, 1], [0, -1]].map(([i, j]) => field[y + j]?.[x + i] ?? null);
      // Umriss außen
      if (nb.some((q) => !q)) {
        put(x, y, C.leafOutline);
        continue;
      }
      // Trennlinie zwischen Blätterbällen, wenn der Nachbarball deutlich höher liegt
      if (nb.some((q) => q.id !== p.id && q.z - p.z > 2.5)) {
        put(x, y, C.leafOutline);
        continue;
      }
      let b = p.nx * LIGHT[0] + p.ny * LIGHT[1] + p.nz * LIGHT[2];
      b -= ((y - cy) / 30) * 0.25; // Unterseite der Krone dunkler
      let t = b > 0.8 ? 3 : b > 0.55 ? 2 : b > 0.25 ? 1 : 0;
      const r = rng(); // etwas Blattstruktur
      if (r < 0.06 && t > 0) t -= 1;
      else if (r < 0.09 && t < 3) t += 1;
      put(x, y, C.leaf[t]);
    }
  }
}

function buildTrees() {
  const img = new PixelImage(TREE_W * TREE_VARIANTS, TREE_H);
  const rng = mulberry32(SEED + 7);
  for (let v = 0; v < TREE_VARIANTS; v++) drawTree(img, v * TREE_W, 0, rng);
  return img;
}

// ---------------------------------------------------------------- Karte

function pickWeighted(rng, entries) {
  const total = entries.reduce((s, [, w]) => s + w, 0);
  let r = rng() * total;
  for (const [value, w] of entries) {
    r -= w;
    if (r < 0) return value;
  }
  return entries[entries.length - 1][0];
}

const inMeadow = (tx, ty) => tx >= MEADOW.x0 && tx < MEADOW.x1 && ty >= MEADOW.y0 && ty < MEADOW.y1;

function buildMap() {
  const rng = mulberry32(SEED + 1);
  const gid = (index) => index + 1; // Tiled zählt ab 1 (0 = leer)

  const ground = [];
  for (let y = 0; y < MAP_H; y++) {
    for (let x = 0; x < MAP_W; x++) {
      let tile = TILES.FOREST_FLOOR;
      if (inMeadow(x, y)) {
        tile = pickWeighted(rng, [
          [TILES.GRASS, 55], [TILES.GRASS_TUFTS, 25], [TILES.GRASS_DENSE, 12],
          [TILES.GRASS_FLOWERS, 5], [TILES.GRASS_ROSES, 3],
        ]);
      } else if (inMeadow(x, y + 1)) tile = TILES.EDGE_N;
      else if (inMeadow(x, y - 1)) tile = TILES.EDGE_S;
      else if (inMeadow(x + 1, y)) tile = TILES.EDGE_W;
      else if (inMeadow(x - 1, y)) tile = TILES.EDGE_E;
      ground.push(gid(tile));
    }
  }

  // Bäume: dichter Wald rund um die Wiese, in versetzten Reihen
  const trees = [];
  const STEP_X = 40;
  const STEP_Y = 30;
  let row = 0;
  for (let y = 20; y <= MAP_H * TILE + 40; y += STEP_Y, row++) {
    for (let x = (row % 2) * (STEP_X / 2) - 8; x <= MAP_W * TILE + 16; x += STEP_X) {
      const px = Math.round(x + (rng() - 0.5) * 14);
      const py = Math.round(y + (rng() - 0.5) * 10);
      // Abstand des Stammfußes zur Wiese (in Pixeln, 0 = auf der Wiese)
      const mx = Math.max(MEADOW.x0 * TILE - px, 0, px - MEADOW.x1 * TILE);
      const my = Math.max(MEADOW.y0 * TILE - py, 0, py - MEADOW.y1 * TILE);
      const dist = Math.hypot(mx, my);
      if (dist === 0) continue;
      if (dist < 24 && rng() < 0.45) continue; // Waldrand etwas aufgelockert
      trees.push({ x: px, y: py, variant: Math.floor(rng() * TREE_VARIANTS) });
    }
  }
  trees.sort((a, b) => a.y - b.y);

  return {
    type: 'map',
    version: '1.10',
    tiledversion: '1.10.2',
    orientation: 'orthogonal',
    renderorder: 'right-down',
    infinite: false,
    compressionlevel: -1,
    width: MAP_W,
    height: MAP_H,
    tilewidth: TILE,
    tileheight: TILE,
    nextlayerid: 3,
    nextobjectid: trees.length + 1,
    layers: [
      {
        id: 1, name: 'ground', type: 'tilelayer', x: 0, y: 0,
        width: MAP_W, height: MAP_H, opacity: 1, visible: true, data: ground,
      },
      {
        id: 2, name: 'trees', type: 'objectgroup', draworder: 'topdown',
        x: 0, y: 0, opacity: 1, visible: true,
        // x/y = Stammfuß des Baumes
        objects: trees.map((t, i) => ({
          id: i + 1, name: 'tree', type: 'tree', x: t.x, y: t.y,
          width: 0, height: 0, rotation: 0, point: true, visible: true,
          properties: [{ name: 'variant', type: 'int', value: t.variant }],
        })),
      },
    ],
    tilesets: [{
      firstgid: 1,
      name: 'tiles',
      image: '../tilesets/tiles.png',
      imagewidth: TILE * TILE_COUNT,
      imageheight: TILE,
      tilewidth: TILE,
      tileheight: TILE,
      tilecount: TILE_COUNT,
      columns: TILE_COUNT,
      margin: 0,
      spacing: 0,
    }],
  };
}

// ---------------------------------------------------------------- Ausgabe

function write(relPath, content) {
  const file = join(ROOT, relPath);
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, content);
  console.log('geschrieben:', relPath);
}

write('public/assets/tilesets/tiles.png', buildTileset().toPNG());
write('public/assets/sprites/trees.png', buildTrees().toPNG());
write('public/assets/maps/world.json', JSON.stringify(buildMap()));
