#!/bin/sh
set -e

# ── Attente de PostgreSQL ──────────────────────────────────────
# Quand Docker Desktop redémarre, tous les conteneurs sont relancés
# SIMULTANÉMENT (la condition depends_on:service_healthy n'est honorée
# que par `docker compose up`, pas par le redémarrage du démon). Sans
# cette boucle, le backend pourrait démarrer avant que la base accepte
# les connexions et tomber en crash-loop. On attend donc activement.
echo ">>> Waiting for PostgreSQL ($POSTGRES_HOST:5432)..."
until python -c "import psycopg2, os; psycopg2.connect(dbname=os.environ['POSTGRES_DB'], user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'], host=os.environ.get('POSTGRES_HOST', 'db'), port=5432).close()" 2>/dev/null; do
    echo "    PostgreSQL indisponible — nouvelle tentative dans 2s..."
    sleep 2
done
echo ">>> PostgreSQL prêt."

echo ">>> Applying database migrations..."
python manage.py migrate --noinput

echo ">>> Seeding default users (admin, medecin, secretaire)..."
python seed_users.py

echo ">>> Starting server..."
exec "$@"
