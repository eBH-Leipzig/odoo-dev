# Copyright 2026 eBike-Haus.de GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import logging

from odoo import models

_logger = logging.getLogger(__name__)

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
        if not self.chart_template or not self.chart_template.startswith("de_"):
            issues.append("Kein deutscher Kontenrahmen geladen")
        if self.currency_id.name != "EUR":
            issues.append("Firmenwährung ist nicht EUR")

        warehouses = self.env["stock.warehouse"].search([("company_id", "=", self.id)])
        if len(warehouses) < 2:
            issues.append("Laden und Außenlager sind nicht beide angelegt")

        return {"ok": not issues, "issues": issues}

    def _ebh_ensure_chart_template(self, template_code):
        """Lädt den deutschen Kontenrahmen, falls noch keiner geladen ist.

        Ein bereits geladener Kontenrahmen wird nie überschrieben.
        Während einer Modulinstallation wird das Laden auf den Zeitpunkt
        verschoben, an dem die Registry vollständig geladen ist (gleiches
        Vorgehen wie im Standardmodul ``account``).
        """
        self.ensure_one()
        if self.chart_template:
            if self.chart_template != template_code:
                _logger.warning(
                    "ebh_base: Firma %s hat bereits den Kontenrahmen %s, "
                    "%s wird nicht geladen.",
                    self.name,
                    self.chart_template,
                    template_code,
                )
            return False

        company_id = self.id

        def _load(env):
            env["account.chart.template"].try_loading(
                template_code, env["res.company"].browse(company_id)
            )

        if self.env.registry.loaded:
            _load(self.env)
        else:
            self.env.registry._auto_install_template = _load
        return True
