"""Vampirin – Frontansicht (Süd) in Skelett-Teile zerlegen.

Quelle: ref/front_sym.json (bereinigte Referenz, rechter Arm gespiegelt → Idle).
Jedes sichtbare Pixel wird genau einem Teil zugeordnet. Verdeckte Bereiche
werden "darunter" aufgefüllt (nur wo das Teil noch transparent ist), damit beim
Animieren keine Löcher entstehen.
"""
import json

W = H = 62
AXIS2 = 62  # Spiegelung Körper: x' = 62 - x (Körpermitte x = 31)

src = json.load(open("ref/front_sym.json"))
PAL = src["pal"]
M = src["grid"]

PARTS = [  # Zeichenreihenfolge (hinten → vorne)
    "hair_back", "skirt_back",
    "thigh_L", "thigh_R", "shin_L", "shin_R", "foot_L", "foot_R",
    "skirt_front", "torso",
    "upper_arm_L", "upper_arm_R", "forearm_L", "forearm_R",
    "head", "hair_front",
]

label = [[None] * W for _ in range(H)]


def lab(part, y, x0, x1):
    for x in range(x0, x1 + 1):
        if M[y][x] != "." and label[y][x] is None:
            label[y][x] = part


def lab_mirror(part_l, part_r, ranges):
    for y, (x0, x1) in ranges.items():
        lab(part_l, y, x0, x1)
        lab(part_r, y, AXIS2 - x1, AXIS2 - x0)


# ------------------------------------------------------------ Kopf
HEAD = {11: (30, 33), 12: (30, 34), 13: (29, 34), 14: (28, 35), 15: (24, 39),
        16: (24, 39), 17: (24, 38), 18: (24, 36), 19: (25, 36), 20: (25, 36), 21: (25, 36)}
for y, (x0, x1) in HEAD.items():
    lab("head", y, x0, x1)

# ------------------------------------------------------------ Arme (links, rechts gespiegelt)
UPPER = {22: (22, 24), 23: (21, 25), 24: (21, 24), 25: (21, 25), 26: (22, 26), 27: (22, 26),
         28: (21, 27), 29: (21, 26), 30: (19, 26), 31: (18, 26)}
FORE = {32: (14, 25), 33: (14, 25), 34: (14, 26), 35: (15, 25), 36: (16, 25), 37: (17, 25),
        38: (18, 25), 39: (18, 22), 40: (18, 21), 41: (18, 20)}
lab_mirror("upper_arm_L", "upper_arm_R", UPPER)
lab_mirror("forearm_L", "forearm_R", FORE)

# ------------------------------------------------------------ Oberkörper (Hals bis Schärpe)
TORSO = {22: (25, 37), 23: (26, 36), 24: (25, 37), 25: (26, 36), 26: (27, 35), 27: (27, 35),
         28: (28, 34), 29: (27, 35), 30: (27, 35), 31: (27, 35)}
for y, (x0, x1) in TORSO.items():
    lab("torso", y, x0, x1)

# ------------------------------------------------------------ Beine
LEG_L = {41: (29, 29), 42: (25, 30), 43: (24, 30), 44: (24, 30), 45: (24, 30), 46: (24, 30),
         47: (24, 29), 48: (23, 29), 49: (23, 29), 50: (23, 29), 51: (23, 28), 52: (23, 28),
         53: (23, 28), 54: (22, 28), 55: (20, 28), 56: (21, 28), 57: (21, 27), 58: (20, 27),
         59: (20, 26), 60: (20, 24)}
LEG_R = {41: (33, 33), 42: (31, 37), 43: (31, 37), 44: (31, 37), 45: (32, 37), 46: (32, 37),
         47: (32, 38), 48: (32, 38), 49: (32, 38), 50: (33, 38), 51: (33, 38), 52: (33, 38),
         53: (33, 40), 54: (33, 42), 55: (33, 40), 56: (34, 41), 57: (35, 42), 58: (37, 42)}
for y, (x0, x1) in LEG_L.items():
    lab("thigh_L" if y <= 44 else "shin_L" if y <= 54 else "foot_L", y, x0, x1)
for y, (x0, x1) in LEG_R.items():
    lab("thigh_R" if y <= 44 else "shin_R" if y <= 53 else "foot_R", y, x0, x1)

# ------------------------------------------------------------ Rock (Rückseite zwischen den Beinen)
SKIRT_BACK = {45: (31, 31), 46: (31, 31), 47: (30, 31), 48: (30, 31), 49: (30, 31),
              50: (30, 32), 51: (29, 32), 52: (29, 32)}
for y, (x0, x1) in SKIRT_BACK.items():
    lab("skirt_back", y, x0, x1)

# ------------------------------------------------------------ Rest: Haare oben, Rock unten
for y in range(H):
    for x in range(W):
        if M[y][x] != "." and label[y][x] is None:
            label[y][x] = "hair" if y <= 31 else "skirt_front"

# ------------------------------------------------------------ Teile extrahieren
parts = {p: [["."] * W for _ in range(H)] for p in PARTS}
for y in range(H):
    for x in range(W):
        p = label[y][x]
        if p is None:
            continue
        if p == "hair":
            parts["hair_back"][y][x] = M[y][x]
            if y <= 21:
                parts["hair_front"][y][x] = M[y][x]
        else:
            parts[p][y][x] = M[y][x]


def under(part, y, x0, x1, ch):
    """Malt verdeckte Pixel (nur wo das Teil noch leer ist)."""
    g = parts[part]
    for x in range(x0, x1 + 1):
        if 0 <= x < W and g[y][x] == ".":
            g[y][x] = ch


def under_row(part, y, x0, s):
    for i, ch in enumerate(s):
        if ch != " ":
            under(part, y, x0 + i, x0 + i, ch)


def under_mirror(part_l, part_r, y, x0, x1, ch):
    under(part_l, y, x0, x1, ch)
    under(part_r, y, AXIS2 - x1, AXIS2 - x0, ch)


# Haare hinten: Fläche hinter Kopf und Oberkörper schließen
for y in range(2, 32):
    xs = [x for x in range(W) if parts["hair_back"][y][x] != "."]
    if xs:
        under("hair_back", y, min(xs), max(xs), "k")

# Kopf: Schädel unter dem Pony dunkel (Haaransatz), Hals unter dem Kinn
for y in range(4, 15):
    xs = [x for x in range(W) if parts["hair_front"][y][x] != "."]
    if xs:
        under("head", y, min(xs) + 1, max(xs) - 1, "k")

# Oberkörper: Hals hinter dem Kinn, Schultern/Seiten unter den Oberarmen
for y in (19, 20, 21):
    under("torso", y, 27, 35, "S")
    under("torso", y, 26, 26, "K")
    under("torso", y, 36, 36, "K")
TORSO_EDGE = {22: 23, 23: 22, 24: 22, 25: 22, 26: 23, 27: 23, 28: 25, 29: 26, 30: 26, 31: 26}
for y, ex in TORSO_EDGE.items():
    under_mirror("torso", "torso", y, ex, ex, "K")
    under_mirror("torso", "torso", y, ex + 1, 30, "d")

# Rock vorne: Hüfte unter den Ärmeln
for y in range(32, 39):
    ex = 26 - round((y - 32) * 4 / 7)
    under_mirror("skirt_front", "skirt_front", y, ex, ex, "K")
    under_mirror("skirt_front", "skirt_front", y, ex + 1, 26, "d")
for y in (39, 40, 41):
    under_mirror("skirt_front", "skirt_front", y, 21, 23, "g")

# Rock hinten: rotes Futter hinter den Beinen, oben dunkel
for y in range(33, 41):
    under("skirt_back", y, 25, 37, "d")
for y in range(41, 52):
    for x in range(24, 39):
        # senkrechte Stofffalten (in den Schrägansichten sichtbar)
        under("skirt_back", y, x, x, "B" if x % 4 == 2 and y < 44 else "R" if x % 4 == 2 else "r")
under("skirt_back", 52, 24, 38, "K")

# Oberschenkel bis zur Hüfte (unter dem Rock) und ins Knie (unter dem Stiefel)
for y in range(33, 42):
    under("thigh_L", y, 25, 25, "K"); under("thigh_L", y, 26, 29, "S"); under("thigh_L", y, 30, 30, "K")
    under("thigh_R", y, 31, 31, "K"); under("thigh_R", y, 32, 36, "S"); under("thigh_R", y, 37, 37, "K")
for y in (45, 46):
    under("thigh_L", y, 25, 29, "m")
    under("thigh_R", y, 32, 36, "m")

# Schienbein reicht unter den Fuß
for y in (55, 56):
    under("shin_L", y, 23, 27, "d")
for y in (54, 55):
    under("shin_R", y, 34, 38, "k")

# ------------------------------------------------------------ Prüfen & speichern
def composite(order=PARTS):
    out = [["."] * W for _ in range(H)]
    for p in order:
        g = parts[p]
        for y in range(H):
            for x in range(W):
                if g[y][x] != ".":
                    out[y][x] = g[y][x]
    return out


comp = composite()
diff = [(x, y, M[y][x], comp[y][x]) for y in range(H) for x in range(W) if comp[y][x] != M[y][x]]
print("Abweichungen zur Vorlage:", len(diff))
for d in diff[:40]:
    print("  ", d)

PIVOTS = {  # Gelenke in Leinwand-Koordinaten (62×62)
    "root": (31, 60),
    "pelvis": (31, 33),
    "torso": (31, 32),
    "head": (30.5, 21),
    "hair_front": (30.5, 6),
    "hair_back": (30.5, 6),
    "upper_arm_L": (23.5, 24), "upper_arm_R": (38.5, 24),
    "forearm_L": (22.5, 31.5), "forearm_R": (39.5, 31.5),
    "skirt_front": (31, 32), "skirt_back": (31, 33),
    "thigh_L": (27.5, 34), "thigh_R": (34, 34),
    "shin_L": (27, 45), "shin_R": (34.5, 45),
    "foot_L": (25, 55), "foot_R": (36, 54),
}
json.dump({"pal": PAL, "order": PARTS, "pivots": PIVOTS,
           "parts": {p: ["".join(r) for r in parts[p]] for p in PARTS}},
          open("char/front_parts.json", "w"))
print("gespeichert: char/front_parts.json")

# Bildseite → anatomische Seite (Frontansicht: links im Bild = ihr rechter Arm/Bein)
def _anatomical(n):
    return n.replace("_L", "_TMP").replace("_R", "_L").replace("_TMP", "_R")


_d = json.load(open("char/front_parts.json"))
json.dump({"pal": _d["pal"], "order": [_anatomical(k) for k in _d["order"]],
           "pivots": {_anatomical(k): v for k, v in _d["pivots"].items()},
           "parts": {_anatomical(k): v for k, v in _d["parts"].items()}},
          open("char/S.json", "w"))
print("gespeichert: char/S.json")

# ------------------------------------------------------------ Füße in Laufrichtung
# Für die Laufanimation stehen beide Füße gerade mit der Spitze zur Kamera.
# Das linke Bein (rechts im Bild, in der Vorlage nach außen gedreht) wird
# durch das gespiegelte rechte ersetzt; beide bekommen den Front-Stiefel.
import os  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, mirror, save  # noqa: E402
from feet import replace_feet  # noqa: E402

LEG_AXIS = 61  # Beine liegen symmetrisch um x = 31,0 (zwischen Pixel 30 und 31)
_s = load("char/S.json")
for _limb in ("thigh", "shin"):
    _s["parts"][f"{_limb}_L"] = mirror(_s["parts"][f"{_limb}_R"], LEG_AXIS)
    _x, _y = _s["pivots"][f"{_limb}_R"]
    _s["pivots"][f"{_limb}_L"] = [LEG_AXIS + 1 - _x, _y]
replace_feet(_s["parts"], _s["pivots"], "front", mirror_left=True)
save(_s, "char/S.json")
print("Füße: Front-Stiefel, gerader Stand")
