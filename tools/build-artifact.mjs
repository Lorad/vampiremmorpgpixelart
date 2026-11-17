// Baut das Spiel als EINE HTML-Datei (z. B. für ein claude.ai-Artefakt):
// Spielcode, Grafiken (Data-URIs) und JSON-Daten werden eingebettet.
//
//   npm run build:artifact   →   dist/vampire-vs-human.html
//
// Die Datei enthält bewusst kein <html>/<head>/<body>; das Gerüst setzt die
// Artefakt-Plattform beim Veröffentlichen selbst drumherum.
import { readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, extname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DIST = join(ROOT, 'dist');
const PUBLIC = join(ROOT, 'public');
const OUT = join(DIST, 'vampire-vs-human.html');

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
}

// 1) Grafiken und Daten einbetten (Schlüssel = Pfad wie im Spielcode)
const embedded = {};
for (const file of walk(join(PUBLIC, 'assets'))) {
  const key = relative(PUBLIC, file).split('\\').join('/');
  const ext = extname(file).toLowerCase();
  if (ext === '.png') embedded[key] = `data:image/png;base64,${readFileSync(file).toString('base64')}`;
  else if (ext === '.json') embedded[key] = JSON.parse(readFileSync(file, 'utf8'));
}

// 2) Spielcode aus dem Vite-Build
const bundles = readdirSync(join(DIST, 'assets')).filter((f) => /^index-.*\.js$/.test(f));
if (bundles.length !== 1) throw new Error(`Erwarte genau ein Bundle in dist/assets, gefunden: ${bundles}`);
const code = readFileSync(join(DIST, 'assets', bundles[0]), 'utf8');

// Inline-Skripte dürfen kein "</script" oder "<!--" enthalten
const safe = (s) => s.replace(/<\/script/gi, '<\\/script').replace(/<!--/g, '<\\!--');

const page = `<title>Vampire vs Human</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Pirata+One&family=Pixelify+Sans:wght@400;600&display=swap">
<style>
  /* Bühne: das Spiel füllt das Fenster, darüber eine Titelkarte bis zum ersten Klick */
  :root {
    --night: #120f18;      /* Grundfarbe: Schwarz der Haare */
    --dusk: #1c1a22;       /* Flächen */
    --bone: #f6e9df;       /* Text: helle Haut */
    --mist: #b3a6b2;       /* Nebentext */
    --blood: #b11c26;      /* Akzent: Augen der Vampirin */
    --blood-hi: #e3575e;
    --font-title: "Pirata One", "UnifrakturMaguntia", Georgia, serif;
    --font-ui: "Pixelify Sans", ui-monospace, "SFMono-Regular", Menlo, monospace;
    color-scheme: dark;
  }
  html { height: 100%; box-sizing: border-box; }
  body {
    height: 100%;
    box-sizing: border-box;
    margin: 0;
    display: flex;
    background: var(--night);
    color: var(--bone);
    font-family: var(--font-ui);
    padding-block: 16px;
    padding-left: max(16px, env(safe-area-inset-left, 0px));
    padding-right: max(16px, env(safe-area-inset-right, 0px));
  }
  .stage {
    position: relative;
    flex: 1;
    min-width: 0;
    overflow: hidden;
    border-radius: 4px;
    box-shadow: 0 0 0 1px color-mix(in srgb, var(--bone) 12%, transparent);
    background: var(--night);
  }
  #game { position: absolute; inset: 0; }
  #game canvas { display: block; image-rendering: pixelated; }
  #hud {
    position: absolute;
    left: 12px;
    bottom: 12px;
    padding: 6px 10px;
    border-radius: 4px;
    background: color-mix(in srgb, var(--night) 78%, transparent);
    color: var(--bone);
    font: 15px/1.3 var(--font-ui);
    pointer-events: none;
  }
  #hud:empty { display: none; }
  .start {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    padding: 24px;
    background: color-mix(in srgb, var(--night) 70%, transparent);
  }
  .card {
    display: grid;
    gap: 22px;
    justify-items: center;
    text-align: center;
    max-width: 30rem;
  }
  .title {
    margin: 0;
    font: 400 clamp(2.6rem, 8vw, 4.6rem)/0.95 var(--font-title);
    letter-spacing: 0.01em;
    text-wrap: balance;
    text-shadow: 0 3px 0 var(--night);
  }
  .title .vs { color: var(--blood); font-size: 0.6em; vertical-align: 0.18em; padding-inline: 0.12em; }
  .sub { margin: 0; color: var(--mist); font-size: 1rem; letter-spacing: 0.04em; }
  .keys {
    display: grid;
    grid-template-columns: auto auto;
    gap: 10px 16px;
    align-items: center;
    justify-items: start;
    margin: 0;
    font-size: 1rem;
  }
  .keys dt { display: flex; gap: 4px; justify-self: end; }
  .keys dd { margin: 0; color: var(--mist); }
  kbd {
    display: inline-grid;
    place-items: center;
    min-width: 1.7em;
    height: 1.7em;
    padding-inline: 0.35em;
    border-radius: 3px;
    background: var(--dusk);
    color: var(--bone);
    font: 600 0.95rem var(--font-ui);
    box-shadow: inset 0 -3px 0 color-mix(in srgb, var(--night) 70%, transparent),
      0 0 0 1px color-mix(in srgb, var(--bone) 18%, transparent);
  }
  .play {
    padding: 12px 34px 14px;
    border: 0;
    border-radius: 4px;
    background: var(--blood);
    color: var(--bone);
    font: 600 1.25rem var(--font-ui);
    letter-spacing: 0.06em;
    cursor: pointer;
    box-shadow: inset 0 -4px 0 color-mix(in srgb, var(--night) 45%, transparent);
  }
  .play:hover { background: color-mix(in srgb, var(--blood) 85%, var(--blood-hi)); }
  .play:focus-visible { outline: 3px solid var(--blood-hi); outline-offset: 3px; }
  .hint { margin: 0; color: var(--mist); font-size: 0.85rem; }
  @media (prefers-reduced-motion: no-preference) {
    .card { animation: rise 600ms ease-out both; }
    @keyframes rise { from { transform: translateY(8px); } to { transform: none; } }
  }
</style>

<main class="stage">
  <div id="game"></div>
  <div id="hud"></div>
  <div class="start" id="start">
    <div class="card">
      <h1 class="title">Vampire <span class="vs">vs</span> Human</h1>
      <p class="sub">Spielbarer Prototyp · die Vampirin · 8 Richtungen</p>
      <dl class="keys">
        <dt><kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd></dt><dd>laufen (oder Pfeiltasten)</dd>
        <dt><kbd>F</kbd></dt><dd>Figuren-Ansicht ↔ Welt</dd>
        <dt><kbd>Leertaste</kbd></dt><dd>Figuren-Ansicht: Laufen an/aus</dd>
        <dt><kbd>B</kbd></dt><dd>Figuren-Ansicht: alle Einzelbilder</dd>
      </dl>
      <button class="play" id="play" type="button">Spielen</button>
      <p class="hint">Am PC mit Tastatur. Klicke ins Spiel, falls die Tasten nicht reagieren.</p>
    </div>
  </div>
</main>

<script>window.__EMBEDDED_ASSETS__ = ${safe(JSON.stringify(embedded))};</script>
<script type="module">${safe(code)}</script>
<script>
  // Erst ein Klick gibt der eingebetteten Seite den Tastatur-Fokus
  (function () {
    var start = document.getElementById('start');
    var play = document.getElementById('play');
    function begin() {
      start.hidden = true;
      window.focus();
      var canvas = document.querySelector('#game canvas');
      if (canvas) { canvas.setAttribute('tabindex', '0'); canvas.focus(); }
    }
    play.addEventListener('click', begin);
    document.getElementById('game').addEventListener('pointerdown', function () { window.focus(); });
  })();
</script>
`;

writeFileSync(OUT, page);
console.log(`geschrieben: ${relative(ROOT, OUT)} (${(page.length / 1024 / 1024).toFixed(2)} MB)`);
