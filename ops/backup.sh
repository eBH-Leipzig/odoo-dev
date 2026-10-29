#!/usr/bin/env bash
# Sichert Datenbank (pg_dump) und Dateiablage (filestore) einer Umgebung.
#
#   bash ops/backup.sh dev|prod [kennung]
#
# Ablage: $BACKUP_DIR/<env>/<zeit>-<kennung>.dump und ...-filestore.tar.gz
# (Standard /docker/backups, liegt damit auch im täglichen Hostinger-Backup).
# Sicherungen älter als $KEEP_DAYS Tage (Standard 7) werden gelöscht.
#
# Zurückspielen: siehe docs/BETRIEB.md.
set -euo pipefail

ENV="${1:-}"
TAG="${2:-manuell}"
case "$ENV" in
    dev) DB=dev_db ;;
    prod) DB=prod_db ;;
    *)
        echo "Aufruf: $0 dev|prod [kennung]" >&2
        exit 2
        ;;
esac

BACKUP_DIR="${BACKUP_DIR:-/docker/backups}"
KEEP_DAYS="${KEEP_DAYS:-7}"
DB_CONTAINER="odoo-db-$ENV"
WEB_VOLUME="odoo-dev_odoo-web-data-$ENV"
TARGET="$BACKUP_DIR/$ENV"
STAMP="$(date +%Y%m%d-%H%M%S)-$TAG"

umask 077
mkdir -p "$TARGET"

# Datenbank: erst in eine .part-Datei, damit nie ein halber Dump liegen bleibt
docker exec "$DB_CONTAINER" sh -c "pg_dump -U \"\$POSTGRES_USER\" -Fc $DB" \
    >"$TARGET/$STAMP.dump.part"
mv "$TARGET/$STAMP.dump.part" "$TARGET/$STAMP.dump"

# Dateiablage direkt aus dem Volume, damit es auch bei gestopptem Odoo geht
docker run --rm -v "$WEB_VOLUME:/data:ro" alpine:3.20 sh -c \
    "if [ -d /data/filestore/$DB ]; then tar czf - -C /data filestore/$DB; fi" \
    >"$TARGET/$STAMP-filestore.tar.gz.part"
mv "$TARGET/$STAMP-filestore.tar.gz.part" "$TARGET/$STAMP-filestore.tar.gz"

find "$TARGET" -maxdepth 1 -type f \( -name '*.dump' -o -name '*.tar.gz' \) \
    -mtime +"$KEEP_DAYS" -delete

echo "Backup $ENV: $TARGET/$STAMP.dump ($(du -h "$TARGET/$STAMP.dump" | cut -f1))"
