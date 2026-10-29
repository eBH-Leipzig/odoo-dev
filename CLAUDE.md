# PROJEKT-RICHTLINIEN: eBike-Haus Leipzig (eBH) - Odoo WaWi

## 1. Über das Unternehmen & Einsatzbereich
- Fahrrad- und E-Bike-Fachhandel in Leipzig.
- Einsatzbereich: Warenwirtschaft (WaWi), Kasse (POS), Werkstatt, Seriennummern-Tracking, Dienstrad-Leasing.

## 2. Technische Infrastruktur & Versionierung
- Plattform: Odoo Community Edition (Docker auf Hostinger VPS sowie lokaler Docker Dev-Container).
- Version: Gesteuert über `.env` (`ODOO_VERSION=19.0`).
- Environments auf dem VPS:
  - **PROD:** `odoo.ebike-haus.de` (Deploy aus `main`-Branch)
  - **DEV:** `odoo-dev.ebike-haus.de` (Deploy aus `dev`-Branch)
- Sprache Backend: Python 3 (strikt deklaratives ORM).
- Schnittstellen: JSON-RPC fähig für externe Node.js/TypeScript-Services.
- Git & Deployment: Vollautomatisiertes Multi-Environment CI/CD via GitHub Actions (`.github/workflows/deploy.yml`). Ein Push auf `dev` aktualisiert die DEV-Instanz, ein Merge/Push auf `main` aktualisiert die PROD-Instanz. Vor jedem Deploy laufen die Modultests in GitHub Actions; scheitern sie, wird nicht deployt. Auf dem VPS hat jede Umgebung einen eigenen Checkout (`/docker/odoo-dev` auf `dev`, `/docker/odoo-prod` auf `main`) und ein eigenes Compose-Profil; den Ablauf (Sicherung, `-u` der eigenen Module, Neustart) macht `ops/deploy.sh`. Betrieb, Backup und Restore: [`docs/BETRIEB.md`](docs/BETRIEB.md). Alle Web-Traffic-Routen laufen sicher über den externen Traefik-Proxy (`root_default` Netzwerk).

## 3. Architektur- & Codestandards (OCA-Richtlinien)
- **Grundsatz Datenbank vor Modul (Vorgabe Wolfgang, 23.10.2026):**
  - Felder, Lager, Kategorien, Stammdaten und Infos werden **direkt in der Odoo-Datenbank** angelegt (Einstellungen, Entwicklermodus) und in `docs/EINRICHTUNG.md` + `docs/AENDERUNGSPROTOKOLL.md` dokumentiert – nicht als Daten-XML in Modulen.
  - **Funktionen** (Logik, die bei Updates verloren gehen könnte) kommen in Module. Wenige, nach Struktur gebündelte Module statt vieler kleiner.
  - In ein Modul auslagern nur, wenn es wirklich nötig ist.
- **Modul-Architektur:** Eure eigenen Module liegen AUSSCHLIESSLICH im Verzeichnis `custom_addons/` (in Docker gemountet nach `/mnt/extra-addons`).
- **Niemals Core verändern:** Ausschließlich `_inherit` in Python und `<xpath>` in XML nutzen.
- **OCA-Konventionen:**
  - Folge den Standards der *Odoo Community Association*.
  - Saubere Trennung: Datenmodell (`models/`), Benutzeroberfläche (`views/`), Sicherheit (`security/`) und Tests (`tests/`).
  - Keine veralteten Attribute in XML (nutze `invisible="..."`, `readonly="..."`).
- **Sicherheit & Rechte:**
  - Jedes neue Modell MUSS in `security/ir.model.access.csv` Berechtigungen definieren.
  - Verwende niemals rohe SQL-Befehle, sondern immer das Odoo-ORM (`self.env[...]`).
- **Versions-Konvention im Manifest:**
  - In `custom_addons/<module>/__manifest__.py` muss die Version mit der Odoo-Version beginnen (z. B. `'version': '19.0.1.0.0'`).
- **Odoo Mail Engine & Notification Safety (`mail.thread`):**
  - Beim Verknüpfen weitergeleiteter E-Mails oder externer Nachrichten im Chatter (`mail.thread`) niemals externe Kunden-Partner-IDs in `message_dict['partner_ids']` übergeben: Odoo behandelt diese als externe Empfänger und versendet ungewollte ausgehende Benachrichtigungen.
  - Den externen Kunden stattdessen ausschließlich als Autor (`author_id`) oder im Chatter-Nachrichtentext bzw. Metadaten vermerken.

## 4. OBLIGATORISCHES TESTING (Zero-Bug-Policy)
Jedes erstellte Modul MUSS automatisierte Tests enthalten!
- Lege für jedes Modul zwingend das Verzeichnis `tests/` mit `__init__.py` und `test_*.py` an.
- Nutze `odoo.tests.common.TransactionCase`.
- Schreibe mindestens 2 Unit-Tests pro Modul:
  1. **Happy Path:** Erstellen eines Datensatzes und Prüfung der Standardwerte/Berechnungen.
  2. **Validation / Edge Case:** Prüfung von Pflichtfeldern, Exceptions oder Sonderfällen (z. B. fehlerhafte Rahmennummer, negative Akkukapazität).

## 5. Docker Dev-Container & Lokale Testumgebung
Für die lokale Entwicklung und das Ausführen von Tests steht ein dedizierter Docker-Dev-Container bereit (`Dockerfile.dev` und `docker-compose.yml`).

### Container-Verwaltung & Services
- **Dev-Container starten (Hintergrund):**
  ```bash
  docker compose up -d
  ```
- **Container-Logs einsehen:**
  ```bash
  docker compose logs -f odoo-dev
  ```
- **Dev-Container stoppen:**
  ```bash
  docker compose down
  ```

### Ports & Entwicklungs-Features
- **Web-Interface:** `http://localhost:8069`
- **Longpolling / WebSockets:** Port `8072`
- **Remote Debugging (`debugpy`):** Port `5678`
- **Live-Reloading & Vorschau vor Commit:** Odoo startet im Dev-Modus (`--dev=xml,reload,qweb,sql,werkzeug`). Änderungen in `custom_addons/` werden live nachgeladen. Entwickler und Tester (z. B. Wolfgang) können Anpassungen direkt unter `http://localhost:8069` im Browser testen und verifizieren, **bevor** Änderungen committet oder gepusht werden.
- **Benutzerhandbuch für Einsteiger:** Eine verständliche Schritt-für-Schritt-Anleitung für nicht-technische Anwender ist in [`USER_GUIDE.md`](USER_GUIDE.md) hinterlegt.

### Tests & Linter im Dev-Container ausführen
Tests und Code-Quality-Prüfungen werden direkt im `odoo-dev`-Container ausgeführt:
- **Pre-Commit Hooks ausführen (Formatierung & Linting vor Commit):**
  ```bash
  pre-commit run --all-files
  ```
- **Modultests ausführen (Pflicht vor jedem Commit, Port 8070 gegen Port-Kollisionen):**
  ```bash
  docker compose exec odoo-dev odoo --test-enable --stop-after-init -u <addon_name> -d dev_db --db_host=odoo-db-dev -r odoo -w odoopass --http-port=8070
  ```
- **Pre-Review Lint & Format Compound Check (vor Code-Review):**
  ```bash
  docker compose exec odoo-dev bash -c "black --check /mnt/extra-addons/<addon> && flake8 --config=/mnt/extra-addons/.flake8 /mnt/extra-addons/<addon>"
  ```
- **Spezifische Test-Tags ausführen:**
  ```bash
  docker compose exec odoo-dev odoo --test-tags /<addon_name> --stop-after-init -d dev_db --db_host=odoo-db-dev -r odoo -w odoopass --http-port=8070
  ```
- **Code-Qualität & Linting einzeln prüfen:**
  ```bash
  docker compose exec odoo-dev flake8 --config=/mnt/extra-addons/.flake8 /mnt/extra-addons/<addon>
  docker compose exec odoo-dev pylint --load-plugins=pylint_odoo /mnt/extra-addons/<addon>
  docker compose exec odoo-dev black --check /mnt/extra-addons/<addon>
  ```

## 6. Externe Anbindungen & API-Freundlichkeit
- Schreibe Geschäftslogik in öffentliche Python-Methoden, sodass diese über die Odoo JSON-RPC API sauber von externen TypeScript/Node-Services aufgerufen werden können.
- Vermeide Logik, die ausschließlich an Frontend-Buttons gebunden ist.

## 7. Referenz-Code (Odoo Core) & Arbeitsverzeichnisse
- Dein Arbeitsverzeichnis für neue Module ist AUSSCHLIESSLICH `custom_addons/`.
- **Speicherort des Core-Codes:** Liegt im Ordner `odoo_core/` im Root des Workspace (insbesondere `odoo_core/addons/` für Standardmodule wie `sale`, `product`, `stock`, `account`, `base`).
- **ABSOLUTE REGEL:** Du darfst NIEMALS Dateien im Ordner `odoo_core/` verändern oder erstellen. Dieser Ordner dient dir nur als Read-Only-Referenz (Lexikon) zur Vermeidung von Halluzinationen.
- **Was tun, wenn `odoo_core/` fehlt oder leer ist?**
  Falls der Ordner nicht existiert oder leer ist, lade den Odoo Core automatisch im Terminal herunter:
  ```bash
  git clone --depth 1 -b 19.0 https://github.com/odoo/odoo.git odoo_core
  ```
- Externe Python-Pakete können in einer `requirements.txt` erfasst werden.

## 8. Workflow-Abschluss
- **Navigation Steering & Kontext-Effizienz:** Nutze `.scratch/<feature>/issues/`-Tickets und `docs/adr/` als Single Sources of Truth für Spezifikationen und Architekturentscheidungen, anstatt wiederholt massive rohe Planungsdateien (`plans/*.txt`) vollständig einzulesen.
Wenn du eine Aufgabe bearbeitest:
1. Schreibe den Code nach OCA-Standard in `custom_addons/`.
2. Schreibe die Unit-Tests in `tests/`.
3. Validiere Manifest und XML-Syntax.
4. Führe den Pre-Review Compound Check und die Modultests im lokalen Container aus:
   ```bash
   docker compose exec odoo-dev bash -c "black --check /mnt/extra-addons/<addon> && flake8 --config=/mnt/extra-addons/.flake8 /mnt/extra-addons/<addon>"
   docker compose exec odoo-dev odoo --test-enable --stop-after-init -u <addon_name> -d dev_db --db_host=odoo-db-dev -r odoo -w odoopass --http-port=8070
   ```
5. **Lokale Live-Prüfung ermöglichen:** Informiere den Nutzer, dass das Feature lokal unter `http://localhost:8069` im Browser bereitsteht und geprüft werden kann (Details siehe [`USER_GUIDE.md`](USER_GUIDE.md)), bevor der Code festgeschrieben wird.
6. Führe im Terminal aus, um den Code zunächst in die **DEV-Umgebung** zu deployen:
   ```bash
   git add .
   git commit -m "feat/test: [Beschreibung des Features inkl. Tests]"
   git push origin dev
   ```
7. Erkläre Wolfgang kurz:
   - Dass das Feature nun auf `odoo-dev.ebike-haus.de` zum ausgiebigen Testen bereitsteht.
   - Welches Modul in Odoo aktiviert bzw. aktualisiert werden muss.
   - Was die automatischen Tests abdecken und wie er das Feature im Laden testen kann.
8. Sobald das Feature auf DEV freigegeben wurde, öffne einen Pull Request von `dev` auf `main` oder führe einen Merge aus, um das Live-Deployment auf `odoo.ebike-haus.de` auszulösen.

## 9. Agent-Skills (Claude Code)
- Projekt-Skills liegen in `.claude/skills/` und stehen in Claude Code als `/<skill-name>` bereit. Quelle: [mattpocock/skills](https://github.com/mattpocock/skills), Versionen laut `skills-lock.json`.
- Installiert (kuratierte Auswahl): `to-spec`, `to-tickets`, `implement-spec`, `implement`, `grill-me`, `grill-with-docs`, `grilling`, `domain-modeling`, `triage`, `tdd`, `diagnosing-bugs`, `improve-codebase-architecture`, `codebase-design`, `handoff`, `research`, `retro`, `setup-matt-pocock-skills`.
- Bewusst nicht installiert: TypeScript-spezifische Skills, Schreib-/Lern-Skills, `code-review` (würde das eingebaute `/code-review` von Claude Code überdecken; `implement`/`implement-spec` nutzen dieses stattdessen) und `git-guardrails-claude-code` (blockiert `git push` und widerspricht damit Abschnitt 8).
- `.agents/skills/` ist die Kopie für andere Agenten (Zoo Code). Wird ein Skill aktualisiert, beide Ordner gleich halten.
