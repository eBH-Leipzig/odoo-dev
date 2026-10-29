# Betrieb: Deployment, Backup, Restore

Server: Hostinger-VPS `72.61.188.248`. Auf dem Server wird nicht entwickelt;
Skripte liegen versioniert in `ops/` und kommen per Git dorthin.

## Aufbau auf dem VPS

| Umgebung | Checkout | Branch | Compose-Profil | Container | Datenbank |
|---|---|---|---|---|---|
| DEV | `/docker/odoo-dev` | `dev` | `dev` | `odoo-web-dev`, `odoo-db-dev` | `dev_db` |
| PROD | `/docker/odoo-prod` | `main` | `prod` | `odoo-web-prod`, `odoo-db-prod` | `prod_db` |

- Beide Checkouts nutzen dieselbe `docker-compose.yml`; jeder startet nur sein Profil.
  Ohne Profil startet `docker compose up` nichts.
- Die Volumes heißen fest `odoo-dev_odoo-*-<env>` (Altlast aus dem gemeinsamen Projekt),
  damit sie unabhängig vom Checkout-Ordner dieselben bleiben.
- Auf dem VPS laufen außerdem n8n, `api`, `pwa`, Weaviate, eine weitere Postgres
  und Traefik. Nicht anfassen.

## Deployment

Push auf `dev` bzw. `main` → GitHub Actions (`.github/workflows/deploy.yml`):

1. **Tests:** alle Module aus `custom_addons/` in einer frischen Datenbank installieren und
   testen. Rot = kein Deploy.
2. **Deploy:** im Checkout der Umgebung `git reset --hard` auf den Branch, dann
   `bash ops/deploy.sh dev|prod`:
   Image bauen → Datenbank starten → *(nur PROD)* Sicherung `vor-deploy` → Odoo stoppen →
   `-u` aller eigenen Module (nur installierte werden aktualisiert) → Odoo starten.
   Eine leere Datenbank wird einmalig mit `-i base` angelegt.

Neue Module werden nicht automatisch installiert, sondern in Odoo unter Apps.
Das Odoo-Basis-Image wird beim Deploy nicht neu gezogen; Odoo-Updates sind ein eigener Schritt.

Schlägt `-u` fehl, bleibt Odoo gestoppt. Dann Log in GitHub Actions lesen, Fehler beheben
und neu pushen, oder die Sicherung `vor-deploy` zurückspielen.

## Backup

`bash ops/backup.sh dev|prod [kennung]` schreibt nach `/docker/backups/<env>/`:

- `<zeit>-<kennung>.dump`: Datenbank (`pg_dump -Fc`)
- `<zeit>-<kennung>-filestore.tar.gz`: Dateiablage (Anhänge, Bilder)

Älter als 7 Tage wird gelöscht (`KEEP_DAYS`). Der Ordner liegt im täglichen
Hostinger-Backup des ganzen VPS. Der nächtliche Cronjob folgt mit dem Betriebspaket.

## Restore (in eine Test-Datenbank)

```bash
# Datenbank in neue DB "prod_db_restore" einspielen
docker exec -i odoo-db-prod sh -c 'createdb -U "$POSTGRES_USER" prod_db_restore && pg_restore -U "$POSTGRES_USER" -d prod_db_restore --no-owner' < /docker/backups/prod/<zeit>-<kennung>.dump

# Dateiablage dazu (Ordnername = Datenbankname)
docker run --rm -i -v odoo-dev_odoo-web-data-prod:/data alpine:3.20 sh -c 'mkdir -p /tmp/x && tar xzf - -C /tmp/x && mv /tmp/x/filestore/prod_db /data/filestore/prod_db_restore' < /docker/backups/prod/<zeit>-<kennung>-filestore.tar.gz
```

Danach kann Odoo die Datenbank `prod_db_restore` öffnen. Wird eine PROD-Kopie in DEV
genutzt, vorher `odoo neutralize -d <db>` ausführen (schaltet Mailserver, Cronjobs und
Schnittstellen ab).

## Umstellung auf getrennte Checkouts (einmalig, Oktober 2026)

Bis 29.10.2026 liefen DEV und PROD aus einem Checkout `/docker/odoo-dev`; PROD band damit
den DEV-Code ein. Umstellung siehe Änderungsprotokoll.
