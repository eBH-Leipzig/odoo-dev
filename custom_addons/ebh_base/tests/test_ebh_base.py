# Copyright 2026 eBike-Haus.de GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEbhBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        # Das Außenlager wird in der Datenbank angelegt, nicht vom Modul.
        if cls.env["stock.warehouse"].search_count([]) < 2:
            cls.env["stock.warehouse"].create({"name": "Außenlager", "code": "AUS"})

    # --- Happy Path -------------------------------------------------------

    def test_company_master_data(self):
        """Firmenstammdaten aus Cycly sind übernommen."""
        company = self.company
        self.assertEqual(company.name, "eBike-Haus.de GmbH")
        self.assertEqual(company.street, "Johannisplatz 21")
        self.assertEqual(company.zip, "04103")
        self.assertEqual(company.city, "Leipzig")
        self.assertEqual(company.country_id.code, "DE")
        self.assertEqual(company.state_id, self.env.ref("base.state_de_sn"))
        self.assertEqual(company.vat, "DE340468638")
        self.assertEqual(company.company_registry, "HRB 38554")
        self.assertEqual(company.currency_id.name, "EUR")
        self.assertEqual(company.partner_id.lang, "de_DE")

    def test_module_owns_no_warehouse(self):
        """Lager gehören der Datenbank, nicht dem Modul (Grundsatz DB vor Modul)."""
        owned = self.env["ir.model.data"].search(
            [("module", "=", "ebh_base"), ("model", "=", "stock.warehouse")]
        )
        self.assertFalse(owned)

    def test_german_chart_of_accounts(self):
        """Deutscher Kontenrahmen ist geladen, Basis-Einrichtung vollständig."""
        self.assertEqual(self.company.chart_template, "de_skr04")
        status = self.company.ebh_get_setup_status()
        self.assertTrue(status["ok"], status["issues"])

    # --- Validation / Edge Cases -----------------------------------------

    def test_invalid_tax_number_rejected(self):
        """Eine Steuernummer, die nicht zu Sachsen passt, wird abgelehnt."""
        with self.assertRaises(ValidationError):
            self.company.l10n_de_stnr = "12345"

    def test_setup_status_reports_missing_vat(self):
        """Fehlt die USt-IdNr., meldet die Statusprüfung das."""
        self.company.vat = False
        status = self.company.ebh_get_setup_status()
        self.assertFalse(status["ok"])
        self.assertIn("USt-IdNr. fehlt", status["issues"])

    def test_existing_chart_not_overwritten(self):
        """Ein bereits geladener Kontenrahmen wird nie ersetzt."""
        self.assertFalse(self.company._ebh_ensure_chart_template("de_skr03"))
        self.assertEqual(self.company.chart_template, "de_skr04")
