"""Baut die Vampirin komplett neu aus art/vampire/reference.png.

    python3 tools/character/build.py

Benötigt Python 3 mit Pillow und numpy. Zwischenergebnisse landen in
tools/character/.work/ (nicht im Git). Ergebnis:
  public/assets/characters/vampire.{png,json,rig.json}  – fürs Spiel
  art/vampire/…                                          – Ebenen & Vorschauen
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
WORK = os.path.join(HERE, ".work")

for sub in ("ref", "char"):
    os.makedirs(os.path.join(WORK, sub), exist_ok=True)
shutil.copy(os.path.join(REPO, "art/vampire/reference.png"),
            os.path.join(WORK, "ref/vampire_ref.png"))

STEPS = [
    "extract.py",   # Referenz → saubere 62×62-Pixel-Art, Idle-Arme
    "front.py",     # Frontansicht (Süd) in Skelett-Teile zerlegen
    "north.py",     # Rückansicht (Nord)
    "east.py",      # Seitenansicht (Ost), gezeichnet
    "rotate.py",    # Schrägansichten (Südost, Nordost) durch Drehen
    "finalize.py",  # West/Südwest/Nordwest gespiegelt + Vorschau
]
for step in STEPS:
    print(f"== {step}")
    subprocess.run([sys.executable, os.path.join(HERE, step)], cwd=WORK, check=True)
print("== export.py")
subprocess.run([sys.executable, os.path.join(HERE, "export.py"), REPO], cwd=WORK, check=True)
