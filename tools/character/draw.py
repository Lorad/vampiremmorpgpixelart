"""Zeichenwerkzeuge für neue Ansichten (Formen per Zeilenbereich + Schattierung)."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import H, W, blank  # noqa: E402,F401

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def ranges_to_set(ranges):
    pts = set()
    for y, rs in ranges.items():
        if isinstance(rs[0], int):
            rs = [rs]
        for x0, x1 in rs:
            for x in range(x0, x1 + 1):
                pts.add((x, y))
    return pts


def edge_of(pts):
    return {(x, y) for x, y in pts if any((x + dx, y + dy) not in pts for dx, dy in N4)}


def paint(g, pts, fn, outline="K", under=False):
    """Füllt `pts` mit fn(x, y) und zieht einen Umriss auf die Randpixel."""
    e = edge_of(pts) if outline else set()
    for x, y in pts:
        if not (0 <= x < W and 0 <= y < H):
            continue
        if under and g[y][x] != ".":
            continue
        c = outline if (x, y) in e else fn(x, y)
        if c and c != ".":
            g[y][x] = c
    return e


def wave(y, period=6.0, amp=1.0, phase=0.0):
    return amp * math.sin(y * 2 * math.pi / period + phase)


def hair_shader(pts, crown, light=(-0.6, -0.8), stripe=2.7, top_hi=14, radial_until=16):
    """Haarstruktur: Strähnen strahlen vom Wirbel aus, unten senkrecht mit Wellen."""
    cx, cy = crown

    def coord(x, y):
        if y < radial_until:
            a = math.atan2(x - cx, y - cy + 3)  # Winkel um den Wirbel
            return a * 8.0 + 0.6 * math.sin(y / 2.5)
        return (x - cx) / 1.0 + 1.1 * math.sin(y / 3.0 + x / 7.0)

    def fn(x, y):
        s = coord(x, y) / stripe
        t = s - math.floor(s)
        sl = coord(x - 1, y) / stripe
        if (x - 1, y) in pts and math.floor(sl) != math.floor(s) and y > cy + 1:
            return "k"
        if t < 0.38:
            return "h" if y <= top_hi else "p"
        if t > 0.8:
            return "d" if y < 22 else "k"
        return "p"

    return fn


def inner_line(g, pts, edge, ch="k", sides=((1, 0), (-1, 0), (0, -1))):
    """Dunkle zweite Kante innen am Umriss (Stil der Vorlage)."""
    for x, y in pts:
        if (x, y) in edge:
            continue
        if g[y][x] in "ph" and any((x + dx, y + dy) in edge for dx, dy in sides):
            g[y][x] = ch


DARKEN = {"r": "R", "R": "B", "B": "b", "m": "b", "g": "d", "d": "k", "h": "p", "p": "k",
          "W": "S", "w": "S", "S": "s", "s": "B", "e": "E", "i": "e", "b": "k"}


def darken(g):
    for y in range(H):
        for x in range(W):
            if g[y][x] in DARKEN:
                g[y][x] = DARKEN[g[y][x]]
    return g


def shift(g, dx, dy=0):
    out = blank()
    for y in range(H):
        for x in range(W):
            if g[y][x] != "." and 0 <= x + dx < W and 0 <= y + dy < H:
                out[y + dy][x + dx] = g[y][x]
    return out
