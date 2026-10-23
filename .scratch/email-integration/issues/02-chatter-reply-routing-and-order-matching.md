# 02: Chatter reply routing and order subject matching

**What to build:** Ensure standard chatter replies to `kd@ebike-haus.de` via `In-Reply-To` / `References` route to the origin record chatter, and add matching logic in `mail.thread` for forwarded staff emails with order numbers (e.g. `S00123`) in the subject to attach directly to that sale order's chatter.

**Blocked by:** 01: Module scaffold and environment mail server hook

**Status:** completed

- [x] Replies with matching message-id headers attach to document chatter.
- [x] Emails with order number patterns in the subject route to the matching `sale.order`.
