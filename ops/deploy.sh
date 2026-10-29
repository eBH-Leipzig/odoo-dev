#!/usr/bin/env bash
# Deploy einer Umgebung auf dem VPS. Läuft im Checkout der Umgebung,
# nachdem GitHub Actions den Branch dort ausgecheckt hat:
#
#   /docker/odoo-dev   (Branch dev)  -> bash ops/deploy.sh dev
#   /docker/odoo-prod  (Branch main) -> bash ops/deploy.sh prod
#
# Ablauf: Image bauen, Datenbank starten, bei PROD vorher sichern,
# Odoo stoppen, eigene Module aktualisieren (-u), Odoo wieder starten.
# Eine leere Datenbank wird einmalig mit -i base angelegt.
set -euo pipefail

ENV="${1:-}"
case "$ENV" in
    dev) DB=dev_db ;;
    prod) DB=prod_db ;;
    *)
        echo "Aufruf: $0 dev|prod" >&2
        exit 2
        ;;
esac

cd "$(dirname "$0")/.."

WEB="odoo-$ENV"
DB_SERVICE="odoo-db-$ENV"
ADDONS_PATH=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons

compose() {
    docker compose --profile "$ENV" "$@"
}

# Alle eigenen Module; -u wirkt nur auf installierte, der Rest wird ignoriert
MODULES="$(find custom_addons -mindepth 2 -maxdepth 2 -name __manifest__.py \
    -exec dirname {} \; | xargs -n1 basename | sort | paste -sd, -)"

echo "== Image bauen ($WEB)"
compose build "$WEB"

echo "== Datenbank starten ($DB_SERVICE)"
compose up -d "$DB_SERVICE"
for _ in $(seq 1 30); do
    if compose exec -T "$DB_SERVICE" sh -c 'pg_isready -q -U "$POSTGRES_USER"'; then
        break
    fi
    sleep 2
done

INITIALIZED="$(compose exec -T "$DB_SERVICE" sh -c \
    "psql -U \"\$POSTGRES_USER\" -d $DB -tAc \
    \"select 1 from pg_tables where tablename = 'ir_module_module'\"" \
    2>/dev/null || true)"

if [ "$ENV" = prod ] && [ "$INITIALIZED" = 1 ]; then
    echo "== Sicherung vor dem Deploy"
    bash ops/backup.sh prod vor-deploy
fi

echo "== Odoo stoppen ($WEB)"
compose stop "$WEB"

odoo_once() {
    # Eigener Container ohne HTTP; von Traefik ausgenommen
    compose run --rm --no-deps --label traefik.enable=false "$WEB" \
        odoo --addons-path="$ADDONS_PATH" -d "$DB" --no-http --stop-after-init "$@"
}

if [ "$INITIALIZED" = 1 ]; then
    echo "== Module aktualisieren: $MODULES"
    odoo_once -u "$MODULES"
else
    echo "== Leere Datenbank $DB: Grundinstallation (-i base)"
    odoo_once -i base
fi

echo "== Odoo starten ($WEB)"
# Ohne --remove-orphans: Im alten gemeinsamen Projekt "odoo-dev" liefen auch
# die PROD-Container, die dürfen hier nicht mit abgeräumt werden.
compose up -d "$WEB"
echo "Deploy $ENV fertig."
