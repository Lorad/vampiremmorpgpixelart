"""Stiefel-Füße je Blickrichtung (Spitze zeigt immer in Laufrichtung).

Jede Vorlage beginnt am Knöchel (erste Zeile setzt den Stiefelschaft fort).
Der Schaft ist innen 4 Pixel breit (Spalten 2–5); ANCHOR = 4 ist die Mitte
des Schafts (linke Kante von Spalte 4) und wird an die Mitte des Schienbeins
gelegt.
"""
from common import H, W, blank

ANCHOR = 4

FEET = {
    # Spitze zur Kamera (Blick nach Süden): heller Fußrücken, runde Spitze unten
    "front": [
        ".KdgddK.",
        "KdhgggdK",
        "KggggggK",
        "KdgggddK",
        ".KKKKKK.",
    ],
    # Spitze von der Kamera weg (Norden): man sieht die Fersenkappe und den Absatz
    "back": [
        ".KddddK.",
        ".KdgddK.",
        ".KdggdK.",
        ".KkkkkK.",
        "..KKKK..",
    ],
    # Spitze nach rechts unten (Südost)
    "se": [
        ".KdgddK...",
        ".KdhggdK..",
        ".KdggggdK.",
        "..KdggggdK",
        "...KKKKKKK",
    ],
    # Spitze nach rechts oben (Nordost): Ferse links unten sichtbar
    "ne": [
        ".KddddK...",
        ".KdddggK..",
        ".KkdhgggK.",
        ".KKkdggdK.",
        "..KKKKKK..",
    ],
}


def shin_bottom(shin):
    """Unterste Zeile des Schienbeins mit Innenpixeln: (Zeile, Mitte des Schafts)."""
    for y in range(H - 1, -1, -1):
        xs = [x for x in range(W) if shin[y][x] not in ".K"]
        if xs:
            return y, (min(xs) + max(xs) + 1) / 2
    raise ValueError("leeres Schienbein")


def foot_for(shin, kind, mirror=False):
    """Erzeugt den Fuß unter einem Schienbein. Gibt (Gitter, Knöchel-Gelenk) zurück."""
    rows = FEET[kind]
    width = len(rows[0])
    anchor = ANCHOR
    if mirror:
        rows = [r[::-1] for r in rows]
        anchor = width - ANCHOR
    y_ankle, center = shin_bottom(shin)
    x0 = round(center - anchor)
    y0 = y_ankle + 1
    grid = blank()
    for j, line in enumerate(rows):
        for i, ch in enumerate(line):
            if ch != "." and 0 <= y0 + j < H and 0 <= x0 + i < W:
                grid[y0 + j][x0 + i] = ch
    return grid, [float(center), float(y0)]


def replace_feet(parts, pivots, kind, mirror_left=False):
    """Ersetzt beide Füße einer Ansicht. In Front-/Rückansicht ist der linke Fuß
    gespiegelt; in Seiten- und Schrägansichten zeigen beide in dieselbe Richtung."""
    for side in ("R", "L"):
        grid, pivot = foot_for(parts[f"shin_{side}"], kind, mirror=(side == "L" and mirror_left))
        parts[f"foot_{side}"] = grid
        pivots[f"foot_{side}"] = pivot
