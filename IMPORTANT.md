# 🛠️ Projekt-Setup (Startanleitung)
 
Wir nutzen **[uv](https://docs.astral.sh/uv/)** für Python-Version, virtuelle Umgebung und Dependencies. Funktioniert identisch unter macOS, Linux und Windows.
 
Alle wichtigen Befehle sind zusätzlich als **npm-Skripte** in der `package.json` hinterlegt und lassen sich per `npm run …` oder in VS Code über den Explorer unter **NPM-Skripte** per Klick starten.
 
## 1. Voraussetzungen installieren (einmalig)
 
### uv
 
**macOS / Linux**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
 
**Windows (PowerShell)**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
 
Alternativ: `brew install uv` (macOS) oder `winget install --id=astral-sh.uv -e` (Windows).
 
### Node.js (für die npm-Skripte)
 
[Node.js LTS](https://nodejs.org/) installieren, alternativ `brew install node` (macOS) oder `winget install OpenJS.NodeJS.LTS` (Windows).
 
Danach Terminal neu öffnen und prüfen:
```bash
uv --version
npm --version
```
 
## 2. Projekt klonen und einrichten
 
```bash
git clone <repo-url>
cd <repo-name>
git checkout develop
npm run setup        # entspricht: uv sync
```
 
`uv sync` lädt automatisch die richtige Python-Version (aus `.python-version`), erstellt die `.venv` und installiert alle Dependencies exakt nach `uv.lock`.
 
## 3. Starten & Testen
 
| Befehl | Was passiert |
|---|---|
| `npm start` | Anwendung starten |
| `npm run smoke` | Kurzer Starttest (`--version`) |
| `npm test` | Tests ausführen |
| `npm run test:cov` | Tests mit Testabdeckung (Coverage) |
| `npm run lint` | Linting inkl. Security-Regeln |
| `npm run lint:fix` | Linting mit automatischer Korrektur |
| `npm run format` | Code formatieren |
| `npm run format:check` | Formatierung nur prüfen |
| `npm run typecheck` | Typprüfung (mypy) |
| `npm run audit` | Dependencies auf Schwachstellen prüfen |
| **`npm run check`** | **Alle Prüfungen wie in der CI** |
| `npm run check:fix` | Wie `check`, korrigiert Format/Lint automatisch |
| `npm run check:tests` | Nur Tests + Smoke-Test |
 
> [!IMPORTANT]
> Vor jedem PR einmal **`npm run check`** ausführen. Dieselben Prüfungen laufen auch automatisch in den GitHub Actions – schlagen sie fehl, kann der PR nicht gemergt werden.
 
> [!TIP]
> Ohne Node.js geht alles auch direkt über uv, z. B. `uv run pytest` oder `uv run python scripts/check.py`.
> Mit `uv run` muss die `.venv` nicht manuell aktiviert werden. Wer es trotzdem möchte:
> macOS/Linux `source .venv/bin/activate` · Windows `.venv\Scripts\activate`
 
## 4. Dependencies hinzufügen
 
```bash
uv add <paket>            # Laufzeit-Dependency
uv add --dev <paket>      # nur für Entwicklung (Tests, Linter, ...)
uv remove <paket>         # entfernen
```
 
> [!IMPORTANT]
> `pyproject.toml` **und** `uv.lock` immer mit committen, z. B. `chore(T0001): add embit dependency`.
> Nach einem Pull mit geänderten Dependencies einfach erneut `npm run setup` ausführen.
 
## 5. Automatische Prüfungen (GitHub Actions)
 
Bei jedem Push und PR auf `develop` und `main` laufen automatisch:
 
| Workflow | Prüft |
|---|---|
| `lint-commits.yml` | Commit-Messages nach Conventional Commits |
| `code-quality.yml` | Linting, Formatierung, Typen, Schwachstellen in Dependencies |
| `tests.yml` | Tests auf Ubuntu, macOS und Windows + Starttest der Anwendung |