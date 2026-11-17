# Hinweise für Claude

Der Projektinhaber schreibt Deutsch – antworte auf Deutsch.

## Git-Workflow (Pull Requests)

1. Neue Arbeit immer auf einem eigenen Branch (`feature/…`), nie direkt auf `main`.
2. Branch pushen und einen Pull Request nach `main` öffnen.
3. Erst wenn der Inhaber „übernehmen“ (o. ä.) sagt, den PR mergen:
   `gh pr merge <nr> --rebase`. GitHub löscht den Branch danach automatisch
   (Repo-Einstellung „Automatically delete head branches“). Anschließend lokal
   `main` aktualisieren und den Branch auch lokal löschen.
4. In der Cloud-Umgebung sind das Löschen von Branches auf GitHub
   (`git push --delete`) und das Ändern von Repo-Einstellungen gesperrt (HTTP 403).
   Nicht umgehen – stattdessen dem Inhaber sagen, was er selbst tun muss.

## Projekt

- Spiel starten: `npm install`, dann `npm run dev` (Port 5173). Zielplattform ist
  nur der PC-Browser mit Tastatur, keine Mobil-Version.
- Spielbares Artefakt: `npm run build:artifact` → `dist/vampire-vs-human.html`.
  Veröffentlicht unter https://claude.ai/artifact/CchQ6D5kyKkoVsqu83x36D – nach
  Änderungen am Spiel neu bauen und unter derselben Adresse aktualisieren.
- Vampirin neu erzeugen: `python3 tools/character/build.py` (braucht Pillow und numpy).
- Welt neu erzeugen: `npm run generate:world` (überschreibt Karte und Grafiken).
