"""Schritt 1: Referenzbild → saubere Pixel-Art in Originalauflösung (Frontansicht, Idle).

1. Pixelraster des hochskalierten Bildes finden (Periode + Versatz)
2. Jede Rasterzelle auf ihren Median-Farbwert reduzieren → 62×62 Pixel
3. Auf eine feste Palette (18 Farben) abbilden, Hintergrund transparent
4. Idle-Pose: linken Arm (+ Körperhälfte) auf die rechte Seite spiegeln

Ein- und Ausgabe relativ zum Arbeitsordner: ref/vampire_ref.png → ref/*.json
"""
import json
from collections import deque

import numpy as np
from PIL import Image

N = 62  # Kantenlänge in Original-Pixeln
PAL = {
    "K": "#050307", "k": "#120f18", "d": "#1c1a22", "g": "#2a2830", "p": "#201830",
    "h": "#352a42", "b": "#2e1c20", "B": "#42130f", "E": "#5e0708", "R": "#5e1f20",
    "r": "#863232", "m": "#4e2a2d", "e": "#b11c26", "i": "#e3575e", "s": "#9f7570",
    "S": "#d4b9b4", "W": "#f6e9df", "w": "#fffbfa",
}


def fit_grid(sig, lo=4.20, hi=4.40):
    best = None
    for p in np.arange(lo, hi, 0.001):
        for ph in np.arange(0, p, 0.02):
            idx = np.floor(np.arange(ph, len(sig), p)).astype(int)
            idx = idx[idx < len(sig)]
            score = sig[idx].sum() / len(idx)
            if best is None or score > best[0]:
                best = (score, p, ph)
    return best[1], best[2]


def sample_native(im, p, ph):
    bounds = [int(np.floor(ph + k * p)) for k in range(-1, N)]
    last = im.shape[0] - 1
    out = np.zeros((N, N, 3))
    for j in range(N):
        y0, y1 = max(0, bounds[j] + 1), min(last, bounds[j + 1])
        ya, yb = (y0 + 1, y1 - 1) if y1 - y0 >= 3 else (y0, y1)
        for i in range(N):
            x0, x1 = max(0, bounds[i] + 1), min(last, bounds[i + 1])
            xa, xb = (x0 + 1, x1 - 1) if x1 - x0 >= 3 else (x0, x1)
            out[j, i] = np.median(im[ya:yb + 1, xa:xb + 1].reshape(-1, 3), axis=0)
    return out


def background_mask(a):
    """Heller Hintergrund = mit dem Bildrand verbundene, fast weiße Fläche."""
    h, w, _ = a.shape
    light = a.min(axis=2) > 225
    bg = np.zeros((h, w), bool)
    q = deque((y, x) for y in range(h) for x in range(w)
              if (x in (0, w - 1) or y in (0, h - 1)) and light[y, x])
    for y, x in q:
        bg[y, x] = True
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and light[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True
                q.append((ny, nx))
    return bg


def quantize(a, bg):
    keys = list(PAL)
    P = np.array([[int(v[i:i + 2], 16) for i in (1, 3, 5)] for v in PAL.values()], float)
    lab = ((a[:, :, None, :] - P[None, None]) ** 2).sum(-1).argmin(-1)
    return [["." if bg[y, x] else keys[lab[y, x]] for x in range(N)] for y in range(N)]


def main():
    img = np.asarray(Image.open("ref/vampire_ref.png").convert("RGB")).astype(float)
    dx = np.abs(np.diff(img, axis=1)).sum(axis=(0, 2))
    dy = np.abs(np.diff(img, axis=0)).sum(axis=(1, 2))
    px, phx = fit_grid(dx)
    py, phy = fit_grid(dy)
    print(f"Raster: {px:.3f} px (x), {py:.3f} px (y)")
    native = sample_native(img, (px + py) / 2, (phx + phy) / 2)
    Image.fromarray(native.round().astype(np.uint8)).save("ref/native62.png")

    grid = quantize(native, background_mask(native))
    json.dump({"pal": PAL, "grid": ["".join(r) for r in grid]}, open("ref/front_q.json", "w"))

    # Idle: Zeilen 22–41 (Schultern bis Hände) links → rechts spiegeln (Körpermitte x = 31)
    sym = [r[:] for r in grid]
    for y in range(22, 42):
        for x in range(32, N):
            sym[y][x] = grid[y][62 - x]
    json.dump({"pal": PAL, "grid": ["".join(r) for r in sym]}, open("ref/front_sym.json", "w"))
    print("ref/front_q.json, ref/front_sym.json geschrieben")


if __name__ == "__main__":
    main()
