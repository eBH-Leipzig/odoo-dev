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
| [EINST] | Artikelnummer | Startwert auf Wunsch von eBH auf **57000** gesetzt (Puffer für neue Cycly-Nummern bis zum Umzug) |
| [EINST] | EU-Steuerzuordnung | „Geschäftspartner EU (mit USt-ID)“: „USt-ID erforderlich“ eingeschaltet. Getestet: NL-Privatkunde → keine Zuordnung (deutsche USt), NL-Firma mit USt-ID → EU, DE-Kunde → Inland |
| [EINST] | Artikelkategorien | Nach alter Shop-Struktur (vor Cycly), bereinigt und von eBH freigegeben: **eBikes** (eCitybike, eTrekkingbike, eSUV, eMountainbike, eKlapprad & Kompaktrad, eGravelbike, eCargo), **Zubehör** (Akku, Bremsen, Elektronik & Display, Gepäckträger & Schutzbleche, Helme, Kette & Tretlager, Laufräder, Lenker & Vorbau, Licht, Motor, Pumpen, Reifen & Schläuche, Sattel & Sattelstütze, Schaltung, Schlösser, Ständer, Taschen & Körbe, Sonstiges), **Werkstatt** (Services & Inspektionen, VanMoof-Teile). Odoo-Standardkategorien (Goods, Services, Expenses, Food) unverändert |
| [EINST] | Kassen-Kategorie | „Fahrräder“ angelegt |
| [EINST] | `ebh_base` vorbereitet | Außenlager vom Modul abgekoppelt (Eintrag `ebh_base.warehouse_aussenlager` in `ir.model.data` gelöscht) – es ist jetzt ein normales Odoo-Lager und bleibt bei einer Deinstallation erhalten. **Deinstallation gestoppt:** `ebh_mail` (ITler) hängt von `ebh_base` ab und würde mit entfernt. Erst Abhängigkeit in `ebh_mail` lösen, dann `ebh_base` deinstallieren und aus dem Repo nehmen |
| [MODUL] | `ebh_base` 19.0.1.0.2 | Bleibt installiert (Entscheidung eBH; `ebh_mail` hängt davon ab). Lager-Daten aus dem Modul entfernt (`data/stock_warehouse_data.xml`) – Lager werden nur noch in der Datenbank gepflegt. Getestet: Neuinstallation (6/6 Tests) und Update einer alten Installation mit vorher abgekoppeltem Lager (Lager bleibt). **Wichtig:** Auf einer Datenbank mit alter Version erst das Lager abkoppeln, dann updaten – sonst löscht Odoo beim Update das Außenlager |
| [EINST] | Attribute | „Farbe“ (Anzeige Farbe) und „Rahmengröße“ (Anzeige Auswahl), beide mit Varianten; Werte legen Admins beim jeweiligen Artikel an |
| [EINST] | Datenblatt | Eigenschaften an „eBikes“ **und allen 7 Unterkategorien** (Odoo nimmt die Definition der Kategorie, in der der Artikel steht – Änderungen daher an allen 8 Kategorien gleich machen). 38 Einträge in 4 Abschnitten: Spezifikationen (Rahmenart, Rahmenmaterial, Raddurchmesser Zoll, Gewicht kg, zul. Gesamtgewicht kg, Ortung, Körpergröße cm), Antrieb (Motor, Unterstützung bis – Standard 25 km/h, Akku, Reichweite, Ladedauer, Display), Ausstattung (Schaltung … Ständer, Federwege mm), Besonderheiten. Grundlage: Prototyp `ebh_datenblatt/data/merkmale.xml`; Farbe/Rahmengröße laufen über Attribute |
| [EINST] | Artikel „Freiposition“ | Referenz FREI, Güter, nicht lagergeführt, 19 % (inkl.), in der Kasse, Kategorie Zubehör / Sonstiges |
| [TEST] | Testrad | „TEST Claude Testrad“ zur Sichtprüfung des Datenblatts angelegt und gelöscht |
| [TEST] | Testdaten EU-Regel | 3 Testkontakte und 3 Angebotsentwürfe angelegt und gelöscht (Angebotsnummern S00001–S00003 dadurch verbraucht, unkritisch) |

Hinweis: Während der Arbeit war DEV etwa eine Minute nicht erreichbar (502/500), ohne Deployment.
Danach waren alle Daten unverändert vorhanden. Ursache unbekannt → ITler.
