"""Exportiert eine Figur ins Repo: Atlas + Rig (Spiel), Ebenen-PNGs + Vorschauen (Kunst).

    python3 export.py <repo> [name] [kunst-ordner]

Standard ist die Vampirin (name "vampire", Ordner art/vampire).
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image  # noqa: E402
from preview import bbox, exploded, part_image  # noqa: E402

REPO = sys.argv[1]
NAME = sys.argv[2] if len(sys.argv) > 2 else "vampire"
ART_DIR = sys.argv[3] if len(sys.argv) > 3 else "art/vampire"
DIRS = ["S", "SE", "E", "NE", "N", "NW", "W", "SW"]
BONES = {
    "pelvis": None,
    "torso": "pelvis", "head": "torso", "hair_front": "head", "hair_back": "head",
    "upper_arm_R": "torso", "forearm_R": "upper_arm_R",
    "upper_arm_L": "torso", "forearm_L": "upper_arm_L",
    "skirt_front": "pelvis", "skirt_back": "pelvis",
    "thigh_R": "pelvis", "shin_R": "thigh_R", "foot_R": "shin_R",
    "thigh_L": "pelvis", "shin_L": "thigh_L", "foot_L": "shin_L",
}
ORIGIN = {"x": 31, "y": 61}  # Fußpunkt auf dem Boden (Leinwand-Koordinaten)

views = {d: json.load(open(f"char/final_{d}.json")) for d in DIRS}
pal = views["S"]["pal"]

# ------------------------------------------------------------ Atlas packen (Regal-Packer)
frames = []
for d in DIRS:
    v = views[d]
    for n in v["order"]:
        rows = v["parts"][n]
        bb = bbox(rows)
        if not bb:
            continue
        img = part_image(rows, pal).crop(bb)
        frames.append((f"{d}/{n}", img, bb, d, n))

frames.sort(key=lambda f: -f[1].height)
ATLAS_W = 512
PAD = 1
x = y = shelf_h = 0
placed = {}
for name, img, bb, d, n in frames:
    if x + img.width + PAD > ATLAS_W:
        x, y, shelf_h = 0, y + shelf_h + PAD, 0
    placed[name] = (x, y)
    x += img.width + PAD
    shelf_h = max(shelf_h, img.height)
atlas_h = y + shelf_h
atlas_h = 1 << (atlas_h - 1).bit_length()
atlas = Image.new("RGBA", (ATLAS_W, atlas_h), (0, 0, 0, 0))
atlas_json = {"frames": {}, "meta": {"image": f"{NAME}.png", "size": {"w": ATLAS_W, "h": atlas_h},
                                     "scale": "1", "app": "tools/character"}}
rig = {"name": NAME, "canvas": {"w": 62, "h": 62}, "origin": ORIGIN, "bones": BONES,
       "directions": {}}
for name, img, bb, d, n in frames:
    px, py = placed[name]
    atlas.paste(img, (px, py))
    w, h = img.size
    atlas_json["frames"][name] = {
        "frame": {"x": px, "y": py, "w": w, "h": h}, "rotated": False, "trimmed": False,
        "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h}, "sourceSize": {"w": w, "h": h},
    }
for d in DIRS:
    v = views[d]
    parts = {}
    for name, img, bb, dd, n in frames:
        if dd != d:
            continue
        piv = v["pivots"].get(n, [bb[0], bb[1]])
        parts[n] = {"frame": name, "x": bb[0], "y": bb[1], "w": img.width, "h": img.height,
                    "pivot": [float(piv[0]), float(piv[1])]}
    rig["directions"][d] = {
        "order": [n for n in v["order"] if n in parts],
        "pivots": {b: [float(c) for c in v["pivots"][b]] for b in BONES},
        "parts": parts,
    }

out_game = os.path.join(REPO, "public/assets/characters")
os.makedirs(out_game, exist_ok=True)
atlas.save(os.path.join(out_game, f"{NAME}.png"))
json.dump(atlas_json, open(os.path.join(out_game, f"{NAME}.json"), "w"), indent=1)
json.dump(rig, open(os.path.join(out_game, f"{NAME}.rig.json"), "w"), indent=1)

# ------------------------------------------------------------ Ebenen für Grafikprogramme
art = os.path.join(REPO, ART_DIR)
if os.path.isdir(os.path.join(art, "parts")):
    shutil.rmtree(os.path.join(art, "parts"))
for d in DIRS:
    v = views[d]
    folder = os.path.join(art, "parts", d)
    os.makedirs(folder, exist_ok=True)
    for i, n in enumerate(v["order"]):
        rows = v["parts"][n]
        if not bbox(rows):
            continue
        part_image(rows, pal).save(os.path.join(folder, f"{i:02d}_{n}.png"))
    full = Image.new("RGBA", (62, 62), (0, 0, 0, 0))
    for n in v["order"]:
        full.alpha_composite(part_image(v["parts"][n], pal))
    full.save(os.path.join(art, f"{NAME}_{d}.png"))

# Vorschauen
shutil.copy("char/compass.png", os.path.join(art, "preview_8_richtungen.png"))
s = views["S"]
exploded({"pal": pal, "order": s["order"], "pivots": s["pivots"], "parts": s["parts"]},
         os.path.join(art, "preview_teile_S.png"))
if os.path.exists("ref/vampire_ref.png"):  # nur die Vampirin hat eine Vorlage
    shutil.copy("ref/vampire_ref.png", os.path.join(art, "reference.png"))
json.dump({"palette": pal}, open(os.path.join(art, "palette.json"), "w"), indent=1)
print("Atlas", ATLAS_W, "x", atlas_h, "Frames:", len(frames))
