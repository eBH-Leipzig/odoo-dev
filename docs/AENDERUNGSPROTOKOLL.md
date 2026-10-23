# Änderungsprotokoll Odoo 19 (eBike-Haus)

Jede Änderung an DEV oder PROD mit Datum, System und Art. Grundlage für den
gleichen Aufbau in PROD. Checkliste: [`EINRICHTUNG.md`](EINRICHTUNG.md).
Vorläufer: Prototyp auf Odoo 20 (`C:\odoo-addons\AENDERUNGSPROTOKOLL.md` auf dem Laden-PC).

| Kennzeichen | Bedeutung |
|---|---|
| **[EINST]** | Einstellung, Recht, Standard-Werkzeug in der Datenbank (Stufe 2–4) – in PROD gleich nachklicken |
| **[MODUL]** | Code in `custom_addons/` – kommt per Git |
| **[SERVER]** | Server/Docker – Sache des ITlers |
| **[TEST]** | Testdaten – **nicht** übernehmen |

## 23.10.2026 – DEV (`odoo-dev.ebike-haus.de`, DB `dev_db`), durch Claude

Vorgefunden: Odoo 19.0-20261015; installiert u. a. Verkauf, Lager, Kasse, pos_sale, Einkauf,
Rechnungsstellung, l10n_de sowie `ebh_base` (19.0.1.0.1, SKR04 geladen, Firmendaten) und `ebh_mail`
(Code nicht im Repo). 0 Buchungszeilen.

| Art | Änderung | Details |
|---|---|---|
| [EINST] | Apps | `base_automation` (Automatisierungsregeln) und `project` (Projekt) installiert |
| [EINST] | Preise inkl. Steuer | Einstellung `account_price_include = tax_included` (vorher `tax_excluded`) |
| [EINST] | Einkaufssteuern netto | alle 29 Einkaufssteuern (auch inaktive): `price_include_override = tax_excluded` |
| [EINST] | Einstellungen | Varianten, Los-/Seriennummern, Lagerorte an; Abrechnung nach bestellter Menge (`default_invoice_policy = order`); Seriennummern auf Rechnungen an; Standard-Incoterm leer |
| [EINST] | Preisliste | „Default“ (USD) → „Standard“ (EUR) |
| [EINST] | Lager | „Laden Johannisplatz“/LADEN → „Laden Leipzig“/WH; „Außenlager“/AUSL → „Außenlager“/AUS; Laden wird aus Außenlager nachgeschoben (`resupply_wh_ids`) |
| [EINST] | Reservierung | Lieferaufträge und Kassen-Vorgänge beider Lager: `reservation_method = manual` |
| [EINST] | Wareneingang | Eingänge beider Lager: neue Seriennummern erlaubt, Etiketten automatisch drucken (Format folgt) |
| [EINST] | Kasse | Journal „Kasse Laden“ (KAS), Konto auf **1600** gesetzt (Odoo-Vorschlag 1601; Cycly: 1600 Kasse Laden, 1601 Kasse Büro); Zahlarten „Bar“ (Kasse Laden) und „Karte (Terminal separat)“ (Bank); Kasse „Laden Leipzig“ mit Preisliste „Standard“ |
| [EINST] | Nummernkreise | „Fahrradnummer“ (`ebh.fahrrad`, Präfix EBH-, 4 Stellen, ab 1); „Artikelnummer“ (`ebh.artikelnummer`, ab 56263 = höchste Cycly-SKU + 1) |
| [EINST] | Automatisierungsregeln | „Artikelnummer automatisch vergeben (Artikel)“ auf `product.template` und „… (Varianten)“ auf `product.product`, je beim Anlegen; Python-Code siehe Regel. Getestet (ohne Nummer, mit Nummer, 2 Varianten) |
| [TEST] | Testdaten Artikelnummer | 3 Testartikel + Testattribut angelegt und wieder gelöscht; Zähler auf 56263 zurückgesetzt |
| [EINST] | Werbesperre | Felder `x_keine_werbung` (Ja/Nein, protokolliert) und `x_keine_werbung_grund` (Widerspruch des Kunden / Interne Entscheidung, protokolliert); Ansicht `res.partner.form.ebh.werbesperre` (unter Stichwörter, Grund nur sichtbar und Pflicht bei Sperre) |
| [EINST] | Benachrichtigungen | Benutzer `admin`: „in Odoo“ statt per Mail |

Hinweis: Während der Arbeit war DEV etwa eine Minute nicht erreichbar (502/500), ohne Deployment.
Danach waren alle Daten unverändert vorhanden. Ursache unbekannt → ITler.
