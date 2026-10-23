# Copyright 2026 eBike-Haus.de GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "eBike-Haus Mail Integration",
    "summary": (
        "Mail server configuration, catchall routing, " "and unassigned mail handling"
    ),
    "version": "19.0.1.0.0",
    "category": "Productivity/Mail",
    "author": "eBike-Haus",
    "website": "https://ebike-haus.de",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "ebh_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ebh_unassigned_mail_views.xml",
        "views/ebh_mail_menus.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
}
