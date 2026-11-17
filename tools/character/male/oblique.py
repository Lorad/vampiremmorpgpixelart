"""Vampir (männlich) – Kopf und Oberkörper der Schrägansichten, von Hand gezeichnet.

Wird von male/diagonals.py nach dem Drehen aufgerufen und ersetzt in Südost und
Nordost die Teile hair_back, hair_front, head und torso. Arme, Gehrock und
Beine bleiben aus der Drehung.

Südost: Gesicht nach rechts unten gedreht, sein rechtes Ohr links am Kopf,
das ferne Auge schmaler, Weste und Krawatte rücken nach rechts.
Nordost: Hinterkopf, sein rechtes Ohr rechts, Stehkragen von hinten mit einem
Streifen rotem Futter an der offenen Seite.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import blank, block, load, save  # noqa: E402
from draw import edge_of, ranges_to_set  # noqa: E402
from rotate import outline_group  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collar import back_collar  # noqa: E402

INNER = ((1, 0), (-1, 0), (0, -1))


def shaded(pts, fn):
    """Fläche mit Umriss (K) und dunkler Innenkante (k) wie bei den Haaren der Vampirin."""
    g = blank()
    edge = edge_of(pts)
    for x, y in pts:
        g[y][x] = "K" if (x, y) in edge else fn(x, y)
    for x, y in pts:
        if (x, y) not in edge and g[y][x] in "ph" and any(
                (x + dx, y + dy) in edge for dx, dy in INNER):
            g[y][x] = "k"
    return g


def put(g, pts):
    for (x, y), c in pts.items():
        g[y][x] = c


def skull_under(hair_pts, rows):
    """Dunkler Schädel unter den Haaren (falls die Haare beim Laufen nachschwingen)."""
    g = blank()
    for x, y in hair_pts:
        if y in rows and all((x + dx, y + dy) in hair_pts for dx, dy in INNER):
            g[y][x] = "k"
    return g


# ============================================================ Südost
se = load("char/SE.json")
P = se["parts"]

HAIR_SE = ranges_to_set({
    1: (27, 33), 2: (25, 35), 3: (23, 37), 4: (22, 38), 5: (21, 39), 6: (21, 39),
    7: (20, 40), 8: (20, 40), 9: (20, 40),
    10: [(20, 28), (32, 34), (38, 40)], 11: [(20, 27), (33, 33), (39, 40)],
    12: [(20, 26), (40, 40)], 13: (20, 23), 14: (20, 23), 15: (20, 23), 16: (21, 23),
    17: (21, 23), 18: (22, 23),
})


def se_hair(x, y):
    if x <= 25 and y >= 10:  # Hinterkopf hinter dem Ohr: dunkel, Strähnen nach hinten
        return "k" if (x + y) % 3 == 0 else "p"
    a = math.atan2(x - 34, 15 - y)  # Strähnen laufen vom Haaransatz nach oben/hinten
    t = (a * 3.2 + 0.5) % 1
    if t < 0.2:
        return "k"
    if y <= 7 and 0.3 < t < 0.75:
        return "h"
    return "p"


P["hair_back"] = shaded(HAIR_SE, se_hair)
P["hair_front"] = blank()
for x, y in HAIR_SE:  # vorderes Haar: Oberkopf und Haaransatz, das Ohr bleibt frei
    if y <= 9 or x >= 27:
        P["hair_front"][y][x] = P["hair_back"][y][x]

head = skull_under({(x, y) for x, y in HAIR_SE if y <= 9 or x >= 27}, range(2, 13))
FACE_SE = ranges_to_set({
    10: [(29, 31), (35, 37)], 11: [(28, 32), (34, 38)], 12: (27, 39), 13: (27, 39),
    14: (27, 39), 15: (27, 39), 16: (27, 40), 17: (27, 40), 18: (28, 39), 19: (29, 38),
    20: (30, 37),
})
for x, y in FACE_SE:
    head[y][x] = "W"
for y in range(12, 21):  # Umriss rechts (Wange/Profil)
    xs = [x for x, yy in FACE_SE if yy == y]
    head[y][max(xs) + 1] = "K"
put(head, {(27, 18): "K", (28, 19): "K", (29, 20): "K"})  # Kiefer links
for x in range(30, 38):
    head[21][x] = "K"  # Kinn
put(head, {
    # Brauen: streng, innen tiefer
    (28, 12): "K", (29, 12): "K", (30, 13): "K", (31, 13): "K",
    (35, 13): "K", (36, 12): "K", (37, 12): "K",
    # nahes Auge (sein rechtes)
    (28, 15): "K", (29, 15): "K", (30, 15): "K", (31, 15): "K",
    (28, 16): "K", (29, 16): "e", (30, 16): "w", (31, 16): "E",
    (29, 17): "E", (30, 17): "e", (31, 17): "E",
    # fernes Auge, schmaler
    (35, 15): "K", (36, 15): "K", (37, 15): "K",
    (35, 16): "E", (36, 16): "w", (37, 16): "K", (35, 17): "E", (36, 17): "e",
    # Nase, Mund mit Eckzähnen, Wangenschatten
    (37, 17): "S", (37, 18): "S",
    (33, 19): "K", (34, 19): "K", (35, 19): "K", (36, 19): "S",
    (33, 20): "w", (34, 20): "S", (35, 20): "w",
    (27, 16): "S", (27, 17): "S", (28, 18): "S", (29, 19): "S", (30, 20): "S",
    (40, 16): "S", (40, 17): "S",
})
# sein rechtes Spitzohr (zeigt nach hinten oben)
put(head, {(22, 11): "K", (22, 12): "K", (23, 12): "W", (24, 12): "K",
           (23, 13): "K", (24, 13): "W", (25, 13): "W", (26, 13): "K",
           (23, 14): "K", (24, 14): "S", (25, 14): "W", (26, 14): "W",
           (24, 15): "K", (25, 15): "S", (26, 15): "W",
           (25, 16): "K", (26, 16): "S", (26, 17): "K"})
P["head"] = head

# Rockschoß: der hintere Zipfel aus der Seitenansicht ragt links als Haken
# heraus – abschneiden und den Umriss neu ziehen
for part in ("skirt_front", "skirt_back"):
    for y in range(46, 62):
        for x in range(0, 22):
            P[part][y][x] = "."
outline_group(P, ["skirt_front", "skirt_back"])

torso = blank()
block(torso, 20, 15, """
....K.................
...KrK................
..KrrK................
..KRrrK..KSSSSSK.KrK..
..KdRrK..KSSSSSK.KRdK.
.KdgRrK..KSSSSSK.KrdK.
.KdgdRK..KSSSSSK..KdK.
..KddddddKWWSeeeSWKdK.
.KdggggddKSWeieeWKdgK.
.KdggggddgKBEeiEBKdgK.
.KdggggddgKRBEeEBKdgK.
.KdggggdddgKRBEBKddgK.
.KdggggdddgKRBmBKddgK.
.KdggggdddgKRBBBKddgK.
.KdggggdddggKRmKdddgK.
.KdggggdddggKRBKdddgK.
..KkkkkkkkkkKBKkkkkK..
""")
P["torso"] = torso
save(se, "char/SE.json")

# ============================================================ Nordost
ne = load("char/NE.json")
P = ne["parts"]
HAIR_NE = ranges_to_set({
    1: (26, 33), 2: (24, 35), 3: (23, 37), 4: (22, 38), 5: (21, 39), 6: (21, 39),
    7: (20, 39), **{y: (20, 40) for y in range(8, 16)}, 16: (21, 39), 17: (22, 38),
    18: (23, 37), 19: (24, 36),
})


def ne_hair(x, y):
    a = math.atan2(x - 29, y + 4)  # Strähnen laufen vom Wirbel nach unten zum Nacken
    t = (a * 5.0 + 0.25 * math.sin(y / 2.2)) % 1
    c = "k" if t < 0.22 else "p"
    r = math.hypot((x - 29) * 0.85, y - 9)
    if 6.0 < r < 7.6 and y < 10 and c != "k":
        c = "h"  # Glanzring am Hinterkopf
    if y >= 16 and c == "p" and (x + y) % 3 == 0:
        c = "k"
    return c


P["hair_back"] = shaded(HAIR_NE, ne_hair)
P["hair_front"] = blank()
head = blank()
# sein rechtes Spitzohr von hinten (zeigt nach hinten oben, rechts am Kopf)
put(head, {(42, 11): "K", (42, 12): "K", (41, 12): "S", (40, 12): "K",
           (41, 13): "K", (40, 13): "S", (39, 13): "s", (38, 13): "K",
           (41, 14): "K", (40, 14): "s", (39, 14): "s",
           (40, 15): "K", (39, 15): "s", (39, 16): "K"})
P["head"] = head

torso = blank()
block(torso, 20, 22, """
..KKKKKKKKKKKKKKKKKK..
.KdddggdddddddgggdddK.
.KddgggdddddddggggddK.
.KdddddddkddddddddddK.
.KdddddddkddddddddgdK.
.KdddddddkddddddddgdK.
.KdddddddkddddddddgdK.
.KdddddddkddddddddddK.
.KdddddddkddddddddddK.
..KkkkkkkkkkkkkkkkkK..
""")
back_collar(torso, 23, 39, open_right=True)
P["torso"] = torso
save(ne, "char/NE.json")
