# Copyright 2026 eBike-Haus.de GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import models

#: Apps, die für den Betrieb des eBike-Haus installiert sein müssen.
EBH_REQUIRED_MODULES = (
    "contacts",
    "sale_management",
    "purchase",
    "stock",
    "point_of_sale",
    "account",
    "l10n_de",
)


class ResCompany(models.Model):
    _inherit = "res.company"

    def ebh_get_setup_status(self):
        """Prüft die Basis-Einrichtung der Firma.

        Öffentlich, damit externe Services (JSON-RPC) den Zustand abfragen
        können, z. B. vor einem Datenimport aus Cycly.

        :return: dict mit ``ok`` (bool) und ``issues`` (Liste von Texten)
        """
        self.ensure_one()
        issues = []

        installed = set(
            self.env["ir.module.module"]
            .sudo()
            .search(
                [
                    ("name", "in", EBH_REQUIRED_MODULES),
                    ("state", "=", "installed"),
                ]
            )
            .mapped("name")
        )
        for module in EBH_REQUIRED_MODULES:
            if module not in installed:
                issues.append(f"App nicht installiert: {module}")

        if self.country_id.code != "DE":
            issues.append("Firmensitz ist nicht Deutschland")
        if not self.vat:
            issues.append("USt-IdNr. fehlt")
        if self.chart_template != "de_skr04":
            issues.append("Kontenrahmen ist nicht SKR04")
        if self.currency_id.name != "EUR":
            issues.append("Firmenwährung ist nicht EUR")

        warehouses = self.env["stock.warehouse"].search([("company_id", "=", self.id)])
        if len(warehouses) < 2:
            issues.append("Laden und Außenlager sind nicht beide angelegt")

        return {"ok": not issues, "issues": issues}
