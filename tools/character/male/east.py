"""Vampir (männlich) – Seitenansicht (Ost, Blick nach rechts). Neu gezeichnet.

Blick nach Osten → seine rechte Körperseite zeigt zur Kamera:
rechter Arm/rechtes Bein = nah (vorne), linker Arm/linkes Bein = fern (hinten, dunkler).
Anders als bei der Vampirin stehen die Stiefel wie in allen anderen
Richtungen auf Zeile 61.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import PARTS, blank, block, load, save  # noqa: E402
from draw import darken, edge_of, ranges_to_set, shift  # noqa: E402

S = load("char/S.json")
E = {p: blank() for p in PARTS}


def fill(part, pts, fn, outline="K"):
    edge = edge_of(pts) if outline else set()
    for x, y in pts:
        E[part][y][x] = outline if (x, y) in edge else fn(x, y)
    return edge


def put(part, pts):
    for (x, y), c in pts.items():
        E[part][y][x] = c


# ------------------------------------------------------------ Haare (zurückgekämmt)
HAIR = {1: (26, 32), 2: (24, 34), 3: (23, 35), 4: (22, 36), 5: (21, 37), 6: (21, 37),
        7: (20, 38), 8: (20, 38), 9: (20, 38), 10: (20, 36), 11: (20, 33), 12: (20, 31),
        13: (20, 30), 14: (21, 30), 15: (21, 29), 16: (22, 29), 17: (22, 28), 18: (23, 28),
        19: (24, 27)}
hair = ranges_to_set(HAIR)


def hair_shade(x, y):
    """Strähnen folgen der Kopfform von der Stirn nach hinten (Bögen um die Kopfmitte)."""
    r = math.hypot((x - 31) * 0.9, (y - 14) * 1.15) + 0.4 * math.sin(x / 2.5)
    t = (r / 2.3) - math.floor(r / 2.3)
    if t < 0.2:
        return "k"
    if y <= 9 and x >= 24 and 0.45 < t < 0.85:
        return "h"  # Glanz oben, wo das Licht auf die gekämmten Strähnen fällt
    return "p"


edge = fill("hair_back", hair, hair_shade)
for x, y in hair:  # zweite, dunkle Innenkante
    if (x, y) not in edge and E["hair_back"][y][x] in "ph" and any(
            (x + dx, y + dy) in edge for dx, dy in ((1, 0), (-1, 0), (0, -1))):
        E["hair_back"][y][x] = "k"
# Vorderes Haar (Oberkopf bis zum Haaransatz) liegt über dem Kopf
for y in range(0, 11):
    E["hair_front"][y] = E["hair_back"][y][:]

# ------------------------------------------------------------ Kopf (Profil)
FRONT = {10: 38, 11: 39, 12: 39, 13: 39, 14: 38, 15: 39, 16: 40, 17: 41, 18: 39, 19: 39,
         20: 38, 21: 37}
BACK = {10: 36, 11: 33, 12: 32, 13: 31, 14: 31, 15: 31, 16: 31, 17: 31, 18: 31, 19: 31,
        20: 32, 21: 34}
face = {(x, y) for y in FRONT for x in range(BACK[y], FRONT[y] + 1)}
for x, y in face:
    E["head"][y][x] = "W"
for y in FRONT:  # Profil-Umriss vorne
    E["head"][y][FRONT[y] + 1] = "K"
for x in range(33, 38):  # Kinn / Kiefer unten
    E["head"][22][x] = "K"
E["head"][21][33] = E["head"][21][32] = "K"
E["head"][20][31] = "K"
# Schädel unter den Haaren dunkel (falls die Haare sich bewegen)
# (nur wo das vordere Haar darüber liegt, sonst wäre der Hinterkopf flach schwarz)
for x, y in hair:
    if 21 <= x <= 36 and 2 <= y <= 10 and E["head"][y][x] == "." and E["hair_front"][y][x] != ".":
        E["head"][y][x] = "k"
put("head", {
    (35, 13): "K", (36, 13): "K", (37, 14): "K", (38, 14): "K",  # Braue
    (35, 15): "K", (36, 15): "K", (37, 15): "K",  # Lid
    (35, 16): "E", (36, 16): "e", (37, 16): "w",  # Auge
    (36, 17): "E", (37, 17): "E",
    (40, 17): "S", (39, 18): "S",  # Nase
    (37, 19): "K", (38, 19): "K", (39, 19): "S",  # Mund
    (38, 20): "w", (37, 20): "S",  # Eckzahn
    (32, 16): "S", (32, 17): "S", (32, 18): "S", (33, 19): "S", (33, 20): "S",  # Wange
})
# Spitzohr (zeigt nach hinten oben)
put("head", {(28, 11): "K", (28, 12): "K", (29, 12): "S", (30, 12): "K",
             (28, 13): "K", (29, 13): "S", (30, 13): "W", (31, 13): "K",
             (29, 14): "K", (30, 14): "S", (31, 14): "W",
             (29, 15): "K", (30, 15): "s", (31, 15): "S",
             (30, 16): "K", (31, 16): "s", (31, 17): "K"})

# ------------------------------------------------------------ Oberkörper
block(E["torso"], 26, 18, """
.....KSSSK...
.....KSSSK...
.....KSSSK...
.....KSSWWK..
.KKKdKSWWeeK.
KdgggdKWeieK.
KdggggdKBeeK.
KdggggdKBReK.
KdggggddKBRK.
KdggggddKBRK.
KdggggddKBRK.
KddgggddKBmK.
KddgggddKBRK.
.KkkkkkkKBK..
""")
# Stehkragen hinter dem Hals: außen schwarz, innen rot
put("torso", {(25, 14): "K",
              (25, 15): "K", (26, 15): "d", (27, 15): "K",
              (25, 16): "K", (26, 16): "d", (27, 16): "r", (28, 16): "K",
              (25, 17): "K", (26, 17): "d", (27, 17): "r", (28, 17): "r", (29, 17): "K",
              (25, 18): "K", (26, 18): "d", (27, 18): "g", (28, 18): "r", (29, 18): "r", (30, 18): "K",
              (25, 19): "K", (26, 19): "d", (27, 19): "g", (28, 19): "R", (29, 19): "r", (30, 19): "K",
              (25, 20): "K", (26, 20): "d", (27, 20): "g", (28, 20): "d", (29, 20): "R", (30, 20): "K",
              (26, 21): "K", (27, 21): "d", (28, 21): "g", (29, 21): "d", (30, 21): "K"})

# ------------------------------------------------------------ Arme
block(E["upper_arm_R"], 29, 22, """
.KKKK.
KgghgK
KdgggK
KdggdK
KdggdK
KdggdK
KdggdK
KdggdK
KdggdK
KdggdK
""")
block(E["forearm_R"], 28, 32, """
.KdggdK.
.KdggdK.
.KdggdK.
KRrrrrRK
KbRRRRbK
.KWwwWK.
..KWWSK.
..KWsSK.
...KWK..
...KK...
""")
# Ferner (linker) Arm: gleiche Form, 2 px weiter hinten und abgedunkelt
E["upper_arm_L"] = darken(shift(E["upper_arm_R"], -2))
E["forearm_L"] = darken(shift(E["forearm_R"], -2))

# ------------------------------------------------------------ Rockschöße (hinten lang, vorne kürzer)


def back_edge(y):
    return round(27 - (y - 32) * 5 / 18)


HEM = {31: 49, 32: 48, 33: 48, 34: 47, 35: 47, 36: 46, 37: 46}
skirt = {(x, y) for y in range(32, 51) for x in range(back_edge(y), 38)
         if y <= HEM.get(x, 50)}


def coat_fold(x, y):
    f = (x - 33 + (y - 32) * 0.35) / 2.6  # Falten laufen schräg nach hinten
    t = f - math.floor(f)
    c = "k" if t < 0.18 else "d" if t < 0.55 else "g" if t < 0.8 else "d"
    return "d" if x <= 22 and c == "g" else c


fill("skirt_front", skirt, coat_fold)
for y in range(34, 47):  # Futter an der vorderen Kante
    if E["skirt_front"][y][37] != "K":
        E["skirt_front"][y][37] = "R" if y % 4 == 0 else "r"
for x in range(31, 37):  # Futter blitzt am hochgezogenen Saum
    yb = HEM[x]
    if E["skirt_front"][yb - 1][x] not in "K.":
        E["skirt_front"][yb - 1][x] = "R"
for x in range(26, 37):  # Taille dunkel
    if E["skirt_front"][32][x] not in "K.":
        E["skirt_front"][32][x] = "k"
# Futter hinter den Beinen (nur beim Laufen sichtbar)
fill("skirt_back", ranges_to_set({y: (27, 38) for y in range(34, 51)}),
     lambda x, y: "R" if y % 3 == 0 else "r")

# ------------------------------------------------------------ Beine (Hose), rechts nah, links fern


def leg(dx=0):
    th, sh, fo = blank(), blank(), blank()
    tpts = ranges_to_set({y: (30 + dx, 35 + dx) for y in range(33, 46)})
    for x, y in tpts:
        th[y][x] = "K" if (x, y) in edge_of(tpts) else ("g" if x == 33 + dx else "d")
    spts = ranges_to_set({y: (31 + dx, 35 + dx) for y in range(44, 57)})
    for x, y in spts:
        sh[y][x] = "K" if (x, y) in edge_of(spts) else ("g" if x == 34 + dx else "d")
    block(fo, 31 + dx, 57, """
KdddgK....
KddddggK..
KdddddggK.
KddddddgdK
KKKKKKKKKK
""")
    return th, sh, fo


E["thigh_R"], E["shin_R"], E["foot_R"] = leg()
tl, sl, fl = leg(dx=-3)
E["thigh_L"], E["shin_L"], E["foot_L"] = darken(tl), darken(sl), darken(fl)

ORDER = ["upper_arm_L", "forearm_L", "hair_back", "skirt_back",
         "thigh_L", "shin_L", "foot_L", "thigh_R", "shin_R", "foot_R",
         "skirt_front", "torso", "upper_arm_R", "forearm_R", "head", "hair_front"]
PIV = {"root": [31, 60], "pelvis": [31, 33], "torso": [31, 32], "head": [32, 21],
       "hair_front": [29, 6], "hair_back": [29, 6],
       "upper_arm_R": [31, 24], "forearm_R": [31, 31.5],
       "upper_arm_L": [29, 24], "forearm_L": [29, 31.5],
       "skirt_front": [31, 32], "skirt_back": [31, 33],
       "thigh_R": [32.5, 34], "shin_R": [33, 45], "foot_R": [33, 57],
       "thigh_L": [29.5, 34], "shin_L": [30, 45], "foot_L": [30, 57]}
save({"pal": S["pal"], "order": ORDER, "pivots": PIV, "parts": E}, "char/E.json")
print("gespeichert: char/E.json")
