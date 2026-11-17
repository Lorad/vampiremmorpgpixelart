"""Vampir (männlich) – Rückansicht (Nord), abgeleitet aus der Frontansicht.

Arme und Beine werden gespiegelt (die Namen bleiben: sein rechter Arm ist von
hinten rechts im Bild). Neu gezeichnet: Hinterkopf, beide Spitzohren, Rücken
des Gehrocks mit Stehkragen und Gehschlitz (rotes Futter blitzt durch).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import blank, load, mirror, pixels, save, union  # noqa: E402
from draw import edge_of, ranges_to_set  # noqa: E402
from feet import replace_feet  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collar import back_collar  # noqa: E402

S = load("char/S.json")
P = S["parts"]
BODY = 62
N = {p: blank() for p in P}

# Gliedmaßen gespiegelt
for p in ("upper_arm_R", "forearm_R", "upper_arm_L", "forearm_L"):
    N[p] = mirror(P[p], BODY)
for p in ("thigh_R", "shin_R", "thigh_L", "shin_L"):
    N[p] = mirror(P[p], 61)

# ------------------------------------------------------------ Hinterkopf
# Silhouette wie von vorne, nur ist jetzt alles Haar (Gesicht → Hinterkopf)
sil = set(pixels(union(P["hair_back"], P["hair_front"])))
sil |= {(x, y) for x, y in pixels(P["head"]) if 22 <= x <= 40 and y <= 20}
sil = {(x, y) for x, y in sil if y <= 19 and 21 <= x <= 41}
for y in range(10, 18):  # Hinterkopf füllen (Ohren gehören zum Kopf-Teil)
    for x in range(21, 42):
        sil.add((x, y))
for y, (x0, x1) in {18: (22, 40), 19: (23, 39), 20: (24, 38)}.items():
    for x in range(x0, x1 + 1):
        sil.add((x, y))
edge = edge_of(sil)
hair = blank()
for x, y in sil:
    # Strähnen laufen vom Wirbel oben nach unten zum Nacken zusammen
    a = math.atan2(x - 31, y + 4)
    s = a * 5.0 + 0.25 * math.sin(y / 2.2)
    t = s - math.floor(s)
    c = "k" if t < 0.22 else "p"
    r = math.hypot((x - 31) * 0.85, y - 9)
    if 6.0 < r < 7.6 and y < 10 and c != "k":
        c = "h"  # Glanzring am Hinterkopf
    if y >= 16 and c == "p" and (x + y) % 3 == 0:
        c = "k"  # zum Nacken hin dunkler
    hair[y][x] = "K" if (x, y) in edge else c
for x, y in sil:  # zweite, dunkle Innenkante
    if (x, y) not in edge and hair[y][x] in "ph" and any(
            (x + dx, y + dy) in edge for dx, dy in ((1, 0), (-1, 0), (0, -1))):
        hair[y][x] = "k"
N["hair_back"] = hair

# ------------------------------------------------------------ Spitzohren (Rückseite)
EAR = {(19, 12): "K", (19, 13): "K", (20, 13): "S", (21, 13): "K",
       (20, 14): "K", (21, 14): "S", (22, 14): "S",
       (20, 15): "K", (21, 15): "s", (22, 15): "s",
       (21, 16): "K", (22, 16): "s", (22, 17): "K"}
for (x, y), c in EAR.items():
    N["head"][y][x] = c
    N["head"][y][BODY - x] = c

# ------------------------------------------------------------ Rücken mit Stehkragen
coat = ranges_to_set({y: (22, 40) for y in range(22, 32)})
coat |= ranges_to_set({22: (23, 39)})
cedge = edge_of(coat)
torso = blank()
for x, y in coat:
    c = "d"
    if y in (23, 24) and abs(x - 31) in (4, 5, 6):
        c = "g"  # Schulterblätter glänzen
    if x == 31 and y >= 25:
        c = "k"  # Rückennaht
    if y == 31:
        c = "k"  # Taille
    torso[y][x] = "K" if (x, y) in cedge else c
# Stehkragen: hoher Bund im Nacken, oben blitzt das rote Futter
back_collar(torso, 23, 39)
N["torso"] = torso

# ------------------------------------------------------------ Gehrock hinten (geschlossen)
sil = set(pixels(mirror(union(P["skirt_front"], P["skirt_back"]), BODY)))
sedge = edge_of(sil)
skirt = blank()
for x, y in sil:
    f = (x - 31) / ((y - 28) * 0.42 + 2.5) * 2.2  # Falten fächern nach unten auf
    t = f - math.floor(f)
    c = "k" if t < 0.16 else "d" if t < 0.5 else "g" if t < 0.8 else "d"
    if y <= 33:
        c = "k" if y == 32 else ("d" if c == "g" else c)
    skirt[y][x] = "K" if (x, y) in sedge else c
# Gehschlitz in der Mitte: rotes Futter blitzt durch
bottom = max(y for x, y in sil if x == 31)
for y in range(43, bottom):
    skirt[y][30], skirt[y][31], skirt[y][32] = "k", ("R" if y % 3 == 0 else "r"), "k"
N["skirt_back"] = skirt

ORDER = ["skirt_front", "thigh_R", "thigh_L", "shin_R", "shin_L", "foot_R", "foot_L",
         "skirt_back", "hair_front", "hair_back", "torso",
         "upper_arm_R", "upper_arm_L", "forearm_R", "forearm_L", "head"]
piv = {k: [BODY - x, y] for k, (x, y) in S["pivots"].items()}
replace_feet(N, piv, "back", mirror_left=True)  # von hinten sieht man die Absätze
save({"pal": S["pal"], "order": ORDER, "pivots": piv, "parts": N}, "char/N.json")
print("gespeichert: char/N.json")
