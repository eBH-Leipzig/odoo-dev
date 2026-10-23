# 01: Module scaffold and environment mail server hook

**What to build:** Module scaffold `custom_addons/ebh_mail/` and post_init_hook reading environment variables to synchronize alias domain (`ebike-haus.de`), catchall (`kd`), bounce (`bounce`), outgoing mail server (`ir.mail_server`), and incoming mail server (`fetchmail.server`).

**Blocked by:** None (can start immediately)

**Status:** done

- [x] `custom_addons/ebh_mail/__manifest__.py` is defined with dependencies on `['base', 'mail', 'ebh_base']`.
- [x] `hooks.py` configures `mail.alias.domain` / config parameters and server records based on environment variables.
- [x] Passes flake8 linter.
