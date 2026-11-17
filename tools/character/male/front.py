"""Vampir (männlich) – Frontansicht (Süd), neu gezeichnet im Stil der Vampirin.

Gleiche Palette, gleiche Leinwand (62×62) und dieselben 16 Skelett-Teile wie
die Vampirin, damit dieselben Animationen passen:

- kurze, zurückgekämmte Haare mit Spitzansatz (hair_front/hair_back)
- Gesicht mit roten Augen, strengen Brauen, Eckzähnen und Spitzohren (head)
- Stehkragen mit rotem Futter, Krawatte, rote Weste, Gehrock (torso)
- Ärmel mit roten Manschetten und Spitze (upper_arm/forearm)
- Rockschöße des Gehrocks (skirt_front), rotes Futter dahinter (skirt_back)
- Hose (thigh/shin) und Stiefel (foot, aus feet.py)

Verdeckte Bereiche werden aufgefüllt (Schädel unter den Haaren, Rock unter
den Armen, Beine unter dem Rock), damit beim Bewegen keine Löcher entstehen.

Ergebnis (relativ zum Arbeitsordner): char/S.json
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import PARTS, blank, block, mirror, save  # noqa: E402
from draw import edge_of, ranges_to_set  # noqa: E402
from extract import PAL  # noqa: E402
from feet import replace_feet  # noqa: E402

BODY = 62  # Spiegelachse Körper: x' = 62 - x (Mitte = Pixel 31)
LEG = 61  # Beine liegen um x = 31,0 (zwischen Pixel 30 und 31)
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))

P = {n: blank() for n in PARTS}


def fill(part, pts, fn, outline="K", keep=False):
    """Füllt Punkte mit fn(x, y); Randpixel bekommen den Umriss.
    keep=True: nur leere Pixel des Teils füllen (verdeckte Bereiche)."""
    g = P[part]
    edge = edge_of(pts) if outline else set()
    for x, y in pts:
        if keep and g[y][x] != ".":
            continue
        c = outline if (x, y) in edge else fn(x, y)
        if c and c != ".":
            g[y][x] = c
    return edge


def put(part, pts):
    for (x, y), c in pts.items():
        P[part][y][x] = c


def sym_ranges(ranges):
    """Linke Hälfte (bis zur Mitte x = 31) → symmetrische Zeilenbereiche."""
    out = {}
    for y, rs in ranges.items():
        rs = [rs] if isinstance(rs[0], int) else rs
        full = []
        for x0, x1 in rs:
            full.append((x0, x1))
            m0, m1 = BODY - x1, BODY - x0
            if (m0, m1) != (x0, x1):
                full.append((m0, m1))
        out[y] = full
    return out


# ------------------------------------------------------------ Haare
# Silhouette: runder Oberkopf, Spitzansatz (Widow's Peak) in der Mitte,
# Schläfen kurz, die Ohren bleiben frei.
HAIR_FRONT = sym_ranges({
    1: (28, 31), 2: (25, 31), 3: (24, 31), 4: (23, 31), 5: (22, 31), 6: (22, 31),
    7: (21, 31), 8: (21, 31), 9: (21, 31), 10: [(21, 26), (30, 31)], 11: [(21, 25), (31, 31)],
    12: (22, 24), 13: (23, 24),
})
hair_front = ranges_to_set(HAIR_FRONT)


def hair_shade(x, y):
    """Zurückgekämmt: Strähnen laufen strahlenförmig vom Haaransatz nach oben."""
    a = math.atan2(x - 31, 15 - y)
    s = a * 3.2 + 0.5
    t = s - math.floor(s)
    if t < 0.2:
        return "k"
    if y <= 7 and 0.3 < t < 0.75:
        return "h"
    return "p"


edge = fill("hair_front", hair_front, hair_shade)
# zweite, dunkle Innenkante wie bei der Vampirin
for x, y in hair_front:
    if (x, y) not in edge and P["hair_front"][y][x] in "ph" and y >= 4 and any(
            (x + dx, y + dy) in edge for dx, dy in ((1, 0), (-1, 0), (0, -1))):
        P["hair_front"][y][x] = "k"

# Hinterkopf: etwas breiter, im Nacken neben dem Kiefer sichtbar
HAIR_BACK = sym_ranges({
    1: (28, 31), 2: (25, 31), 3: (24, 31), 4: (23, 31), 5: (22, 31), 6: (22, 31),
    **{y: (21, 31) for y in range(7, 17)}, 17: (22, 31), 18: (23, 31), 19: (24, 31),
})
hair_back = ranges_to_set(HAIR_BACK)
fill("hair_back", hair_back, lambda x, y: "p" if (x + y) % 5 == 0 and y < 17 else "k")

# ------------------------------------------------------------ Kopf
# Schädel unter den Haaren dunkel (falls die Haare sich bewegen)
skull = ranges_to_set(sym_ranges({y: (x0 + 1, 31) for y, x0 in {
    2: 25, 3: 24, 4: 23, 5: 22, 6: 22, 7: 21, 8: 21, 9: 21, 10: 21, 11: 22, 12: 22}.items()}))
for x, y in skull:
    P["head"][y][x] = "k"

FACE = sym_ranges({10: (26, 31), **{y: (24, 31) for y in range(11, 19)}, 19: (25, 31),
                   20: (27, 31)})
face = ranges_to_set(FACE)
for x, y in face:
    P["head"][y][x] = "W"
# Umriss außen am Gesicht
for y in range(11, 19):
    P["head"][y][23] = P["head"][y][39] = "K"
for x, y in ((24, 19), (38, 19), (25, 20), (26, 20), (36, 20), (37, 20)):
    P["head"][y][x] = "K"
for x in range(27, 36):
    P["head"][21][x] = "K"

# Schattierung: Wangen und Kiefer etwas dunkler
for y in range(15, 19):
    P["head"][y][24] = P["head"][y][38] = "S"
for x, y in ((25, 19), (37, 19), (27, 20), (35, 20)):
    P["head"][y][x] = "S"

# Gesicht (linke Bildhälfte = sein rechtes Auge), rechts gespiegelt
FACE_L = {
    (25, 12): "K", (26, 12): "K",  # Braue außen hoch …
    (27, 13): "K", (28, 13): "K", (29, 13): "K",  # … innen tief: strenger Blick
    (25, 15): "K", (26, 15): "K", (27, 15): "K", (28, 15): "K",  # Oberlid
    (25, 16): "K", (26, 16): "e", (27, 16): "w", (28, 16): "E",  # Auge
    (26, 17): "E", (27, 17): "e", (28, 17): "E",
}
for (x, y), c in FACE_L.items():
    P["head"][y][x] = c
    P["head"][y][BODY - x] = c
# Glanzpunkt im rechten Auge auf derselben Seite wie links (Licht von links oben)
P["head"][16][34], P["head"][16][35] = "E", "w"
P["head"][16][36] = "e"
P["head"][18][31] = "S"  # Nase
for x, c in ((29, "S"), (30, "K"), (31, "K"), (32, "K"), (33, "S")):
    P["head"][19][x] = c  # Mund
P["head"][20][30] = P["head"][20][32] = "w"  # Eckzähne
P["head"][20][31] = "S"

# Spitzohren (links im Bild), rechts gespiegelt
EAR = {(19, 12): "K", (19, 13): "K", (20, 13): "S", (21, 13): "K",
       (20, 14): "K", (21, 14): "S", (22, 14): "W",
       (20, 15): "K", (21, 15): "s", (22, 15): "S",
       (21, 16): "K", (22, 16): "s", (22, 17): "K"}
for (x, y), c in EAR.items():
    P["head"][y][x] = c
    P["head"][y][BODY - x] = c

# ------------------------------------------------------------ Oberkörper
# Hals (meist vom Kinn verdeckt)
for y in range(18, 22):
    for x in range(28, 35):
        P["torso"][y][x] = "S"
    P["torso"][y][27] = P["torso"][y][35] = "K"

# Gehrock: Schultern bis Taille (unter den Armen aufgefüllt)
COAT = sym_ranges({22: (23, 31), 23: (22, 31), **{y: (22, 31) for y in range(24, 31)},
                   31: (23, 31)})
coat = ranges_to_set(COAT)
fill("torso", coat, lambda x, y: "g" if (x in (24, 38) or abs(x - 31) == 5) and y > 23 else "d")


def v_half(y):
    """Halbe Breite des V-Ausschnitts (Revers) in Zeile y."""
    return 4 - (y - 22) // 3


for y in range(22, 32):
    hw = v_half(y)
    for x in range(31 - hw, 32 + hw):
        P["torso"][y][x] = "B"  # Weste (dunkelrot)
    P["torso"][y][31 - hw - 1] = P["torso"][y][31 + hw + 1] = "K"  # Revers-Kante
    if y >= 24:
        P["torso"][y][31 - hw - 2] = P["torso"][y][31 + hw + 2] = "g"  # Revers glänzt
# Weste: Lichtkante + Knöpfe
for y in range(25, 32):
    hw = v_half(y)
    if hw >= 2:
        P["torso"][y][31 - hw] = "R"
for y in (27, 29):
    P["torso"][y][31] = "m"
# Hemdkragen (weiß) und Krawatte (rot)
put("torso", {(27, 22): "W", (28, 22): "W", (29, 22): "S", (30, 22): "e", (31, 22): "e",
              (32, 22): "e", (33, 22): "S", (34, 22): "W", (35, 22): "W",
              (27, 23): "S", (28, 23): "W", (29, 23): "e", (30, 23): "i", (31, 23): "e",
              (32, 23): "e", (33, 23): "e", (34, 23): "W", (35, 23): "S",
              (29, 24): "E", (30, 24): "e", (31, 24): "i", (32, 24): "e", (33, 24): "E",
              (30, 25): "E", (31, 25): "e", (32, 25): "E", (31, 26): "E"})
# Taille: Naht
for x in range(25, 38):
    if P["torso"][31][x] in "dg":
        P["torso"][31][x] = "k"

# Stehkragen: steht hinter dem Hals, innen rot gefüttert
COLLAR_L = {(24, 16): "K", (23, 17): "K", (24, 17): "r", (25, 17): "K",
            (22, 18): "K", (23, 18): "r", (24, 18): "r", (25, 18): "K",
            (22, 19): "K", (23, 19): "R", (24, 19): "r", (25, 19): "r", (26, 19): "K",
            (21, 20): "K", (22, 20): "d", (23, 20): "R", (24, 20): "r", (25, 20): "r", (26, 20): "K",
            (21, 21): "K", (22, 21): "d", (23, 21): "g", (24, 21): "R", (25, 21): "r", (26, 21): "K"}
for (x, y), c in COLLAR_L.items():
    P["torso"][y][x] = c
    P["torso"][y][BODY - x] = c

# ------------------------------------------------------------ Arme (sein rechter = links im Bild)
UPPER = {22: (21, 25), 23: (20, 26), 24: (19, 26), **{y: (19, 25) for y in range(25, 32)}}
fill("upper_arm_R", ranges_to_set(UPPER),
     lambda x, y: "g" if x in (21, 22) and y >= 23 else "d" if x == 24 else "g" if y == 23 else "d")
P["upper_arm_R"][23][22] = "h"  # Schulterpolster glänzt
# Unterarm: Ärmel, rote Manschette, weiße Spitze, Hand
block(P["forearm_R"], 18, 32, """
.KdgggdK
.KdgggdK
.KdggddK
KRrrrrRK
KbRRRRbK
.KWwwWK.
.KWWSK..
.KWsSK..
..KWK...
..KKK...
""")

P["upper_arm_L"] = mirror(P["upper_arm_R"], BODY)
P["forearm_L"] = mirror(P["forearm_R"], BODY)

# ------------------------------------------------------------ Rockschöße (Gehrock, vorne offen)


def outer(y):
    return round(22 - (y - 32) * 4 / 18)


def inner(y):
    return 31 if y < 34 else 30 - (y - 34) * 3 // 12


def hem(x):
    """Unterkante: außen waagerecht (Zeile 50), zur Öffnung hin rund hochgezogen."""
    return {27: 46, 26: 47, 25: 48, 24: 49}.get(x, 50 if x < 27 else 46)


panel = {(x, y) for y in range(32, 51) for x in range(outer(y), inner(y) + 1) if y <= hem(x)}
panel |= {(BODY - x, y) for x, y in panel}
bottom = {}
for x, y in panel:
    bottom[x] = max(bottom.get(x, 0), y)


def coat_fold(x, y):
    f = (x - 31) / ((y - 28) * 0.42 + 2.5) * 2.2  # Falten fächern nach unten auf
    t = f - math.floor(f)
    return "k" if t < 0.16 else "d" if t < 0.5 else "g" if t < 0.8 else "d"


edge = fill("skirt_front", panel, coat_fold)
for x, y in panel:
    xi = inner(y)
    if y >= 35 and (x == xi or x == BODY - xi):
        P["skirt_front"][y][x] = "R" if y % 4 == 0 else "r"  # Futter an der Öffnung
    elif y == bottom[x] - 1 and abs(x - 31) >= 5 and y >= 46:
        P["skirt_front"][y][x] = "R"  # Futter blitzt am Saum
# Taille unter der Naht dunkel
for x in range(23, 40):
    if (x, 32) in panel and P["skirt_front"][32][x] != "K":
        P["skirt_front"][32][x] = "k"

# Rückseite: rotes Futter hinter den Beinen
back = ranges_to_set({y: (23, 39) for y in range(33, 51)})
fill("skirt_back", back,
     lambda x, y: "d" if y < 39 else ("B" if x % 4 == 1 and y < 42 else "R" if x % 4 == 1 else "r"))

# ------------------------------------------------------------ Beine (Hose)
thigh = ranges_to_set({y: (25, 30) for y in range(33, 46)})
fill("thigh_R", thigh, lambda x, y: "g" if x == 27 else "d")
shin = ranges_to_set({**{y: (24, 29) for y in range(45, 55)}, 55: (25, 28), 56: (25, 28)})
fill("shin_R", shin, lambda x, y: "g" if x == 26 else "d")
for y in (55, 56):  # unten ohne Umriss: der Stiefel setzt hier an
    for x in range(25, 29):
        P["shin_R"][y][x] = "g" if x == 26 else "d"
P["thigh_L"] = mirror(P["thigh_R"], LEG)
P["shin_L"] = mirror(P["shin_R"], LEG)

PIVOTS = {
    "root": [31, 60], "pelvis": [31, 33], "torso": [31, 32],
    "head": [31, 21], "hair_front": [31, 6], "hair_back": [31, 6],
    "upper_arm_R": [23.5, 24], "upper_arm_L": [38.5, 24],
    "forearm_R": [22.5, 31.5], "forearm_L": [39.5, 31.5],
    "skirt_front": [31, 32], "skirt_back": [31, 33],
    "thigh_R": [27.5, 34], "thigh_L": [34.5, 34],
    "shin_R": [27, 45], "shin_L": [35, 45],
}
replace_feet(P, PIVOTS, "front", mirror_left=True)

ORDER = ["hair_back", "skirt_back", "thigh_R", "thigh_L", "shin_R", "shin_L",
         "foot_R", "foot_L", "skirt_front", "torso",
         "upper_arm_R", "upper_arm_L", "forearm_R", "forearm_L", "head", "hair_front"]
os.makedirs("char", exist_ok=True)
save({"pal": PAL, "order": ORDER, "pivots": PIVOTS, "parts": P}, "char/S.json")
print("gespeichert: char/S.json")
