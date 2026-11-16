/**
 * Einfache Idle-Animation: Der Oberkörper (mit Kopf, Haaren und Armen) senkt
 * sich im Atemrhythmus um 1 Pixel. Nur ganze Pixel → bleibt pixelgenau.
 */
export function startIdle(scene, rig, { period = 1400, delay = 0 } = {}) {
  let down = false;
  return scene.time.addEvent({
    delay: period / 2,
    startAt: delay % (period / 2),
    loop: true,
    callback: () => {
      down = !down;
      rig.setBone('torso', { y: down ? 1 : 0 });
    },
  });
}
