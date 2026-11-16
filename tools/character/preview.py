"""Vorschau-Bilder für Teile-Sätze (Explosionsansicht + Zusammenbau)."""
import json
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import hex2rgb  # noqa: E402


def part_image(rows, pal):
    h = len(rows)
    w = len(rows[0])
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != ".":
                px[x, y] = hex2rgb(pal[ch]) + (255,)
    return im


def bbox(rows):
    ys = [y for y, r in enumerate(rows) if r.strip(".")]
    xs = [x for r in rows for x, ch in enumerate(r) if ch != "."]
    if not ys:
        return None
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def checker(w, h, s=4):
    im = Image.new("RGBA", (w, h), (235, 235, 235, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range(0, w, s):
            if (x // s + y // s) % 2:
                d.rectangle([x, y, x + s - 1, y + s - 1], fill=(210, 210, 210, 255))
    return im


def exploded(data, out, scale=6, cols=6, pivots=True):
    pal = data["pal"]
    names = data["order"]
    cell = 64 * scale // 2 + 40
    tiles = []
    for name in names:
        rows = data["parts"][name]
        bb = bbox(rows)
        im = part_image(rows, pal)
        if bb:
            im = im.crop(bb)
        big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        tiles.append((name, big, bb))
    cw = max(t[1].width for t in tiles) + 20
    ch = max(t[1].height for t in tiles) + 34
    rows_n = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (cw * cols, ch * rows_n), (255, 255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, (name, big, bb) in enumerate(tiles):
        cx = (i % cols) * cw
        cy = (i // cols) * ch
        bg = checker(big.width, big.height, scale)
        bg.alpha_composite(big)
        sheet.paste(bg, (cx + 10, cy + 24))
        d.text((cx + 10, cy + 6), name, fill=(0, 0, 0))
        piv = data.get("pivots", {}).get(name)
        if pivots and piv and bb:
            px = cx + 10 + (piv[0] - bb[0]) * scale
            py = cy + 24 + (piv[1] - bb[1]) * scale
            d.ellipse([px - 4, py - 4, px + 4, py + 4], outline=(0, 160, 255), width=2)
    sheet.save(out)


def assembled(data, out, scale=6, order=None, bg=(255, 255, 255, 255)):
    pal = data["pal"]
    order = order or data["order"]
    first = data["parts"][order[0]]
    im = Image.new("RGBA", (len(first[0]), len(first)), bg)
    for name in order:
        im.alpha_composite(part_image(data["parts"][name], pal))
    im.resize((im.width * scale, im.height * scale), Image.NEAREST).save(out)
    return im


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    exploded(data, sys.argv[2])
    if len(sys.argv) > 3:
        assembled(data, sys.argv[3])
