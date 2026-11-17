"""Baut den Vampir (männliche Figur) komplett neu.

    python3 tools/character/build_male.py

Benötigt Python 3 mit Pillow und numpy. Anders als die Vampirin hat der Vampir
keine Vorlage: Front-, Rück- und Seitenansicht sind gezeichnet (male/*.py),
im selben Stil, mit derselben Palette und denselben 16 Skelett-Teilen.
Zwischenergebnisse landen in tools/character/.work/male/ (nicht im Git). Ergebnis:
  public/assets/characters/vampire_male.{png,json,rig.json}  – fürs Spiel
  art/vampire_male/…                                          – Ebenen & Vorschauen
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
WORK = os.path.join(HERE, ".work", "male")
os.makedirs(os.path.join(WORK, "char"), exist_ok=True)

STEPS = [
    "male/front.py",      # Frontansicht (Süd), gezeichnet
    "male/north.py",      # Rückansicht (Nord)
    "male/east.py",       # Seitenansicht (Ost), gezeichnet
    "male/diagonals.py",  # Südost/Nordost: Drehen + Kopf/Oberkörper von Hand
    "finalize.py",        # West/Südwest/Nordwest gespiegelt + Vorschau
]
for step in STEPS:
    print(f"== {step}")
    subprocess.run([sys.executable, os.path.join(HERE, step)], cwd=WORK, check=True)
print("== export.py")
subprocess.run([sys.executable, os.path.join(HERE, "export.py"), REPO, "vampire_male",
                "art/vampire_male"], cwd=WORK, check=True)
