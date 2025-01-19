#!/bin/bash

# Wait for the database to be ready (assuming 'db' is the name of your database service)
# Modify the DB hostname (e.g., 'db') and port (5432 for PostgreSQL) as necessary.
echo "Waiting for PostgreSQL to be ready..."
wait-for-it db:5432 --timeout=30 --strict -- echo "Database is ready"

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Start the Django development server (or use Gunicorn in production)
exec python manage.py runserver 0.0.0.0:8000
