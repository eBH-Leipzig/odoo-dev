# Copyright 2026 eBike-Haus.de GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import logging

_logger = logging.getLogger(__name__)

#: Kontenrahmen für die Buchhaltung (Export nach Collmex).
EBH_CHART_TEMPLATE = "de_skr03"


def post_init_hook(env):
    """Einmalige Einrichtung nach der Installation von ebh_base.

    - Deutsch als Sprache aktivieren und für die Firma setzen.
    - Deutschen Kontenrahmen laden, falls noch keiner (oder nur der
      generische) installiert ist und noch nicht gebucht wurde.
    """
    company = env.ref("base.main_company")

    env["res.lang"]._activate_lang("de_DE")
    company.partner_id.lang = "de_DE"

    company._ebh_ensure_chart_template(EBH_CHART_TEMPLATE)
