# PROJEKT-RICHTLINIEN: eBike-Haus Leipzig (eBH) - Odoo WaWi

## 1. Über das Unternehmen & Einsatzbereich
- Fahrrad- und E-Bike-Fachhandel in Leipzig.
- Einsatzbereich: Warenwirtschaft (WaWi), Kasse (POS), Werkstatt, Seriennummern-Tracking, Dienstrad-Leasing.

## 2. Technische Infrastruktur & Versionierung
- Plattform: Odoo Community Edition (Docker auf Hostinger VPS).
- Version: Gesteuert über `.env` (`ODOO_VERSION=19.0`).
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

## 5. Externe Anbindungen & API-Freundlichkeit
- Schreibe Geschäftslogik in öffentliche Python-Methoden, sodass diese über die Odoo JSON-RPC API sauber von externen TypeScript/Node-Services aufgerufen werden können.
- Vermeide Logik, die ausschließlich an Frontend-Buttons gebunden ist.

## 6. Referenz-Code (Odoo Core) & Arbeitsverzeichnisse
- Dein Arbeitsverzeichnis für neue Module ist AUSSCHLIESSLICH `custom_addons/`.
- Im Ordner `odoo_core/` liegt der originale Odoo Quellcode.
- Nutze `odoo_core/`, um proaktiv nachzusehen, wie originale Modelle, Methoden (z. B. `_compute_*`) oder XML-Views aufgebaut sind, bevor du Code schreibst.
- **ABSOLUTE REGEL:** Du darfst NIEMALS Dateien im Ordner `odoo_core/` verändern oder erstellen. Dieser Ordner dient dir nur als Read-Only-Referenz (Lexikon) zur Vermeidung von Halluzinationen.
- Externe Python-Pakete können in einer `requirements.txt` erfasst werden.

## 7. Workflow-Abschluss
Wenn du eine Aufgabe bearbeitest:
1. Schreibe den Code nach OCA-Standard in `custom_addons/`.
2. Schreibe die Unit-Tests in `tests/`.
3. Validiere Manifest und XML-Syntax.
4. Führe im Terminal aus:
   ```bash
   git add .
   git commit -m "feat/test: [Beschreibung des Features inkl. Tests]"
   git push origin main
   ```
5. Erkläre Wolfgang kurz:
   - Welches Modul in Odoo aktiviert werden muss.
   - Was die automatischen Tests abdecken und wie er das Feature im Laden testen kann.
