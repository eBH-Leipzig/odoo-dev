# 03: Unassigned mails model and bounce suppression

**What to build:** Create `ebh.unassigned.mail` model and views for staging incoming emails that have no matching record or alias. Suppress automatic NDR bounces in `mail.thread` so external senders never receive automated rejection notices.

**Blocked by:** 02: Chatter reply routing and order subject matching

**Status:** completed

- [x] Unrouted incoming messages do not raise bounce errors or send NDR emails.
- [x] Unrouted incoming messages are stored in `ebh.unassigned.mail` with fields for sender, recipient, subject, body, and state (`draft`, `assigned`, `forwarded`).
- [x] Actions exist to assign an unassigned mail to any record chatter or forward to `leipzig@ebike-haus.de`.
- [x] Security access rules defined in `ir.model.access.csv`.
