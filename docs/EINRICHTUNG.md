# Einrichtungs-Checkliste Odoo 19 (eBike-Haus)

Wird in **DEV** (`odoo-dev.ebike-haus.de`) und später in **PROD** (`odoo.ebike-haus.de`)
gleich abgearbeitet. Neue Einrichtungspunkte kommen hierher, nicht in Code.
Grundlage: Dokument „Odoo-Neuaufbau auf Odoo 19: Bestand und Reihenfolge“ (23.10.2026).
Jede Ausführung wird in [`AENDERUNGSPROTOKOLL.md`](AENDERUNGSPROTOKOLL.md) eingetragen.

Grundsatz: Standard vor Code. 1 Standard → 2 Einstellung/Recht → 3 Standard-Werkzeug
(Eigenschaften, Stichwörter, Aliase, Automatisierungsregeln) → 4 Feld `x_…` →
5 eigenes Modul. Testdaten werden nicht übernommen.

Status: `[ ]` offen · `[x]` erledigt · `[~]` teilweise / mit Anmerkung

## Phase 1 – Apps

| Punkt | DEV | PROD |
|---|---|---|
| Verkauf (`sale_management`), Lager (`stock`), Kasse (`point_of_sale`), Kasse↔Verkauf (`pos_sale`), Einkauf (`purchase`) | [x] | [ ] |
| Rechnungsstellung (`account`) + Deutschland (`l10n_de`) – **Achtung:** Odoo lädt dabei bei Land DE automatisch SKR03 → **sofort danach auf SKR04 umstellen, bevor irgendetwas gebucht wird** (geht nur bei 0 Buchungszeilen) | [x] | [ ] |
| Automatisierungsregeln (`base_automation`), Projekt (`project`, für Posteingang) | [x] | [ ] |
| Sprache Deutsch, Zeitzone Europe/Berlin (alle Benutzer) | [x] | [ ] |

## Firma und Buchhaltung

| Punkt | DEV | PROD |
|---|---|---|
| Firma: eBike-Haus.de GmbH, Johannisplatz 21, 04103 Leipzig, Tel. 0341 97854310, leipzig@ebike-haus.de | [x] | [ ] |
| Währung EUR, Standard-Preisliste auf EUR | [x] | [ ] |
| Kontenrahmen **SKR04** (`de_skr04`, laut Cycly-Kontenplan). PROD: vorher mit Collmex und Steuerberater abgleichen | [x] | [ ] |
| Preise: Firmeneinstellung „inklusive Steuer“; an jeder Einkaufssteuer „exklusive“ (Einkauf netto) | [x] | [ ] |
| Steuerzuordnung „Geschäftspartner EU (mit USt-ID)“: **„USt-ID erforderlich“ einschalten**; EU-Lieferanten mit Land und USt-ID anlegen | [x] | [ ] |

## Einstellungen

| Punkt | DEV | PROD |
|---|---|---|
| Varianten, Seriennummern, Lagerorte einschalten | [x] | [ ] |
| Verkauf: Abrechnung nach bestellter Menge | [x] | [ ] |
| Seriennummern auf Rechnungen anzeigen | [x] | [ ] |
| Incoterms aus | [x] | [ ] |

## Lager

| Punkt | DEV | PROD |
|---|---|---|
| Lager „Laden Leipzig“ (WH) und „Außenlager“ (AUS, Nachschublager) | [x] | [ ] |
| Vorgangstypen Ausgang und Kasse: Reservierung „manuell“ | [x] | [ ] |
| Vorgangstyp Eingang: neue Seriennummern erlauben, Etiketten drucken (Brother-Format folgt) | [~] | [ ] |
| Nummernkreis „Fahrradnummer“: Präfix EBH-, 4 Stellen; an jedem Fahrrad-Artikel als Seriennummern-Sequenz | [~] | [ ] |

## Artikel

| Punkt | DEV | PROD |
|---|---|---|
| Kategorien nach alter Shop-Struktur (siehe Änderungsprotokoll 23.10.), Kassen-Kategorie „Fahrräder“ | [x] | [ ] |
| Attribute Farbe, Rahmengröße | [ ] | [ ] |
| Eigenschaften an der Kategorie Fahrräder (Datenblatt: Spezifikationen, Antrieb, Ausstattung; Liste aus Prototyp `ebh_datenblatt/data/merkmale.xml`) | [ ] | [ ] |
| Artikel „Freiposition“ (nicht lagergeführt, 19 %, in der Kasse) | [ ] | [ ] |
| Automatisierungsregel: neuer Artikel ohne Interne Referenz bekommt die nächste Nummer (Start 57000) | [x] | [ ] |

## Kontakte

| Punkt | DEV | PROD |
|---|---|---|
| Felder `x_keine_werbung` (Ja/Nein) und `x_keine_werbung_grund` (Widerspruch des Kunden / Interne Entscheidung) über den Entwicklermodus, im Kontaktformular anzeigen | [x] | [ ] |

## Kasse

| Punkt | DEV | PROD |
|---|---|---|
| Kasse „Laden Leipzig“ für zwei Arbeitsplätze; Journal „Kasse Laden“ (Konto mit SKR04 abgleichen); Zahlarten „Bar“ und „Karte (Terminal separat)“ | [x] | [ ] |

## Benutzer und Rechte

| Punkt | DEV | PROD |
|---|---|---|
| Je Mitarbeiter ein Benutzer; Artikel, Kategorien und Attribute anlegen nur für Admins | [~] | [ ] |
| Benachrichtigungen „in Odoo“ statt per Mail | [~] | [ ] |
| Später: technischer Benutzer „Claude“ mit eingeschränkten Rechten | [ ] | [ ] |

## E-Mail

| Punkt | DEV | PROD |
|---|---|---|
| Adressen kd@, partner@, bounce@ als echte Adressen, ein Postfach für Odoo | [ ] | [ ] |
| Alias: nicht zugeordnete Mails landen als Aufgabe im Projekt „Posteingang“ | [ ] | [ ] |

## Anmerkungen DEV (23.10.2026)

- **Kontenrahmen:** SKR04 war auf DEV schon geladen (über `ebh_base`), 0 Buchungen.
- **EU-Steuerzuordnung:** „USt-ID erforderlich“ eingeschaltet. EU-Firmen mit USt-ID → steuerfrei, EU-Privatkunden → deutsche USt.
- **Wareneingang:** Neue Seriennummern erlaubt und Etikettendruck an; Etikettenformat (Brother QL-810W) folgt.
- **Fahrradnummer:** Nummernkreis `ebh.fahrrad` (EBH-0001) angelegt. Zuordnung zu Fahrrad-Artikeln, sobald es welche gibt (Phase 4).
- **Artikelnummer:** Nummernkreis `ebh.artikelnummer` ab **57000** (höchste Cycly-SKU am 23.10.: 56262, Puffer bis zum Umzug). Zwei Regeln: eine für Artikel mit
  einer Variante, eine für Artikel mit mehreren Varianten. Getestet: ohne Nummer → 56263; mitgegebene Nummer bleibt;
  Varianten bekommen je eine Nummer. Testdaten gelöscht, Zähler danach auf 57000 gesetzt.
- **Kasse:** Journal „Kasse Laden“ (KAS), Konto **1600** wie in Cycly (Odoo hatte 1601 vergeben; in Cycly ist 1601 „Kasse Büro“).
  Zahlart „Karte“ bucht vorerst auf das Bank-Journal; Cycly nutzt dafür 3610 „Transit Kartenzahlung“ → beim Collmex-Abgleich klären.
- **Rechte:** Im Standard dürfen nur „Administrator“-Rollen (Verkauf/Lager) Artikel, Kategorien und Attribute anlegen. Mitarbeiter
  bekommen deshalb „Benutzer“-Rollen, nicht „Administrator“. Benutzer gibt es noch nicht (nur `admin`, Benachrichtigung „in Odoo“).
- **Nachschub:** Laden Leipzig wird aus dem Außenlager nachgeschoben (Lager › Nachschub aus „Außenlager“).
- **Vorgefunden, nicht von Claude:** Artikel „kaffee“ (Testdatum?) und Modul `ebh_mail` (installiert, Code noch nicht im Repo – ITler arbeitet daran).

## Zu klären

- Fahrradnummer: Dokument sagt 4 Stellen (EBH-0001), der Prototyp nutzte 6 Stellen (EBH-000001).
  Umgesetzt wird laut Dokument (4 Stellen); bei mehr als 9999 Rädern springt die Nummer auf 5 Stellen.
- TSE: angefragt (initOS, Intero), noch nicht gekauft (Stand 23.10.2026).
