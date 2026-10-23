# Copyright 2026 eBike-Haus.de GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEbhBase(TransactionCase):
    """ebh_base bringt nur Apps und die Einrichtungs-Prüfung mit.

    Stammdaten, Lager und Kontenrahmen werden in der Datenbank gepflegt
    (Grundsatz „Datenbank vor Modul“), deshalb legen die Tests diese
    Daten so an, wie sie laut Einrichtungs-Checkliste in der DB stehen.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")

    def _einrichten_wie_checkliste(self):
        self.company.write(
            {
                "country_id": self.env.ref("base.de").id,
                "currency_id": self.env.ref("base.EUR").id,
                "vat": "DE340468638",
            }
        )
        if self.company.chart_template != "de_skr04":
            self.env["account.chart.template"].try_loading(
                "de_skr04", self.company, install_demo=False
            )
        if self.env["stock.warehouse"].search_count([]) < 2:
            self.env["stock.warehouse"].create({"name": "Außenlager", "code": "AUS"})

    # --- Happy Path -------------------------------------------------------

    def test_setup_status_ok(self):
        """Eingerichtet wie in der Checkliste → Prüfung meldet nichts."""
        self._einrichten_wie_checkliste()
        status = self.company.ebh_get_setup_status()
        self.assertTrue(status["ok"], status["issues"])

    def test_module_owns_no_data(self):
        """Das Modul besitzt keine Stammdaten, Lager oder Firmeneinträge."""
        owned = self.env["ir.model.data"].search(
            [
                ("module", "=", "ebh_base"),
                ("model", "in", ["stock.warehouse", "res.company", "res.partner"]),
            ]
        )
        self.assertFalse(owned)

    # --- Validation / Edge Cases -----------------------------------------

    def test_setup_status_reports_missing_vat(self):
        """Fehlt die USt-IdNr., meldet die Prüfung das."""
        self._einrichten_wie_checkliste()
        self.company.vat = False
        status = self.company.ebh_get_setup_status()
        self.assertFalse(status["ok"])
        self.assertIn("USt-IdNr. fehlt", status["issues"])

    def test_setup_status_reports_wrong_chart(self):
        """Ein anderer Kontenrahmen als SKR04 wird gemeldet."""
        self._einrichten_wie_checkliste()
        self.company.chart_template = "de_skr03"
        status = self.company.ebh_get_setup_status()
        self.assertIn("Kontenrahmen ist nicht SKR04", status["issues"])
