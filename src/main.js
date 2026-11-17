import Phaser from 'phaser';
import PreloadScene from './scenes/PreloadScene.js';
import SelectScene from './scenes/SelectScene.js';
import WorldScene from './scenes/WorldScene.js';
import CharacterScene from './scenes/CharacterScene.js';

const game = new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  backgroundColor: '#0b1710',
  pixelArt: true, // scharfe Pixel, keine Weichzeichnung
  scale: {
    mode: Phaser.Scale.RESIZE, // Spielfläche = ganzes Browserfenster
  },
  scene: [PreloadScene, SelectScene, WorldScene, CharacterScene],
});

// Nur beim Entwickeln: Zugriff für automatische Tests
if (import.meta.env.DEV) window.__game = game;
