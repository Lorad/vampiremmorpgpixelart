"""Alle 8 Richtungen zusammenstellen (W, SW, NW = gespiegelt) + Vorschau."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, mirror, save  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
from preview import part_image  # noqa: E402


def swap(n):
    return n.replace("_R", "_TMP").replace("_L", "_R").replace("_TMP", "_L")


def mirrored(d):
    parts = {swap(k): mirror(v, 62) for k, v in d["parts"].items()}
    pivots = {swap(k): [63 - x, y] for k, (x, y) in d["pivots"].items()}
    return {"pal": d["pal"], "order": [swap(n) for n in d["order"]], "pivots": pivots,
            "parts": parts}


views = {k: load(f"char/{k}.json") for k in ("S", "SE", "E", "NE", "N")}
views["SW"] = mirrored(views["SE"])
views["W"] = mirrored(views["E"])
views["NW"] = mirrored(views["NE"])
for k, v in views.items():
    save(v, f"char/final_{k}.json")


def assemble(d):
    im = Image.new("RGBA", (62, 62), (0, 0, 0, 0))
    for n in d["order"]:
        rows = ["".join(r) for r in d["parts"][n]]
        im.alpha_composite(part_image(rows, d["pal"]))
    return im


# Kompass-Anordnung
layout = [["NW", "N", "NE"], ["W", None, "E"], ["SW", "S", "SE"]]
S = 6
cell = 62 * S
sheet = Image.new("RGBA", (cell * 3 + 40, cell * 3 + 40), (246, 244, 240, 255))
dr = ImageDraw.Draw(sheet)
for r, row in enumerate(layout):
    for c, k in enumerate(row):
        x0, y0 = 10 + c * (cell + 10), 10 + r * (cell + 10)
        if k is None:
            dr.text((x0 + cell // 2 - 40, y0 + cell // 2), "8 Richtungen", fill=(90, 90, 90))
            continue
        im = assemble(views[k]).resize((cell, cell), Image.NEAREST)
        sheet.alpha_composite(im, (x0, y0))
        dr.text((x0 + 6, y0 + 4), k, fill=(150, 30, 40))
sheet.save("char/compass.png")
print("ok")
