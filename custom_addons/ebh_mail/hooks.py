# Copyright 2026 eBike-Haus.de GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import logging
import os

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Post-installation hook to configure mail servers and routing."""
    _configure_alias_domain(env)
    _configure_outgoing_mail_server(env)
    _configure_incoming_mail_server(env)


def _configure_alias_domain(env):
    alias_domain_name = (
        os.getenv("MAIL_ALIAS_DOMAIN", "ebike-haus.de") or "ebike-haus.de"
    )
    catchall_alias = os.getenv("MAIL_CATCHALL_ALIAS", "kd") or "kd"
    bounce_alias = os.getenv("MAIL_BOUNCE_ALIAS", "bounce") or "bounce"
    default_from = os.getenv("MAIL_DEFAULT_FROM", "kd") or "kd"
    partner_alias = os.getenv("MAIL_PARTNER_ALIAS", "partner") or "partner"

    alias_domain = False
    if "mail.alias.domain" in env:
        domain_vals = {
            "name": alias_domain_name,
            "catchall_alias": catchall_alias,
            "bounce_alias": bounce_alias,
            "default_from": default_from,
        }
        alias_domain = env["mail.alias.domain"].search(
            [("name", "=", alias_domain_name)], limit=1
        )
        if alias_domain:
            alias_domain.write(domain_vals)
        else:
            alias_domain = env["mail.alias.domain"].create(domain_vals)

        # Set company alias domain if supported
        if "res.company" in env and "alias_domain_id" in env["res.company"]._fields:
            companies = env["res.company"].search([])
            companies.write({"alias_domain_id": alias_domain.id})

    # Set up or recognize partner alias (partner@ebike-haus.de) alongside kd and bounce
    if "mail.alias" in env and "ebh.unassigned.mail" in env:
        unassigned_model = env["ir.model"]._get("ebh.unassigned.mail")
        if unassigned_model:
            alias_vals = {
                "alias_name": partner_alias,
                "alias_model_id": unassigned_model.id,
                "alias_contact": "everyone",
            }
            if alias_domain:
                alias_vals["alias_domain_id"] = alias_domain.id
            existing_alias = env["mail.alias"].search(
                [("alias_name", "=", partner_alias)], limit=1
            )
            if existing_alias:
                existing_alias.write(alias_vals)
            else:
                env["mail.alias"].create(alias_vals)

    # Set ir.config_parameter keys for backward compatibility
    config_params = env["ir.config_parameter"].sudo()
    config_params.set_param("mail.catchall.domain", alias_domain_name)
    config_params.set_param("mail.catchall.alias", catchall_alias)
    config_params.set_param("mail.bounce.alias", bounce_alias)
    config_params.set_param("mail.default.from", default_from)
    config_params.set_param("mail.partner.alias", partner_alias)
    _logger.info(
        "Configured alias domain '%s' "
        "(catchall: %s, bounce: %s, default_from: %s, partner: %s)",
        alias_domain_name,
        catchall_alias,
        bounce_alias,
        default_from,
        partner_alias,
    )


def _configure_outgoing_mail_server(env):
    smtp_server = os.getenv("SMTP_SERVER", "mailpit") or "mailpit"
    smtp_port_raw = os.getenv("SMTP_PORT", "1025")
    try:
        smtp_port = int(smtp_port_raw)
    except (ValueError, TypeError):
        smtp_port = 1025

    smtp_user = os.getenv("SMTP_USER") or False
    smtp_password = os.getenv("SMTP_PASSWORD") or False
    smtp_encryption = os.getenv("SMTP_ENCRYPTION", "none") or "none"
    smtp_ssl = os.getenv("SMTP_SSL", "false").lower() in ("true", "1", "yes")

    if smtp_ssl and smtp_encryption == "none":
        smtp_encryption = "ssl"

    mail_server_vals = {
        "name": "Mail Server (Environment)",
        "sequence": 1,
        "smtp_host": smtp_server,
        "smtp_port": smtp_port,
        "smtp_user": smtp_user,
        "smtp_pass": smtp_password,
        "smtp_encryption": smtp_encryption,
    }

    server = env["ir.mail_server"].search(
        [("name", "=", "Mail Server (Environment)")], limit=1
    )
    if server:
        server.write(mail_server_vals)
    else:
        env["ir.mail_server"].create(mail_server_vals)
    _logger.info(
        "Configured outgoing mail server: %s:%s (encryption: %s)",
        smtp_server,
        smtp_port,
        smtp_encryption,
    )


def _configure_incoming_mail_server(env):
    if "fetchmail.server" not in env:
        return

    fetchmail_server = os.getenv("FETCHMAIL_SERVER", "mailpit") or "mailpit"
    fetchmail_port_raw = os.getenv("FETCHMAIL_PORT", "1143")
    try:
        fetchmail_port = int(fetchmail_port_raw)
    except (ValueError, TypeError):
        fetchmail_port = 1143

    fetchmail_type = os.getenv("FETCHMAIL_TYPE", "imap") or "imap"
    fetchmail_user = os.getenv("FETCHMAIL_USER") or False
    fetchmail_password = os.getenv("FETCHMAIL_PASSWORD") or False
    fetchmail_is_ssl = os.getenv("FETCHMAIL_IS_SSL", "false").lower() in (
        "true",
        "1",
        "yes",
    )

    fetchmail_vals = {
        "name": "Odoo Inbox (Environment)",
        "server": fetchmail_server,
        "port": fetchmail_port,
        "server_type": fetchmail_type,
        "user": fetchmail_user,
        "password": fetchmail_password,
        "is_ssl": fetchmail_is_ssl,
    }

    server = env["fetchmail.server"].search(
        [("name", "=", "Odoo Inbox (Environment)")], limit=1
    )
    if server:
        server.write(fetchmail_vals)
    else:
        env["fetchmail.server"].create(fetchmail_vals)
    _logger.info(
        "Configured incoming mail server: %s:%s (%s, SSL: %s)",
        fetchmail_server,
        fetchmail_port,
        fetchmail_type,
        fetchmail_is_ssl,
    )
