/**
 * Pfad einer Spieldatei. Im Einzeldatei-Build (Artefakt, siehe
 * tools/build-artifact.mjs) liegen alle Grafiken als Data-URI und alle
 * JSON-Dateien als fertige Objekte eingebettet vor; Phaser lädt beides direkt.
 */
const EMBEDDED = typeof window !== 'undefined' ? window.__EMBEDDED_ASSETS__ : undefined;

export function asset(path) {
  return EMBEDDED?.[path] ?? path;
}
