# Copyright 2026 eBike-Haus.de GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import os
from email.message import EmailMessage
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

from ..hooks import post_init_hook


@tagged("post_install", "-at_install")
class TestEbhMail(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Kunde Max Mustermann",
                "email": "max.mustermann@example.de",
            }
        )

    def _create_email(
        self,
        subject,
        email_from,
        email_to="kd@ebike-haus.de",
        msg_id="<test.1000@example.de>",
        in_reply_to=None,
        references=None,
        body="Guten Tag!",
    ):
        """Helper to create an EmailMessage and parse it."""
        msg = EmailMessage()
        msg["Message-Id"] = msg_id
        msg["From"] = email_from
        msg["To"] = email_to
        msg["Subject"] = subject
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
        if references:
            msg["References"] = references
        msg.set_content(body)
        msg_dict = self.env["mail.thread"].message_parse(msg)
        return msg, msg_dict

    def test_post_init_hook_configuration(self):
        """Test post_init_hook creates/updates mail servers and alias domain."""
        mock_env = {
            "SMTP_SERVER": "smtp.test-mail.de",
            "SMTP_PORT": "2525",
            "SMTP_USER": "test_smtp_user",
            "SMTP_PASSWORD": "test_smtp_password",
            "SMTP_ENCRYPTION": "starttls",
            "FETCHMAIL_SERVER": "imap.test-mail.de",
            "FETCHMAIL_PORT": "1993",
            "FETCHMAIL_TYPE": "imap",
            "FETCHMAIL_USER": "test_fetch_user",
            "FETCHMAIL_PASSWORD": "test_fetch_password",
            "MAIL_ALIAS_DOMAIN": "test.ebike-haus.de",
            "MAIL_CATCHALL_ALIAS": "support",
            "MAIL_BOUNCE_ALIAS": "mail-bounce",
            "MAIL_DEFAULT_FROM": "support",
        }

        with patch.dict(os.environ, mock_env):
            post_init_hook(self.env)

        # 1. Outgoing mail server
        outgoing = self.env["ir.mail_server"].search(
            [("name", "=", "Mail Server (Environment)")], limit=1
        )
        self.assertTrue(outgoing.exists())
        self.assertEqual(outgoing.smtp_host, "smtp.test-mail.de")
        self.assertEqual(outgoing.smtp_port, 2525)
        self.assertEqual(outgoing.smtp_user, "test_smtp_user")
        self.assertEqual(outgoing.smtp_pass, "test_smtp_password")
        self.assertEqual(outgoing.smtp_encryption, "starttls")

        # 2. Incoming mail server
        incoming = self.env["fetchmail.server"].search(
            [("name", "=", "Odoo Inbox (Environment)")], limit=1
        )
        self.assertTrue(incoming.exists())
        self.assertEqual(incoming.server, "imap.test-mail.de")
        self.assertEqual(incoming.port, 1993)
        self.assertEqual(incoming.server_type, "imap")
        self.assertEqual(incoming.user, "test_fetch_user")
        self.assertEqual(incoming.password, "test_fetch_password")

        # 3. Alias domain & config parameters
        alias_domain = self.env["mail.alias.domain"].search(
            [("name", "=", "test.ebike-haus.de")], limit=1
        )
        self.assertTrue(alias_domain.exists())
        self.assertEqual(alias_domain.catchall_alias, "support")
        self.assertEqual(alias_domain.bounce_alias, "mail-bounce")
        self.assertEqual(alias_domain.default_from, "support")

        params = self.env["ir.config_parameter"].sudo()
        self.assertEqual(params.get_param("mail.catchall.domain"), "test.ebike-haus.de")
        self.assertEqual(params.get_param("mail.catchall.alias"), "support")
        self.assertEqual(params.get_param("mail.bounce.alias"), "mail-bounce")
        self.assertEqual(params.get_param("mail.default.from"), "support")
        self.assertEqual(params.get_param("mail.partner.alias"), "partner")

        # 4. Partner alias
        partner_alias = self.env["mail.alias"].search(
            [("alias_name", "=", "partner")], limit=1
        )
        self.assertTrue(partner_alias.exists())
        self.assertEqual(partner_alias.alias_model_id.model, "ebh.unassigned.mail")

    def test_chatter_reply_routing(self):
        """Inbound email with In-Reply-To routes directly to record chatter."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        order_msg = order.message_post(
            body="Auftragsbestätigung gesendet",
            message_type="comment",
        )
        self.assertTrue(order_msg.message_id)

        reply_msg, reply_dict = self._create_email(
            subject="Re: Auftragsbestätigung",
            email_from=self.partner.email,
            msg_id="<reply.1001@example.de>",
            in_reply_to=order_msg.message_id,
            references=order_msg.message_id,
            body="Vielen Dank, Auftrag ist freigegeben.",
        )

        routes = self.env["mail.thread"].message_route(reply_msg, reply_dict)
        self.assertTrue(routes, "Expected routes for chatter reply")
        target_model, target_id = routes[0][0], routes[0][1]
        self.assertEqual(target_model, "sale.order")
        self.assertEqual(target_id, order.id)

    def test_subject_order_matching(self):
        """Forwarded email with order ref in subject routes to sale.order."""
        order = self.env["sale.order"].create(
            {
                "name": "SO9999",
                "partner_id": self.partner.id,
            }
        )

        fwd_msg, fwd_dict = self._create_email(
            subject="Fwd: Anfrage zu SO9999",
            email_from="mitarbeiter@ebike-haus.de",
            msg_id="<fwd.1002@example.de>",
            body="Hallo, bitte prüfen.\nVon: max.mustermann@example.de\n",
        )

        routes = self.env["mail.thread"].message_route(fwd_msg, fwd_dict)
        self.assertTrue(routes, "Expected route matching order SO9999")
        target_model, target_id = routes[0][0], routes[0][1]
        self.assertEqual(target_model, "sale.order")
        self.assertEqual(target_id, order.id)

        # Verify forwarded metadata banner is injected into chatter body
        self.assertIn("ebh_forwarded_metadata", fwd_dict.get("body", ""))
        self.assertIn("max.mustermann@example.de", fwd_dict.get("body", ""))

        # Verify customer notification leak prevention: customer not in partner_ids
        self.assertNotIn(
            self.partner.id,
            fwd_dict.get("partner_ids") or [],
            "Customer partner must not be in partner_ids for forwarded emails",
        )

    def test_flexible_order_reference_matching(self):
        """Order matching supports prefix variations (SO vs S)."""
        order_so = self.env["sale.order"].create(
            {
                "name": "SO1234",
                "partner_id": self.partner.id,
            }
        )
        order_s = self.env["sale.order"].create(
            {
                "name": "S5678",
                "partner_id": self.partner.id,
            }
        )

        # Match S1234 in subject against SO1234 record
        msg_s, dict_s = self._create_email(
            subject="Kundenanfrage zu S1234",
            email_from="mitarbeiter@ebike-haus.de",
            msg_id="<fwd.flex1@example.de>",
        )
        routes_s = self.env["mail.thread"].message_route(msg_s, dict_s)
        self.assertTrue(routes_s)
        self.assertEqual(routes_s[0][0], "sale.order")
        self.assertEqual(routes_s[0][1], order_so.id)

        # Match SO5678 in subject against S5678 record
        msg_so, dict_so = self._create_email(
            subject="Kundenanfrage zu SO5678",
            email_from="mitarbeiter@ebike-haus.de",
            msg_id="<fwd.flex2@example.de>",
        )
        routes_so = self.env["mail.thread"].message_route(msg_so, dict_so)
        self.assertTrue(routes_so)
        self.assertEqual(routes_so[0][0], "sale.order")
        self.assertEqual(routes_so[0][1], order_s.id)

    def test_unassigned_mail_get_all_attachments(self):
        """Helper _get_all_attachments extracts attachments from record and chatter."""
        unassigned = self.env["ebh.unassigned.mail"].create(
            {
                "name": "Mail mit Anhang",
                "email_from": "kunde@example.de",
            }
        )
        att_record = self.env["ir.attachment"].create(
            {
                "name": "doc1.pdf",
                "res_model": unassigned._name,
                "res_id": unassigned.id,
                "raw": b"PDF content 1",
            }
        )
        msg = unassigned.message_post(body="Chatter message")
        att_chatter = self.env["ir.attachment"].create(
            {
                "name": "doc2.pdf",
                "res_model": msg._name,
                "res_id": msg.id,
                "raw": b"PDF content 2",
            }
        )
        msg.write({"attachment_ids": [(4, att_chatter.id)]})

        all_atts = unassigned._get_all_attachments()
        self.assertIn(att_record, all_atts)
        self.assertIn(att_chatter, all_atts)

    def test_unassigned_mail_suppresses_bounce(self):
        """Unmatched inbound email creates draft unassigned mail without bounce."""
        unmatched_msg, unmatched_dict = self._create_email(
            subject="Allgemeine Frage zu Werkstattterminen",
            email_from="neu.interessent@example.de",
            msg_id="<unmatched.1003@example.de>",
            body="Haben Sie nächste Woche einen Inspektionstermin frei?",
        )

        routes = self.env["mail.thread"].message_route(unmatched_msg, unmatched_dict)
        self.assertTrue(routes, "Expected fallback route to unassigned mail")
        target_model, target_id = routes[0][0], routes[0][1]
        self.assertEqual(target_model, "ebh.unassigned.mail")

        unassigned_mail = self.env["ebh.unassigned.mail"].browse(target_id)
        self.assertTrue(unassigned_mail.exists())
        self.assertEqual(unassigned_mail.state, "draft")
        self.assertEqual(unassigned_mail.name, "Allgemeine Frage zu Werkstattterminen")
        self.assertEqual(unassigned_mail.email_from, "neu.interessent@example.de")
        self.assertEqual(unassigned_mail.message_id, "<unmatched.1003@example.de>")

    def test_unassigned_mail_action_assign(self):
        """Draft unassigned mail can be assigned to target document chatter."""
        order = self.env["sale.order"].create(
            {
                "name": "SO9998",
                "partner_id": self.partner.id,
            }
        )
        unassigned = self.env["ebh.unassigned.mail"].create(
            {
                "name": "Dringende Nachfrage zur Lieferung",
                "email_from": "neu.kunde@example.de",
                "email_to": "kd@ebike-haus.de",
                "body_html": "<p>Wann wird mein E-Bike geliefert?</p>",
                "state": "draft",
            }
        )

        # Assign to sale.order
        unassigned.action_assign_to_record(order._name, order.id)
        self.assertEqual(unassigned.state, "assigned")
        self.assertEqual(unassigned.res_model, order._name)
        self.assertEqual(unassigned.res_id, order.id)

        # Verify message was posted to target record chatter
        posted_message = order.message_ids.filtered(
            lambda m: m.subject == "Dringende Nachfrage zur Lieferung"
        )
        self.assertTrue(posted_message, "Expected posted message on target order")
        self.assertIn("Weitergeleitet aus unzugeordneten E-Mails", posted_message.body)
        self.assertIn("Wann wird mein E-Bike geliefert?", posted_message.body)

        # Validation: attempting to assign without target record raises UserError
        unassigned_empty = self.env["ebh.unassigned.mail"].create(
            {
                "name": "Ungültige Zuordnung",
                "state": "draft",
            }
        )
        with self.assertRaises(UserError):
            unassigned_empty.action_assign_to_record()
