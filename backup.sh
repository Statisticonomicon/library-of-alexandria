#!/usr/bin/env bash
# =====================================================================
#  Back up everything to ./backups/ :
#    * loa-<timestamp>.sql        full PostgreSQL dump (authoritative)
#    * library-<timestamp>.csv    + wishlist-<timestamp>.csv  (UTF-8)
#
#  Usage:   ./backup.sh
# =====================================================================
set -euo pipefail
cd "$(dirname "$0")"
DB_USER="${POSTGRES_USER:-loa}"; DB_NAME="${POSTGRES_DB:-loa}"
mkdir -p backups
TS="$(date +%Y%m%d-%H%M%S)"

# Write to a .part file and only publish it once the command succeeded AND the
# output is non-empty. A direct `> file` redirect creates the destination
# before the command runs, so a failure (e.g. the db container not running)
# leaves a 0-byte file behind that looks like a real backup.
dump_to() {
    # $1 = final path, rest = command to run
    local dest="$1"; shift
    local part="${dest%/*}/.${dest##*/}.part"
    if "$@" > "$part" && [ -s "$part" ]; then
        mv -- "$part" "$dest"
    else
        rm -f -- "$part"
        echo "ERROR: failed or empty -> $dest" >&2
        return 1
    fi
}

echo "==> Dumping PostgreSQL -> backups/loa-$TS.sql"
dump_to "backups/loa-$TS.sql" docker compose exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" --clean --if-exists

echo "==> Exporting CSV copies (UTF-8 with BOM)"
dump_to "backups/library-$TS.csv"  docker compose exec -T app python manage.py export-csv --stdout library
dump_to "backups/wishlist-$TS.csv" docker compose exec -T app python manage.py export-csv --stdout wishlist

echo
echo "Backup complete:"
ls -lh "backups/loa-$TS.sql" "backups/library-$TS.csv" "backups/wishlist-$TS.csv"
