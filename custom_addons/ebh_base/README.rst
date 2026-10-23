=====================
eBH Basis-Einrichtung
=====================

Grundmodul für das eBike-Haus Leipzig. Die Installation richtet ein:

* **Apps:** Kontakte, Verkauf, Einkauf, Lager, Kasse, Rechnungsstellung,
  deutsche Lokalisierung.
* **Firmenstammdaten** der eBike-Haus.de GmbH (aus Cycly und Impressum):
  Anschrift, Kontakt, USt-IdNr., Steuernummer, Handelsregister,
  Fußzeile für Belege.
* **Kontenrahmen SKR04** (wie in Cycly), falls noch keiner geladen ist. Ein vorhandener
  Kontenrahmen wird nie überschrieben.
* **Lager legt das Modul nicht (mehr) an.** Lager werden direkt in der
  Datenbank gepflegt (siehe ``docs/EINRICHTUNG.md``). Bis Version 19.0.1.0.1
  legte das Modul das Außenlager an; dieses wurde am 23.10.2026 auf DEV vom
  Modul entkoppelt.

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
