#!/bin/sh
set -e

echo ">>> Applying database migrations..."
python manage.py migrate --noinput

echo ">>> Seeding default users (admin, medecin, secretaire)..."
python seed_users.py

echo ">>> Starting server..."
exec "$@"
