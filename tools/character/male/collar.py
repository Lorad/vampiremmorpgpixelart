"""Stehkragen des Vampirs von hinten (für Nord und Nordost)."""


def back_collar(g, x0, x1, bottom=22, open_right=False):
    """Zeichnet den Kragen in das Gitter g (Spalten x0..x1, bis Zeile bottom).

    Von schräg oben gesehen ist der obere Rand rund: außen höher als in der
    Mitte, wo er im Nacken anliegt. Unter dem schwarzen Rand blitzt das rote
    Futter. open_right: rechts ist der Kragen offen (Nordost), dort sieht man
    mehr Futter.
    """
    cx = (x0 + x1) / 2
    half = (x1 - x0) / 2
    for x in range(x0, x1 + 1):
        u = abs(x - cx) / half  # 0 = Mitte, 1 = Rand
        top = 18 - round(2 * u * u)
        for y in range(top, bottom + 1):
            if x in (x0, x1) or y == top:
                c = "K"
            elif y == top + 1:
                c = "R" if u > 0.6 else "r"
            elif y == top + 2:
                c = "g"
            else:
                c = "d"
            g[y][x] = c
    if open_right:
        for y in range(17, 21):
            g[y][x1 - 1] = "r" if y % 2 else "R"
