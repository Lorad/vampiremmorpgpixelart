"""Vampirin – Rückansicht (Nord), abgeleitet aus der Frontansicht."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (H, W, blank, block, composite, load, mirror, outline,  # noqa: E402
                    pixels, save, union)

S = load("char/S.json")
P = S["parts"]
BODY = 62  # Spiegelung Körper (Mitte x = 31)
HEAD = 61  # Spiegelung Kopf (Mitte x = 30.5)

N = {p: blank() for p in P}

# Gliedmaßen: gespiegelt, Namen bleiben (ihr rechter Arm ist jetzt rechts im Bild)
for p in ("upper_arm_R", "forearm_R", "upper_arm_L", "forearm_L",
          "thigh_R", "shin_R", "foot_R", "thigh_L", "shin_L", "foot_L"):
    N[p] = mirror(P[p], BODY)

# Oberkörper: Rücken des Mieders (größtenteils von Haaren verdeckt)
torso = mirror(P["torso"], BODY)
for x, y in pixels(torso):
    if torso[y][x] in "SWws":
        torso[y][x] = "d" if y >= 22 else "S"  # Hals bleibt Haut
N["torso"] = torso

# ------------------------------------------------------------ Rock (geschlossene Rückseite)
sil = mirror(union(P["skirt_front"], P["skirt_back"]), BODY)
pts = set(pixels(sil))
skirt = blank()
for x, y in pts:
    f = (x - 31) / ((y - 27) * 0.42 + 2.5) * 2.2  # Falten fächern nach unten auf
    t = f - math.floor(f)
    c = "k" if t < 0.18 else "d" if t < 0.5 else "g" if t < 0.82 else "d"
    if y <= 33:
        c = "d" if c == "g" else c
    skirt[y][x] = c
# Saum: unterste Pixelreihe jeder Spalte dunkelrot (Futter blitzt durch)
for x in range(W):
    ys = [y for y in range(H) if (x, y) in pts]
    if ys and max(ys) >= 50:
        skirt[max(ys)][x] = "R"
# Umriss auf den Rand der Form
edge = [(x, y) for x, y in pts
        if any((x + dx, y + dy) not in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
for x, y in edge:
    skirt[y][x] = "K"
N["skirt_back"] = skirt

# ------------------------------------------------------------ Haare (bedecken Kopf und Rücken)
hair_sil = set(pixels(mirror(union(P["hair_back"], P["hair_front"]), HEAD)))
head_area = mirror(P["head"], HEAD)
for x, y in pixels(head_area):
    hair_sil.add((x, y))
# Untere Kante: wellige Spitzen
xs = [x for x, y in hair_sil]
x0, x1 = min(xs), max(xs)
for x in range(x0, x1 + 1):
    col = [y for (xx, y) in hair_sil if xx == x]
    if not col:
        continue
    bottom = 30 + round(1.4 + 1.6 * math.sin((x - x0) * 2 * math.pi / 6.5))
    for y in range(22, H):
        if y > bottom:
            hair_sil.discard((x, y))
        elif y >= 22 and min(col) < 22:
            hair_sil.add((x, y))

hair = blank()
for x, y in hair_sil:
    spread = 1 + max(0, y - 5) * 0.07
    u = (x - 30.5) / spread + 0.9 * math.sin(y / 3.2 + x / 6.0)
    s = u / 2.7
    t = s - math.floor(s)
    left = (x - 1, y) in hair_sil
    sl = ((x - 1 - 30.5) / spread + 0.9 * math.sin(y / 3.2 + (x - 1) / 6.0)) / 2.7
    if left and math.floor(sl) != math.floor(s) and y > 4:
        c = "k"  # Strähnen-Trennlinie
    elif t < 0.4:
        c = "h" if 4 <= y <= 13 else "p"
    elif t > 0.8:
        c = "k" if y > 24 else "d"
    else:
        c = "p"
    # Glanzring am Hinterkopf
    r = math.hypot((x - 30.5) * 0.9, y - 13)
    if 7.2 < r < 8.6 and y < 12 and c != "k":
        c = "h"
    if y >= 29 and c == "h":
        c = "p"
    hair[y][x] = c
edge = [(x, y) for x, y in hair_sil
        if any((x + dx, y + dy) not in hair_sil for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
for x, y in edge:
    hair[y][x] = "K"
# zweite, dunkle Innenkante wie in der Frontansicht
for x, y in list(hair_sil):
    if (x, y) not in edge and hair[y][x] in "ph" and any(
            (x + dx, y + dy) in edge for dx, dy in ((1, 0), (-1, 0), (0, -1))):
        hair[y][x] = "k"
N["hair_back"] = hair

# ------------------------------------------------------------ Kopf: nur das Spitzohr (linkes Ohr)
block(N["head"], 20, 14, """
.KK..
KSSK.
.KsK.
..K..
""")

N_ORDER = ["skirt_front", "thigh_R", "thigh_L", "shin_R", "shin_L", "foot_R", "foot_L",
           "skirt_back", "torso", "upper_arm_R", "upper_arm_L", "forearm_R", "forearm_L",
           "hair_front", "hair_back", "head"]

piv = {}
for k, (x, y) in S["pivots"].items():
    axis = HEAD if k in ("head", "hair_front", "hair_back") else BODY
    piv[k] = [axis - x, y]

save({"pal": S["pal"], "order": N_ORDER, "pivots": piv, "parts": N}, "char/N.json")
print("ok")
