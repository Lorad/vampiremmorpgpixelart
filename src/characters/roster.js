/**
 * Spielbare Figuren. Jede hat einen Texturatlas und ein Skelett unter
 * public/assets/characters/<file>.png | .json | .rig.json
 * (erzeugt mit tools/character/build.py bzw. build_male.py).
 * `motion` passt die Animation an (siehe characters/animations.js).
 */
export const CHARACTERS = [
  { id: 'vampire', name: 'Vampirin', file: 'vampire', motion: {} },
  // kurze, zurückgekämmte Haare: schwingen nicht nach
  { id: 'vampire_male', name: 'Vampir', file: 'vampire_male', motion: { hair: 0 } },
];

/** Schlüssel der Skelettdaten im JSON-Cache. */
export const rigKey = (character) => `${character.file}-rig`;

const STORAGE_KEY = 'vampire-vs-human.figur';

/** Gewählte Figur: aus dem Spiel-Register, sonst die zuletzt gespeicherte Wahl. */
export function currentCharacter(registry) {
  let id = registry.get('character');
  if (!id) {
    try {
      id = window.localStorage.getItem(STORAGE_KEY);
    } catch {
      id = null; // z. B. privates Fenster: dann eben die erste Figur
    }
  }
  return CHARACTERS.find((c) => c.id === id) ?? CHARACTERS[0];
}

/** Figur wählen (gilt sofort und wird fürs nächste Mal gemerkt). */
export function chooseCharacter(registry, character) {
  registry.set('character', character.id);
  try {
    window.localStorage.setItem(STORAGE_KEY, character.id);
  } catch {
    // Speichern ist nur Komfort
  }
}
