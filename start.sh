#!/bin/bash

# Wait for DB to be ready (simple sleep for now, could use wait-for-it)
echo "Waiting for database..."
sleep 5

echo "Applying migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Creating superuser if not exists..."
# Simple script to create superuser if needed, or user can do it manually.
# For now, just print a message
echo "Ready to start server."

exec "$@"
