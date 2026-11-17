"""Vampir (männlich) – Schrägansichten (Südost, Nordost): Drehen + Handarbeit.

Nutzt dasselbe Verfahren wie die Vampirin (../rotate.py) mit zwei Anpassungen:

- Die abstehenden Spitzohren der Front- und Rückansicht würden die Kopfbreite
  einzelner Zeilen verfälschen (der Kopf würde zackig). Gedreht wird deshalb
  ohne sie; das Ohr kommt wie bei der Vampirin aus der Seitenansicht.
- Von hinten liegt der Stehkragen über dem kurzen Nackenhaar, deshalb wird das
  Haar in Nordost vor dem Oberkörper gezeichnet.
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from common import load  # noqa: E402
from rotate import build  # noqa: E402

SE_ORDER = ["upper_arm_L", "forearm_L", "hair_back", "skirt_back",
            "thigh_L", "shin_L", "foot_L", "thigh_R", "shin_R", "foot_R",
            "skirt_front", "torso", "upper_arm_R", "forearm_R", "head", "hair_front"]
NE_ORDER = ["hair_front", "skirt_front",
            "thigh_L", "shin_L", "foot_L", "thigh_R", "shin_R", "foot_R",
            "skirt_back", "upper_arm_L", "forearm_L", "hair_back", "torso",
            "upper_arm_R", "forearm_R", "head"]


def without_ears(view, keep):
    """Kopie der Ansicht, im Kopf-Teil nur die Spalten keep[0]..keep[1]."""
    v = copy.deepcopy(view)
    for y, row in enumerate(v["parts"]["head"]):
        for x in range(len(row)):
            if not keep[0] <= x <= keep[1]:
                row[x] = "."
    return v


views = {"S": without_ears(load("char/S.json"), (23, 39)),
         "N": without_ears(load("char/N.json"), (23, 39)),
         "E": load("char/E.json")}
build(35, ["S", "E", "N"], "S", SE_ORDER,
      {"S": {}, "N": {}, "E": {"skirt_back": None}}, "char/SE.json", "se", views=views)
build(145, ["N", "E", "S"], "N", NE_ORDER,
      {"N": {}, "S": {}, "E": {"skirt_front": "skirt_back", "skirt_back": None}},
      "char/NE.json", "ne", views=views)

# Kopf und Oberkörper der Schrägansichten sind von Hand gezeichnet (male/oblique.py):
# beim Drehen entstehen dort Lücken (Ohr, Kragen) und die Weste würde aus der
# Seitenansicht an die falsche Stelle wandern.
import oblique  # noqa: E402,F401

print("gespeichert: char/SE.json, char/NE.json")
