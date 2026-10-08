# PROJEKT-RICHTLINIEN: eBike-Haus Leipzig (eBH) - Odoo 18 WaWi

## 1. Über das Unternehmen & Einsatzbereich
- Fahrrad- und E-Bike-Fachhandel in Leipzig.
- Einsatzbereich: Warenwirtschaft (WaWi), Kasse (POS), Werkstatt, Seriennummern-Tracking, Dienstrad-Leasing.

## 2. Technische Infrastruktur
- Plattform: Odoo 18.0 Community Edition (Docker auf Hostinger VPS).
- Sprache Backend: Python 3 (strikt deklaratives ORM).
- Schnittstellen: JSON-RPC fähig für externe Node.js/TypeScript-Services.
- Git & Deployment: Jeder Push auf `main` deployt vollautomatisch via GitHub Actions auf den VPS.

## 3. Architektur- & Codestandards (OCA-Richtlinien)
- **Modul-Architektur:** Jedes Feature ist ein eigenes Modul im Root-Verzeichnis (entspricht `extra-addons/`).
- **Niemals Core verändern:** Ausschließlich `_inherit` in Python und `<xpath>` in XML nutzen.
- **OCA-Konventionen:**
  - Folge den Standards der *Odoo Community Association*.
  - Saubere Trennung: Datenmodell (`models/`), Benutzeroberfläche (`views/`), Sicherheit (`security/`) und Tests (`tests/`).
  - Keine veralteten Attribute in XML (nutze `invisible="..."`, `readonly="..."`).
- **Sicherheit & Rechte:**
  - Jedes neue Modell MUSS in `security/ir.model.access.csv` Berechtigungen definieren.
  - Verwende niemals rohe SQL-Befehle, sondern immer das Odoo-ORM (`self.env[...]`).

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

## 6. Workflow-Abschluss für Claude
Wenn du eine Aufgabe bearbeitest:
1. Schreibe den Code nach OCA-Standard.
2. Schreibe die Unit-Tests in `tests/`.
3. Validiere Manifest und XML-Syntax.
4. Führe im Terminal aus:
   ```
   git add .
   git commit -m "feat/test: [Beschreibung des Features inkl. Tests]"
   git push origin main
   ```
5. Erkläre Wolfgang kurz:
   - Welches Modul in Odoo aktiviert werden muss.
   - Was die automatischen Tests abdecken und wie er das Feature im Laden testen kann.
