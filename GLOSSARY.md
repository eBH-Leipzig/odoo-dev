# Email Integration

The domain of inbound and outbound electronic mail communication for customer correspondence, automated notifications, and document-level conversations.

## Language

**Alias Domain**:
The configured primary domain name used for receiving and routing incoming messages into business records.
_Avoid_: Mail domain, virtual domain, server domain

**Catchall Alias**:
A designated generic address local-part configured to receive incoming messages when no specific record or mailbox alias matches the recipient address.
_Avoid_: Default inbox, wildcard mailbox, generic inbox

**Bounce Alias**:
A dedicated local-part address configured to receive automated delivery failure notifications and non-delivery reports.
_Avoid_: Return-path address, error mailbox, mailer-daemon

**Unassigned Mail (`Unzugeordnete Mails`)**:
An incoming email that cannot be matched to an existing document thread or registered alias, retained for human or automated evaluation without dispatching an automatic rejection notice.
_Avoid_: Orphaned email, dropped email, rejected message, dead letter

**Mailpit**:
A local development and testing mock SMTP server and web interface that intercepts outbound emails to guarantee that no test messages reach real recipients.
_Avoid_: Fake SMTP, mail sink, email trap

**Chatter Reply Routing**:
The protocol for matching incoming email replies to their originating business document thread via standardized message identification headers.
_Avoid_: Thread syncing, message linking, conversation pairing
