"""Schrägansichten (SE, NE) durch Drehen elliptischer Querschnitte.

Jede Teile-Gruppe (Kopf, Oberkörper, Rock) wird pro Pixelzeile als Ellipse
modelliert: Breite a / Mitte X aus der Front- bzw. Rückansicht (S/N), Tiefe b /
Mitte Z aus der Seitenansicht (E). Für den Zielwinkel theta wird jedes Ziel-Pixel
auf einen Oberflächenwinkel phi zurückgerechnet und aus der Ansicht übernommen,
die diese Stelle am frontalsten zeigt. Kein Weichzeichnen → Pixel-Stil bleibt.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import H, W, blank, load, pixels, save  # noqa: E402
from feet import replace_feet  # noqa: E402

C0 = 31.0  # Körperachse
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
GROUPS = {
    "head": ["hair_back", "hair_front", "head"],
    "torso": ["torso"],
    "skirt": ["skirt_front", "skirt_back"],
}


def row_extent(parts, names, y):
    xs = [x for n in names for x in range(W) if parts[n][y][x] != "."]
    if not xs:
        return None
    return min(xs), max(xs) + 1


def rotate_group(views, names, theta_deg, out, pick, partmap):
    th = math.radians(theta_deg)
    for y in range(H):
        ep = {}
        for v, d in views.items():
            src_names = [n for n in names if partmap[v].get(n, n)]
            e = row_extent(d["parts"], src_names, y)
            if e:
                ep[v] = ((e[0] + e[1]) / 2, (e[1] - e[0]) / 2)
        if not ep:
            continue
        if "S" in ep:
            a, X = ep["S"][1], ep["S"][0] - C0
        elif "N" in ep:
            a, X = ep["N"][1], C0 - ep["N"][0]
        else:
            a, X = ep["E"][1], 0.0
        if "E" in ep:
            b, Z = ep["E"][1], ep["E"][0] - C0
        else:
            b, Z = a * 0.8, 0.0
        cx = C0 + X * math.cos(th) + Z * math.sin(th)
        best = {}
        for i in range(1440):
            phi = -math.pi + 2 * math.pi * i / 1440
            xp = cx + a * math.sin(phi) * math.cos(th) + b * math.cos(phi) * math.sin(th)
            zp = -a * math.sin(phi) * math.sin(th) + b * math.cos(phi) * math.cos(th)
            if zp <= 0:
                continue
            px = math.floor(xp)
            err = abs(xp - (px + 0.5))
            if px not in best or err < best[px][0]:
                best[px] = (err, phi)
        for px, (err, phi) in best.items():
            if not (0 <= px < W):
                continue
            src = pick(math.degrees(phi))
            if src not in views or src not in ep:
                continue
            c, r = ep[src]
            if src == "S":
                xs = c + r * math.sin(phi)
            elif src == "E":
                xs = c + r * math.cos(phi)
            else:
                xs = c - r * math.sin(phi)
            sx = min(W - 1, max(0, math.floor(xs)))
            for n in names:
                target = partmap[src].get(n, n)
                if not target:
                    continue
                if src == "E" and n == "head" and (sx > 31 or y < 13):
                    continue  # vom Profil nur das Ohr übernehmen
                ch = views[src]["parts"][n][y][sx]
                if ch != ".":
                    out[target][y][px] = ch


def remove_fringes(g, rounds=2):
    for _ in range(rounds):
        kill = [(x, y) for x, y in pixels(g)
                if sum(1 for dx, dy in N4 if 0 <= x + dx < W and 0 <= y + dy < H
                       and g[y + dy][x + dx] != ".") < 2]
        for x, y in kill:
            g[y][x] = "."


def outline_group(parts, names):
    """Umriss nur am Außenrand der ganzen Gruppe (keine Linien zwischen den Ebenen)."""
    occ = set()
    for n in names:
        occ.update(pixels(parts[n]))
    for n in names:
        g = parts[n]
        for x, y in pixels(g):
            if any((x + dx, y + dy) not in occ for dx, dy in N4):
                g[y][x] = "K"


def clean_hem(parts, names, y_from=44):
    """Rocksaum aufräumen: Löcher füllen, Saumlinie glätten, schmale Lücken schließen.

    Beim Drehen treffen die spitzen Rockzipfel der Frontansicht auf den schrägen
    Saum der Seitenansicht – das ergibt Fransen und Löcher am unteren Rand.
    """
    def owner(x, y):
        for n in names:  # vordere Ebene zuerst
            if parts[n][y][x] != ".":
                return n
        return None

    def fill_from(n, x, y, sx, sy):
        c = parts[n][sy][sx]
        parts[n][y][x] = "d" if c == "K" else c  # Umriss wird später neu gezogen

    cols = {}
    for n in names:
        for x, y in pixels(parts[n]):
            cols.setdefault(x, set()).add(y)
    if not cols:
        return
    bottom = {x: max(ys) for x, ys in cols.items()}
    smooth = {}
    for x in bottom:
        win = sorted(bottom[k] for k in range(x - 2, x + 3) if k in bottom)
        smooth[x] = win[len(win) // 2]
    for x in sorted(bottom):
        for y in range(smooth[x] + 1, H):  # Zacken unterhalb der Saumlinie weg
            for n in names:
                parts[n][y][x] = "."
        for y in range(max(min(cols[x]) + 1, y_from), smooth[x] + 1):  # Löcher füllen
            if owner(x, y) is None:
                n = owner(x, y - 1)
                if n:
                    fill_from(n, x, y, x, y - 1)
    for y in range(y_from, H):  # waagerechte Lücken von 1–2 px schließen
        row = [owner(x, y) for x in range(W)]
        x = 0
        while x < W:
            if row[x] is not None:
                x += 1
                continue
            x0 = x
            while x < W and row[x] is None:
                x += 1
            if x0 > 0 and x < W and x - x0 <= 2 and row[x0 - 1]:
                for k in range(x0, x):
                    fill_from(row[x0 - 1], k, y, x0 - 1, y)

    # Seitliche Zipfel: Zeilen, die außen deutlich über beide Nachbarzeilen
    # hinausragen, auf deren Breite kürzen
    def extent(y):
        xs = [x for x in range(W) if owner(x, y)]
        return (min(xs), max(xs)) if xs else None

    for y in range(y_from, H - 1):
        cur, up, down = extent(y), extent(y - 1), extent(y + 1)
        if not cur or not up:
            continue
        lo = up[0] if not down else min(up[0], down[0])
        hi = up[1] if not down else max(up[1], down[1])
        for x in range(cur[0], lo - 1):
            for n in names:
                parts[n][y][x] = "."
        for x in range(hi + 2, cur[1] + 1):
            for n in names:
                parts[n][y][x] = "."

    # Winzige Restfetzen (< 8 Pixel, nicht mit dem Rock verbunden) entfernen
    occ = {(x, y) for n in names for x, y in pixels(parts[n])}
    seen = set()
    for start in occ:
        if start in seen:
            continue
        comp, stack = [], [start]
        seen.add(start)
        while stack:
            x, y = stack.pop()
            comp.append((x, y))
            for dx, dy in N4:
                q = (x + dx, y + dy)
                if q in occ and q not in seen:
                    seen.add(q)
                    stack.append(q)
        if len(comp) < 8:
            for x, y in comp:
                for n in names:
                    parts[n][y][x] = "."


def shift_part(g, dx, dy=0):
    out = blank()
    for x, y in pixels(g):
        if 0 <= x + dx < W and 0 <= y + dy < H:
            out[y + dy][x + dx] = g[y][x]
    return out


def build(theta_deg, sources, limb_src, order, partmap, out_path, foot_kind, views=None):
    """views: bereits geladene (z. B. vorbereitete) Quellansichten; sonst aus char/."""
    views = views or {k: load(f"char/{k}.json") for k in sources}
    parts = {n: blank() for n in views[sources[0]]["parts"]}
    for g, names in GROUPS.items():

        def pick(phi_deg, head=(g == "head")):
            # Jeder sichtbare Winkel bekommt eine Quelle (sonst entstehen Lücken)
            p = (phi_deg + 180) % 360 - 180
            if head:  # Gesicht aus S, Ohr aus E, Hinterkopf aus N
                if -72 <= p <= 90:
                    return "S"
                if -90 <= p < -72:
                    return "E"
                return "N"
            if -45 <= p <= 90:
                return "S"
            if -135 <= p < -45:
                return "E"
            return "N"

        targets = sorted({partmap[v].get(n, n) for v in views for n in names} - {None})
        rotate_group(views, names, theta_deg, parts, pick, partmap)
        for t in targets:
            remove_fringes(parts[t])
        if g == "skirt":
            clean_hem(parts, ["skirt_front", "skirt_back"])
        outline_group(parts, targets)

    th = math.radians(theta_deg)
    L = load(f"char/{limb_src}.json")
    E = load("char/E.json")
    piv = {}
    for limb in ("upper_arm", "forearm", "thigh", "shin", "foot"):
        for side in ("R", "L"):
            n = f"{limb}_{side}"
            px_l = L["pivots"][n][0]
            X = (px_l - C0) if limb_src == "S" else (C0 - px_l)
            Z = E["pivots"][n][0] - C0
            target = C0 + X * math.cos(th) + Z * math.sin(th)
            dx = round(target - px_l)
            parts[n] = shift_part(L["parts"][n], dx)
            piv[n] = [L["pivots"][n][0] + dx, L["pivots"][n][1]]
    # Beide Stiefelspitzen zeigen in die Laufrichtung (nicht gespiegelt)
    replace_feet(parts, piv, foot_kind)
    for k in ("root", "pelvis", "torso", "head", "hair_front", "hair_back",
              "skirt_front", "skirt_back"):
        X = L["pivots"][k][0] - C0
        if limb_src == "N":
            X = -X
        Z = E["pivots"][k][0] - C0
        piv[k] = [round(C0 + X * math.cos(th) + Z * math.sin(th), 1), L["pivots"][k][1]]
    save({"pal": views[sources[0]]["pal"], "order": order, "pivots": piv, "parts": parts},
         out_path)


if __name__ == "__main__":
    SE_ORDER = ["upper_arm_L", "forearm_L", "hair_back", "skirt_back",
                "thigh_L", "shin_L", "foot_L", "thigh_R", "shin_R", "foot_R",
                "skirt_front", "torso", "upper_arm_R", "forearm_R", "head", "hair_front"]
    NE_ORDER = ["hair_front", "skirt_front",
                "thigh_L", "shin_L", "foot_L", "thigh_R", "shin_R", "foot_R",
                "skirt_back", "upper_arm_L", "forearm_L", "torso",
                "upper_arm_R", "forearm_R", "hair_back", "head"]
    build(35, ["S", "E", "N"], "S", SE_ORDER,
          {"S": {}, "N": {}, "E": {"skirt_back": None}}, "char/SE.json", "se")
    build(145, ["N", "E", "S"], "N", NE_ORDER,
          {"N": {}, "S": {}, "E": {"skirt_front": "skirt_back", "skirt_back": None}},
          "char/NE.json", "ne")
    print("ok")
