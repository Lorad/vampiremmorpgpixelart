"""Gemeinsame Helfer für alle Ansichten der Vampirin."""
import json
import math

W = H = 62
PARTS = [
    "hair_back", "hair_front", "head", "torso",
    "upper_arm_R", "forearm_R", "upper_arm_L", "forearm_L",
    "skirt_front", "skirt_back",
    "thigh_R", "shin_R", "foot_R", "thigh_L", "shin_L", "foot_L",
]


def blank():
    return [["."] * W for _ in range(H)]


def load(path):
    d = json.load(open(path))
    d["parts"] = {k: [list(r) for r in v] for k, v in d["parts"].items()}
    return d


def save(d, path):
    out = dict(d)
    out["parts"] = {k: ["".join(r) for r in v] for k, v in d["parts"].items()}
    json.dump(out, open(path, "w"))


def mirror(g, axis2):
    """Spiegelt ein Gitter horizontal: x' = axis2 - x."""
    out = blank()
    for y in range(H):
        for x in range(W):
            if g[y][x] != ".":
                nx = axis2 - x
                if 0 <= nx < W:
                    out[y][nx] = g[y][x]
    return out


def pixels(g):
    return [(x, y) for y in range(H) for x in range(W) if g[y][x] != "."]


def union(*gs):
    out = blank()
    for g in gs:
        for x, y in pixels(g):
            out[y][x] = g[y][x]
    return out


def block(g, x0, y0, text, under=False):
    """Malt einen Textblock (Leerzeichen/Punkt = transparent) bei (x0, y0)."""
    lines = text.strip("\n").split("\n")
    for j, line in enumerate(lines):
        for i, ch in enumerate(line):
            if ch in " .":
                continue
            x, y = x0 + i, y0 + j
            if 0 <= x < W and 0 <= y < H and (not under or g[y][x] == "."):
                g[y][x] = ch


def outline(g, ch="K", inner=False):
    """Setzt einen Umriss: außen um die Form (Standard) oder auf deren Randpixel."""
    pts = set(pixels(g))
    add = []
    for x, y in pts if inner else []:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in pts:
                add.append((x, y))
                break
    if not inner:
        for x, y in pts:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in pts:
                    add.append((nx, ny))
    for x, y in add:
        g[y][x] = ch
    return g


def composite(parts, order):
    out = blank()
    for p in order:
        if p in parts:
            for x, y in pixels(parts[p]):
                out[y][x] = parts[p][y][x]
    return out
