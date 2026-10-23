=====================
eBH Basis-Einrichtung
=====================

Schlankes Grundmodul für das eBike-Haus Leipzig.

* **Apps:** installiert als Abhängigkeiten Kontakte, Verkauf, Einkauf, Lager,
  Kasse, Rechnungsstellung und die deutsche Lokalisierung.
* **Einrichtungs-Prüfung:** ``res.company.ebh_get_setup_status()`` liefert
  ``{"ok": bool, "issues": [...]}`` (Apps, Land DE, USt-IdNr., Kontenrahmen
  SKR04, Währung EUR, mindestens zwei Lager). Per JSON-RPC abfragbar, z. B. vor
  einem Datenimport.

Das Modul legt **keine Daten** an (Grundsatz „Datenbank vor Modul“, siehe
``CLAUDE.md``). Firmendaten, Lager und Kontenrahmen werden in der Datenbank
nach ``docs/EINRICHTUNG.md`` gepflegt.

Achtung Kontenrahmen
====================

Wird das Modul auf einer Datenbank mit Land Deutschland installiert, lädt Odoo
mit der Rechnungsstellung automatisch **SKR03**. Direkt danach – bevor irgendetwas
gebucht wird – unter Rechnungsstellung › Einstellungen auf **SKR04** umstellen
(geht nur ohne Buchungen). Die Einrichtungs-Prüfung meldet einen falschen
Kontenrahmen.

Versionen
=========

* 19.0.1.1.0 – Firmendaten und automatisches Laden von SKR04 entfernt.
* 19.0.1.0.2 – Lager-Daten entfernt.
* 19.0.1.0.1 – Kontenrahmen SKR04 statt SKR03.

Update von 19.0.1.0.1 oder älter: vorher das Außenlager abkoppeln (Eintrag
``ebh_base.warehouse_aussenlager`` in ``ir.model.data`` löschen), sonst löscht
Odoo beim Update das Lager.
