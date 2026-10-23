# Copyright 2026 eBike-Haus.de GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import html

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EbhUnassignedMail(models.Model):
    _name = "ebh.unassigned.mail"
    _description = "Unassigned Inbound Email"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Subject", required=True, default="/")
    email_from = fields.Char(string="From")
    email_to = fields.Char(string="To")
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    body_html = fields.Html(string="Body HTML")
    message_id = fields.Char(string="Message ID")
    state = fields.Selection(
        [
            ("draft", "Draft / Unassigned"),
            ("assigned", "Assigned"),
            ("forwarded", "Forwarded"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )
    res_model = fields.Char(string="Target Model")
    res_id = fields.Integer(string="Target Record ID")
    target_reference = fields.Reference(
        selection="_selection_target_model",
        compute="_compute_target_reference",
        inverse="_inverse_target_reference",
        string="Linked Document",
    )

    @api.model
    def _selection_target_model(self):
        default_models = [
            ("sale.order", "Sales Order"),
            ("purchase.order", "Purchase Order"),
            ("res.partner", "Contact"),
            ("account.move", "Invoice / Entry"),
        ]
        if "ir.model" in self.env:
            ir_models = (
                self.env["ir.model"]
                .sudo()
                .search([("model", "in", [m[0] for m in default_models])])
            )
            if ir_models:
                return [(m.model, m.name) for m in ir_models]
        return default_models

    @api.depends("res_model", "res_id")
    def _compute_target_reference(self):
        for record in self:
            if record.res_model and record.res_id and record.res_model in self.env:
                record.target_reference = f"{record.res_model},{record.res_id}"
            else:
                record.target_reference = False

    def _inverse_target_reference(self):
        for record in self:
            if record.target_reference:
                record.res_model = record.target_reference._name
                record.res_id = record.target_reference.id
            else:
                record.res_model = False
                record.res_id = False

    def _get_all_attachments(self):
        """Return all attachments linked directly to this record or chatter."""
        self.ensure_one()
        record_attachments = self.env["ir.attachment"].search(
            [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
            ]
        )
        msg_attachments = self.message_ids.mapped("attachment_ids")
        return record_attachments | msg_attachments

    def action_assign_to_record(self, res_model=None, res_id=None):
        """Assign unassigned mail to target record chatter with attachments."""
        for record in self:
            target_model = res_model or record.res_model
            target_id = res_id or record.res_id

            if not target_model or not target_id:
                raise UserError(_("Please specify a target document before assigning."))
            if target_model not in self.env:
                raise UserError(_("Target model '%s' does not exist.") % target_model)
            target = self.env[target_model].browse(target_id)
            if not target.exists():
                raise UserError(
                    _("Target record #%s in '%s' does not exist.")
                    % (target_id, target_model)
                )

            all_attachments = record._get_all_attachments()

            copied_attachment_ids = []
            for att in all_attachments:
                copied = att.copy(
                    {
                        "res_model": target_model,
                        "res_id": target.id,
                    }
                )
                copied_attachment_ids.append(copied.id)

            body_content = record.body_html or ""
            header_lines = [
                "<p><strong>Weitergeleitet aus unzugeordneten " "E-Mails:</strong></p>",
                "<ul>",
                f"<li><strong>Von:</strong> "
                f"{html.escape(record.email_from or '')}</li>",
                f"<li><strong>An:</strong> "
                f"{html.escape(record.email_to or '')}</li>",
                f"<li><strong>Datum:</strong> {record.date or ''}</li>",
                f"<li><strong>Betreff:</strong> "
                f"{html.escape(record.name or '')}</li>",
                "</ul><hr/>",
            ]
            full_body = "".join(header_lines) + body_content

            if hasattr(target, "message_post"):
                target.message_post(
                    body=full_body,
                    subject=record.name,
                    email_from=record.email_from,
                    message_type="email",
                    subtype_xmlid="mail.mt_comment",
                    attachment_ids=copied_attachment_ids,
                )

            record.write(
                {
                    "state": "assigned",
                    "res_model": target_model,
                    "res_id": target_id,
                }
            )
            record.message_post(
                body=_("Email assigned to %s (ID: %s)") % (target_model, target_id)
            )
        return True

    def action_forward_to_company(self):
        """Send email to company inbox with [Nicht zugeordnet] prefix."""
        for record in self:
            company_email = record.env.company.email or "leipzig@ebike-haus.de"
            subject = f"[Nicht zugeordnet] {record.name or '/'}"

            attachments = record._get_all_attachments()

            body_content = record.body_html or ""
            forward_header = (
                "<p><strong>Weitergeleitete unzugeordnete E-Mail:</strong></p>"
                "<ul>"
                f"<li><strong>Ursprünglicher Absender:</strong> "
                f"{html.escape(record.email_from or '')}</li>"
                f"<li><strong>Empfänger:</strong> "
                f"{html.escape(record.email_to or '')}</li>"
                f"<li><strong>Datum:</strong> {record.date or ''}</li>"
                f"<li><strong>Betreff:</strong> "
                f"{html.escape(record.name or '')}</li>"
                "</ul><hr/>"
            )
            full_body = f"{forward_header}{body_content}"

            mail_values = {
                "subject": subject,
                "email_to": company_email,
                "email_from": company_email,
                "reply_to": record.email_from or company_email,
                "body_html": full_body,
                "model": record._name,
                "res_id": record.id,
            }
            if attachments:
                mail_values["attachment_ids"] = [(6, 0, attachments.ids)]

            mail = self.env["mail.mail"].sudo().create(mail_values)
            mail.send()

            record.write({"state": "forwarded"})
            record.message_post(body=_("Email forwarded to %s.") % company_email)
        return True

    def action_set_draft(self):
        """Reset state back to draft."""
        self.write({"state": "draft"})
        return True
