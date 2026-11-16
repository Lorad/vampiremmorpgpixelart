# vampiremmorpgpixelart

Ein Pixel-Art-MMORPG im Browser: **Vampire gegen Menschen**, in 3/4-Ansicht
(„schräg von oben“). Gebaut mit [Phaser 4](https://phaser.io) und [Vite](https://vite.dev).

![Die Vampirin in allen 8 Richtungen](art/vampire/preview_8_richtungen.png)

## Stand

- **Welt:** kleine Wiese, umgeben von dichtem Wald. Bodenkacheln 32×32 px,
  Bäume als einzelne Objekte. Alles, was steht, wird nach seinem Fußpunkt
  sortiert, sodass Figuren hinter Baumkronen verschwinden können.
- **Vampirin:** aus dem Referenzbild rekonstruiert (62×62 px, 18 Farben), in
  Idle-Pose mit hängenden Armen, zerlegt in 16 Skelett-Teile, in allen
  **8 Himmelsrichtungen**.

## Starten

```bash
npm install
npm run dev
```

Dann im Browser <http://localhost:5173> öffnen.

| Taste | Funktion |
| --- | --- |
| `Q` / `E` | Figur drehen (8 Richtungen) |
| `F` | Figuren-Ansicht ↔ Welt (direkt: <http://localhost:5173/#figur>) |

## Projektaufbau

```
src/
  main.js                    Spiel-Konfiguration
  scenes/PreloadScene.js     lädt alle Grafiken
  scenes/WorldScene.js       die Welt
  scenes/CharacterScene.js   Figuren-Ansicht (8 Richtungen + Teile)
  characters/CharacterRig.js Figur aus Teilen mit Skelett
  characters/idle.js         Atem-Animation
public/assets/
  tilesets/tiles.png         Bodenkacheln
  sprites/trees.png          Bäume
  maps/world.json            Karte (Format des Map-Editors „Tiled“)
  characters/vampire.*       Vampirin: Texturatlas + Skelett (rig.json)
art/vampire/
  reference.png              Original-Vorlage
  parts/<Richtung>/NN_*.png  jedes Teil als eigene Ebene (62×62, NN = Zeichenreihenfolge)
  vampire_<Richtung>.png     zusammengesetzte Figur je Richtung
tools/
  generate-world.mjs         erzeugt Kacheln, Bäume und Karte
  character/                 erzeugt die Vampirin aus der Vorlage
```

## Die Vampirin (Skelett)

| Teil | hängt an | | Teil | hängt an |
| --- | --- | --- | --- | --- |
| `torso` (Oberkörper) | `pelvis` (Becken) | | `skirt_front` / `skirt_back` | `pelvis` |
| `head` (Kopf) | `torso` | | `thigh_R/L` (Oberschenkel) | `pelvis` |
| `hair_front` / `hair_back` | `head` | | `shin_R/L` (Schienbein) | `thigh` |
| `upper_arm_R/L` (Oberarm) | `torso` | | `foot_R/L` (Fuß) | `shin` |
| `forearm_R/L` (Unterarm + Hand) | `upper_arm` | | | |

`R`/`L` sind ihre rechte/linke Seite (in der Frontansicht ist ihr rechter Arm
also links im Bild). Verdeckte Bereiche, etwa der Oberkörper unter den Armen,
sind aufgefüllt, damit beim Bewegen keine Löcher entstehen.

`public/assets/characters/vampire.rig.json` enthält pro Richtung die Bilder,
die Gelenkpunkte (`pivots`) und die Zeichenreihenfolge. Im Spiel:

```js
const vampire = new CharacterRig(scene, x, y, 'vampire', rig, 'S');
vampire.setDirection('NE');                  // Blickrichtung
vampire.setBone('forearm_R', { angle: -30 }); // Unterarm anwinkeln (Grad)
vampire.setBone('torso', { y: 1 });           // Oberkörper 1 px absenken
```

Kinder-Knochen bewegen sich automatisch mit, zum Beispiel die Hand mit dem
Oberarm.

### Wie die 8 Richtungen entstehen

- **Süd:** aus der Vorlage. Das Raster des hochskalierten Bildes wird erkannt
  und auf die Originalpixel zurückgerechnet, der angewinkelte Arm wird durch den
  gespiegelten hängenden Arm ersetzt.
- **Nord:** Rücken; Arme, Beine und Rocksilhouette aus Süd, Haare neu.
- **Ost:** Profil, neu gezeichnet.
- **Südost / Nordost:** Jede Körperpartie wird zeilenweise als Ellipse gedreht.
  Jedes Pixel stammt aus der Ansicht, die diese Stelle am frontalsten zeigt.
- **West / Südwest / Nordwest:** gespiegelt (links/rechts getauscht).

Alles neu bauen (benötigt Python 3 mit Pillow und numpy):

```bash
python3 tools/character/build.py
```

Die Welt neu erzeugen (überschreibt Karte und Grafiken):

```bash
npm run generate:world
```
