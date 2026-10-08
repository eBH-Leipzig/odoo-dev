# PROJEKT-RICHTLINIEN: eBike-Haus Leipzig (eBH) - Odoo WaWi

## 1. Über das Unternehmen & Einsatzbereich
- Fahrrad- und E-Bike-Fachhandel in Leipzig.
- Einsatzbereich: Warenwirtschaft (WaWi), Kasse (POS), Werkstatt, Seriennummern-Tracking, Dienstrad-Leasing.

## 2. Technische Infrastruktur & Versionierung
- Plattform: Odoo Community Edition (Docker auf Hostinger VPS sowie lokaler Docker Dev-Container).
- Version: Gesteuert über `.env` (`ODOO_VERSION=19.0`).
- Lokaler Dev-Stack: PostgreSQL 16 (`db`), Odoo 19.0 mit Dev-Paketen (`web` via `Dockerfile.dev`).
- Sprache Backend: Python 3 (strikt deklaratives ORM).
- Schnittstellen: JSON-RPC fähig für externe Node.js/TypeScript-Services.
- Git & Deployment: Jeder Push auf `main` deployt vollautomatisch via GitHub Actions auf den VPS (`.github/workflows/deploy.yml`).

## 3. Architektur- & Codestandards (OCA-Richtlinien)
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
  docker compose logs -f web
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
Tests und Code-Quality-Prüfungen werden direkt im Odoo-Container ausgeführt:
- **Modultests ausführen (Pflicht vor jedem Commit):**
  ```bash
  docker compose exec web odoo -d postgres --test-enable --stop-after-init -i <modul_name>
  ```
- **Spezifische Test-Tags ausführen:**
  ```bash
  docker compose exec web odoo -d postgres --test-tags /<modul_name> --stop-after-init
  ```
- **Code-Qualität & Linting prüfen:**
  ```bash
  docker compose exec web flake8 /mnt/extra-addons/<modul_name>
  docker compose exec web pylint --load-plugins=pylint_odoo /mnt/extra-addons/<modul_name>
  docker compose exec web black --check /mnt/extra-addons/<modul_name>
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
Wenn du eine Aufgabe bearbeitest:
1. Schreibe den Code nach OCA-Standard in `custom_addons/`.
2. Schreibe die Unit-Tests in `tests/`.
3. Validiere Manifest und XML-Syntax.
4. Führe die Tests und Linter im lokalen Docker-Container aus (`docker compose exec web odoo -d postgres --test-enable --stop-after-init -i <modul_name>`).
5. **Lokale Live-Prüfung ermöglichen:** Informiere den Nutzer, dass das Feature lokal unter `http://localhost:8069` im Browser bereitsteht und geprüft werden kann (Details siehe [`USER_GUIDE.md`](USER_GUIDE.md)), bevor der Code festgeschrieben wird.
6. Führe im Terminal aus:
   ```bash
   git add .
   git commit -m "feat/test: [Beschreibung des Features inkl. Tests]"
   git push origin main
   ```
7. Erkläre Wolfgang kurz:
   - Welches Modul in Odoo aktiviert bzw. aktualisiert werden muss.
   - Was die automatischen Tests abdecken und wie er das Feature im Laden testen kann.
