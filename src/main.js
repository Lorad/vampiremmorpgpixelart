import Phaser from 'phaser';
import WorldScene from './scenes/WorldScene.js';

new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  backgroundColor: '#0b1710',
  pixelArt: true, // scharfe Pixel, keine Weichzeichnung
  scale: {
    mode: Phaser.Scale.RESIZE, // Spielfläche = ganzes Browserfenster
  },
  scene: [WorldScene],
});
