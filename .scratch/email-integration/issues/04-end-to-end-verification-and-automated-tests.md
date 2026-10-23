# 04: End-to-end verification and automated tests

**What to build:** Automated Odoo test suite in `custom_addons/ebh_mail/tests/` covering environment synchronization, outbound mail routing, chatter reply ingestion, and unassigned mail capture.

**Blocked by:** 03: Unassigned mails model and bounce suppression

**Status:** done

- [x] Test passes verifying mail server and alias domain initialization.
- [x] Test passes verifying simulated inbound email linked to chatter.
- [x] Test passes verifying unmatched inbound email staging into `ebh.unassigned.mail` without bounce.
