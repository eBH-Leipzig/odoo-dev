# Copyright 2026 eBike-Haus.de GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import html
import logging
import re

from odoo import api, models

_logger = logging.getLogger(__name__)

ORDER_REF_PATTERN = re.compile(
    r"\b(SO\d{4,6}|S\d{4,6}|PO\d{4,6}|P\d{4,6})\b",
    re.IGNORECASE,
)
FORWARDED_FROM_HEADER_NAMES = (
    "X-Forwarded-From",
    "X-Original-From",
    "X-Original-Sender",
    "Resent-From",
)
FORWARDED_BODY_PATTERN = re.compile(
    r"(?:Von|From):\s*([^\r\n<]+(?:<[^>]+>)?)",
    re.IGNORECASE,
)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _routing_create_bounce_email(
        self, email_from, body_html, message, **mail_values
    ):
        """Suppress automatic bounce/NDR generation per ADR 0001.

        Unmatched emails should not produce confusing bounce notices
        for customers or forwarded staff messages.
        """
        if self.env.context.get("ebh_suppress_bounce", True):
            msg_id = message.get("Message-Id") if message else "unknown"
            _logger.info(
                "Suppressed automatic bounce email to %s for Message-Id %s",
                email_from,
                msg_id,
            )
            return False
        return super()._routing_create_bounce_email(
            email_from, body_html, message, **mail_values
        )

    @api.model
    def message_route(
        self,
        message,
        message_dict,
        model=None,
        thread_id=None,
        custom_values=None,
    ):
        """Route incoming email to document chatter.

        First attempts standard Odoo route extraction (Message-Id,
        In-Reply-To, References, Aliases). If no route is found, inspects
        email subject for order references (e.g. S00123, SO00123, P00123,
        PO00123) and routes to the corresponding sale or purchase order.
        """
        route_exception = None
        try:
            routes = super().message_route(
                message,
                message_dict,
                model=model,
                thread_id=thread_id,
                custom_values=custom_values,
            )
        except ValueError as exc:
            routes = []
            route_exception = exc

        if not routes:
            matched_route = self._find_route_from_subject(
                message,
                message_dict,
                custom_values=custom_values,
            )
            if matched_route:
                routes = [matched_route]
            else:
                unassigned_route = self._route_to_unassigned_mail(
                    message,
                    message_dict,
                    custom_values=custom_values,
                )
                if unassigned_route:
                    routes = [unassigned_route]
                elif route_exception:
                    raise route_exception

        return routes

    @api.model
    def _route_to_unassigned_mail(self, message, message_dict, custom_values=None):
        """Route unassigned incoming email to ebh.unassigned.mail staging."""
        if "ebh.unassigned.mail" not in self.env:
            return False

        email_from = message_dict.get("email_from") or ""
        user = self._mail_find_user_for_gateway(email_from)
        user_id = user.id or self.env.uid

        unassigned_vals = {
            "name": message_dict.get("subject") or "/",
            "email_from": email_from,
            "email_to": message_dict.get("to") or "",
            "body_html": message_dict.get("body") or "",
            "message_id": message_dict.get("message_id") or "",
            "state": "draft",
        }
        if message_dict.get("date"):
            unassigned_vals["date"] = message_dict["date"]

        try:
            unassigned_record = (
                self.env["ebh.unassigned.mail"].sudo().create(unassigned_vals)
            )
        except Exception:
            unassigned_vals.pop("date", None)
            unassigned_record = (
                self.env["ebh.unassigned.mail"].sudo().create(unassigned_vals)
            )

        _logger.info(
            "Created unassigned mail record %s (ID %s) for message %s",
            unassigned_record.name,
            unassigned_record.id,
            unassigned_record.message_id,
        )

        return (
            unassigned_record._name,
            unassigned_record.id,
            custom_values,
            user_id,
            None,
        )

    @api.model
    def _find_route_from_subject(self, message, message_dict, custom_values=None):
        """Extract order reference from subject and build matching route."""
        subject = message_dict.get("subject") or ""
        match = ORDER_REF_PATTERN.search(subject)
        if not match:
            return False

        matched_ref = match.group(1).strip()
        ref_upper = matched_ref.upper()
        target_record = None

        if ref_upper.startswith(("SO", "S")) and "sale.order" in self.env:
            if ref_upper.startswith("SO"):
                candidates = [matched_ref, matched_ref[0] + matched_ref[2:]]
            else:
                candidates = [
                    matched_ref,
                    matched_ref[0] + "O" + matched_ref[1:],
                ]
            target_record = (
                self.env["sale.order"]
                .sudo()
                .search(
                    [
                        "|",
                        ("name", "=ilike", candidates[0]),
                        ("name", "=ilike", candidates[1]),
                    ],
                    limit=1,
                )
            )
        elif ref_upper.startswith(("PO", "P")) and "purchase.order" in self.env:
            if ref_upper.startswith("PO"):
                candidates = [matched_ref, matched_ref[0] + matched_ref[2:]]
            else:
                candidates = [
                    matched_ref,
                    matched_ref[0] + "O" + matched_ref[1:],
                ]
            target_record = (
                self.env["purchase.order"]
                .sudo()
                .search(
                    [
                        "|",
                        ("name", "=ilike", candidates[0]),
                        ("name", "=ilike", candidates[1]),
                    ],
                    limit=1,
                )
            )

        if not target_record:
            return False

        email_from = message_dict.get("email_from") or ""
        user = self._mail_find_user_for_gateway(email_from)
        user_id = user.id or self.env.uid

        self._enrich_forwarded_metadata(message, message_dict)

        route = (
            target_record._name,
            target_record.id,
            custom_values,
            user_id,
            None,
        )
        checked_route = self._routing_check_route(
            message, message_dict, route, raise_exception=False
        )
        return checked_route or route

    @api.model
    def _enrich_forwarded_metadata(self, message, message_dict):
        """Preserve and highlight forwarded email metadata in chatter body."""
        orig_sender = None
        for header in FORWARDED_FROM_HEADER_NAMES:
            if message and message.get(header):
                orig_sender = message.get(header).strip()
                break

        if not orig_sender and message_dict.get("body"):
            body_match = FORWARDED_BODY_PATTERN.search(message_dict["body"])
            if body_match:
                orig_sender = body_match.group(1).strip()

        if orig_sender:
            clean_sender = html.escape(orig_sender)
            note_banner = (
                '<div class="ebh_forwarded_metadata" '
                'style="background-color: #f8f9fa; '
                "border-left: 4px solid #00A09D; "
                'padding: 8px 12px; margin-bottom: 10px; font-size: 13px;">'
                f"<strong>Ursprünglicher Absender:</strong> {clean_sender}"
                "</div>"
            )
            existing_body = message_dict.get("body") or ""
            message_dict["body"] = f"{note_banner}{existing_body}"

            # Note matching partner as author if not already set; never add to
            # partner_ids to prevent automated outbound notification email leak.
            email_match = re.search(r"[\w\.-]+@[\w\.-]+", orig_sender)
            if email_match and "res.partner" in self.env:
                orig_email = email_match.group(0)
                partner = (
                    self.env["res.partner"]
                    .sudo()
                    .search([("email", "=ilike", orig_email)], limit=1)
                )
                if partner and not message_dict.get("author_id"):
                    message_dict["author_id"] = partner.id
