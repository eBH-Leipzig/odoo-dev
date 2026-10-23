# 0001 Email Routing and Catchall Architecture

Configure a robust, production-ready inbound and outbound email architecture for E-Bike-Haus using a dedicated custom addon, Mailpit for safe local testing, environment-driven configuration, and an unassigned mail review queue that suppresses automated bounce messages.

## Status

Accepted

## Context

Email integration is a mandatory milestone prior to production go-live ("E-Mail-Anbindung Pflicht vor Go-live"). E-Bike-Haus requires reliable email processing for customer inquiries, sales quotes, repairs, and invoice communications.

Several risks and architectural requirements were identified:
1. **Safety in non-production environments**: Developers and automated tests running against staging or sanitized production databases risk accidentally dispatching emails to real customers or suppliers if outbound SMTP is connected.
2. **Modular codebase**: Mail routing logic, server parameter initialization, and custom mail queues must remain decoupled from core ERP customization (`ebh_base`).
3. **Inbound routing and chatter linking**: Replies to system-generated notifications must link automatically to their originating document chatter, while new incoming inquiries to generic addresses need orderly ingestion via a single mailbox.
4. **Environment isolation**: Credentials and host configurations for incoming and outgoing mail servers must adhere to 12-factor principles and never be committed to source control.
5. **Customer experience for unmatched incoming emails**: Default Odoo behavior can trigger automated non-delivery reports (NDRs) / bounce messages when an email arrives at a catchall address without matching an active record or registered alias. For customer inquiries sent to generic or slightly mistyped addresses, an immediate NDR creates a poor customer experience and risks losing business inquiries.

## Decision

We decided to implement the email architecture based on the following five decisions:

1. **Local Development & Testing Safety with Mailpit**:
   Integrate Mailpit into [`docker-compose.yml`](../../docker-compose.yml) as the default SMTP and web-inspection service for local development and test environments. All outgoing emails in development are routed to Mailpit (port 1025) and inspectable via the web interface (port 8025), preventing any external email transmission.

2. **Dedicated Addon (`custom_addons/ebh_mail`)**:
   Establish a dedicated module [`custom_addons/ebh_mail`](../../custom_addons/) to house all email configuration data, model extensions, and mail routing handlers, keeping `ebh_base` clean and focused on general company definitions.

3. **Alias Domain & Catchall Routing**:
   Configure `ebike-haus.de` as the alias domain. Set the catchall alias to `kd` (`kd@ebike-haus.de`) and the bounce alias to `bounce` (`bounce@ebike-haus.de`). Inbound emails will be retrieved by fetchmail polling a single dedicated mailbox. Standard Odoo reply-to message ID routing handles linking replies to their target document chatter.

4. **Environment-Driven Configuration**:
   Manage all incoming (POP3/IMAP) and outgoing (SMTP) mail server hostnames, ports, security settings, and credentials using environment variables defined in [`.env.example`](../../.env.example) and loaded via [`.env`](../../.env).

5. **Unassigned Mails & Suppression of Automated NDRs**:
   Intercept inbound emails received on the catchall or domain aliases that cannot be matched to an existing document or specific alias, routing them to a dedicated "Unzugeordnete Mails" (`ebh.mail.unassigned`) model for manual staff triage or future automated AI categorization. Suppress automatic NDR/bounce message generation for these unmatched emails.

## Consequences

### Positive

- **Safety**: Developers and QA can test all business flows (quotes, invoices, order confirmations) without risk of sending emails to real customers or third parties.
- **Maintainability**: Email routing customizations are cleanly isolated in `ebh_mail`, facilitating independent upgrades and testing.
- **Customer Experience**: External customers who email generic addresses or make minor recipient errors receive no confusing bounce notifications; their messages are retained for staff review.
- **Configuration Security**: Credentials and server addresses are decoupled from codebase manifests and XML records, enabling seamless promotion across dev, staging, and production.
- **Auditability**: Unassigned emails are centralized in a visible Odoo view, preventing dropped communications.

### Trade-offs & Operational Requirements

- **Queue Monitoring**: Staff or triage agents must monitor the "Unzugeordnete Mails" queue to reassign or resolve unmatched inquiries.
- **DNS / Mailbox Prerequisites**: Production deployment requires corresponding MX, SPF, DKIM, DMARC, and mailbox configurations on the external mail provider for `ebike-haus.de`.
- **Compose Stack Footprint**: Running Mailpit adds a lightweight container service to the local Docker Compose environment.
