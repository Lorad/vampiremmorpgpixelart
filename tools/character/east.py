"""Vampirin – Seitenansicht (Ost, Blick nach rechts). Neu gezeichnet.

Blick nach Osten → ihre rechte Körperseite zeigt zur Kamera:
rechter Arm/rechtes Bein = nah (vorne), linker Arm/linkes Bein = fern (hinten, dunkler).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PARTS, blank, block, save  # noqa: E402
from draw import (darken, inner_line, paint, ranges_to_set, shift, wave,  # noqa: E402
                  hair_shader)

S = json.load(open("char/S.json"))
E = {p: blank() for p in PARTS}

# ------------------------------------------------------------ Haare
HAIR = {1: (24, 30), 2: (22, 32), 3: (21, 34), 4: (20, 35), 5: (19, 36), 6: (19, 37),
        7: (18, 38), 8: (18, 38), 9: (18, 39), 10: (17, 39), 11: (17, 40),
        12: [(17, 34), (38, 40)], 13: [(17, 32), (38, 39)]}
HAIR.update({14: (17, 31), 15: (17, 31), 16: (16, 31), 17: (16, 31), 18: (16, 31),
             19: (17, 31), 20: (17, 31), 21: (17, 31), 22: (17, 30), 23: (16, 29),
             24: (16, 28), 25: (17, 28), 26: (17, 28), 27: (16, 28), 28: (17, 28),
             29: (18, 28), 30: (18, 27), 31: (19, 27), 32: [(19, 21), (23, 26)],
             33: [(20, 20), (24, 25)]})
hair = ranges_to_set(HAIR)
shade = hair_shader(hair, crown=(31, 3), top_hi=13, radial_until=15)
edge = paint(E["hair_back"], hair, shade)
inner_line(E["hair_back"], hair, edge)
# Vorderes Haar (Oberkopf + Pony) = alles bis Zeile 13
for y in range(0, 14):
    E["hair_front"][y] = E["hair_back"][y][:]

# ------------------------------------------------------------ Kopf (Gesicht im Profil + Spitzohr)
block(E["head"], 27, 12, """
........WWW...
K.....SWWWWWK.
KSK..SWWWWWWK.
.KSSKSWKKKWWK.
..KsSSWEweWWK.
...KsSWEeeWWSK
....KSWKieWWK.
.....SWWWWWsK.
.....KSWWWSK..
......KKKKK...
""")
# Schädel unter den Haaren (dunkel, falls die Haare sich bewegen)
for y in range(2, 14):
    for x in range(20, 38):
        if (x, y) in hair:
            if E["head"][y][x] == ".":
                E["head"][y][x] = "k"

# ------------------------------------------------------------ Oberkörper
block(E["torso"], 27, 21, """
....KssSK..
....KgggK..
.KdddKSWWK.
KkddddKWWK.
KkddddgKSSK
KkdddgggggK
KkdddggggdK
KkddddgggK.
.KbRRrrrbK.
.KRrrrRrrK.
.KbRrrrRbK.
.KdddddddK.
""")

# ------------------------------------------------------------ Arme
def arm(upper, fore, dx=0):
    up = ranges_to_set({y: (a + dx, b + dx) for y, (a, b) in upper.items()})
    fo = ranges_to_set({y: (a + dx, b + dx) for y, (a, b) in fore.items()})
    gu, gf = blank(), blank()
    paint(gu, up, lambda x, y: "g" if x >= 31 + dx else "d")

    def ffn(x, y):
        if y >= 38:
            return "W" if x <= 31 + dx else "s" if y == 39 else "S"
        if y == 36:
            return "B" if (x + dx) % 3 == 0 else "b" if x < 29 + dx else "r"
        if x <= 27 + dx:
            return "B"
        return "R" if (x + y // 3) % 3 == 0 else "r"
    paint(gf, fo, ffn)
    return gu, gf


UPPER = {y: (29, 33) for y in range(24, 32)}
UPPER[23] = (30, 32)
FORE = {31: (29, 33), 32: (28, 34), 33: (27, 34), 34: (26, 35), 35: (26, 35), 36: (26, 36),
        37: (27, 35), 38: (30, 33), 39: (30, 33), 40: (31, 32)}
E["upper_arm_R"], E["forearm_R"] = arm(UPPER, FORE)
ul, fl = arm(UPPER, FORE, dx=-2)
E["upper_arm_L"], E["forearm_L"] = darken(ul), darken(fl)

# ------------------------------------------------------------ Rock
SK = {32: (28, 35), 33: (27, 36), 34: (27, 36), 35: (26, 37), 36: (26, 37), 37: (25, 38),
      38: (25, 38), 39: (24, 38), 40: (24, 39), 41: (23, 39), 42: (23, 39), 43: (22, 40),
      44: (22, 40), 45: (21, 40), 46: (21, 40), 47: (20, 41), 48: (20, 41), 49: (19, 41),
      50: (19, 41), 51: (18, 42), 52: (18, 42), 53: (17, 41), 54: (17, 40), 55: (16, 37),
      56: (16, 33), 57: (16, 29), 58: (17, 25)}
skirt = ranges_to_set(SK)
front = {y: b for y, (a, b) in SK.items()}


def sfn(x, y):
    if y >= 37 and x >= front[y] - 1 and y <= 55:
        return "r" if y % 4 else "R"  # Futter an der vorderen Öffnung
    f = (x - 31) / ((y - 28) * 0.38 + 2.2) * 2.0
    t = f - int(f // 1)
    t = f - __import__("math").floor(f)
    c = "k" if t < 0.2 else "d" if t < 0.52 else "g" if t < 0.82 else "d"
    if x <= 22 and c == "g":
        c = "d"
    return c


paint(E["skirt_front"], skirt, sfn)
# Rückseite des Rocks hinter den Beinen (rotes Futter, nur beim Animieren sichtbar)
paint(E["skirt_back"], ranges_to_set({y: (28, 40) for y in range(36, 55)}),
      lambda x, y: "R" if y % 3 == 0 else "r")

# ------------------------------------------------------------ Beine (rechts nah, links fern)
def leg(dx=0):
    th, sh, fo = blank(), blank(), blank()
    paint(th, ranges_to_set({y: (30 + dx, 35 + dx) for y in range(33, 46)}),
          lambda x, y: "r" if y in (43, 44) else "S" if x < 34 + dx else "s")
    paint(sh, ranges_to_set({y: (31 + dx, 35 + dx) for y in range(44, 56)}),
          lambda x, y: "g" if x == 34 + dx else "d")
    block(fo, 31 + dx, 54, """
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
       "upper_arm_R": [31, 24], "forearm_R": [31, 31],
       "upper_arm_L": [29, 24], "forearm_L": [29, 31],
       "skirt_front": [31, 32], "skirt_back": [31, 33],
       "thigh_R": [32.5, 34], "shin_R": [33, 45], "foot_R": [33, 54],
       "thigh_L": [29.5, 34], "shin_L": [30, 45], "foot_L": [30, 54]}
save({"pal": S["pal"], "order": ORDER, "pivots": PIV, "parts": E}, "char/E.json")
print("ok")
