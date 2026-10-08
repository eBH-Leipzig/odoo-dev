# Copyright 2026 eBike-Haus.de GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "eBH Basis-Einrichtung",
    "summary": "Basis-Apps, Firmenstammdaten und Lager für das eBike-Haus Leipzig",
    "version": "19.0.1.0.1",
    "category": "Hidden/Tools",
    "author": "eBike-Haus.de GmbH",
    "website": "https://ebike-haus.de",
    "license": "LGPL-3",
    "depends": [
        # Kunden & Kontakte
        "contacts",
        # Verkauf (Angebote, Aufträge)
        "sale_management",
        # Einkauf (Bestellungen bei Lieferanten)
        "purchase",
        # Lager / Warenwirtschaft
        "stock",
        "sale_stock",
        "purchase_stock",
        # Kasse
        "point_of_sale",
        # Rechnungsstellung
        "account",
        # Deutsche Lokalisierung (Kontenrahmen SKR03/SKR04, Steuern)
        "l10n_de",
    ],
    "data": [
        "data/res_company_data.xml",
        "data/stock_warehouse_data.xml",
    ],
    "post_init_hook": "post_init_hook",
}
