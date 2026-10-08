=====================
eBH Basis-Einrichtung
=====================

Grundmodul für das eBike-Haus Leipzig. Die Installation richtet ein:

* **Apps:** Kontakte, Verkauf, Einkauf, Lager, Kasse, Rechnungsstellung,
  deutsche Lokalisierung.
* **Firmenstammdaten** der eBike-Haus.de GmbH (aus Cycly und Impressum):
  Anschrift, Kontakt, USt-IdNr., Steuernummer, Handelsregister,
  Fußzeile für Belege.
* **Kontenrahmen SKR03**, falls noch keiner geladen ist. Ein vorhandener
  Kontenrahmen wird nie überschrieben.
* **Lager:** "Laden Johannisplatz" (LADEN) als Hauptlager und
  "Außenlager" (AUSL).

Alle Daten sind ``noupdate``: Änderungen in Odoo bleiben bei Modul-Updates
erhalten.

Noch nicht enthalten
====================

* Bankverbindung (bitte in Odoo unter Rechnungsstellung → Konfiguration →
  Bankkonten erfassen).
* Logo.
* Nachschubregel Außenlager → Laden.

API
===

``res.company.ebh_get_setup_status()`` liefert ``{"ok": bool, "issues": [...]}``
und kann per JSON-RPC abgefragt werden, z. B. vor einem Datenimport.
