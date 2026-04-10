#!/usr/bin/env bash
set -o errexit

echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Running migrations ==="
python manage.py migrate --noinput

echo "=== Creating superuser if not exists ==="
python manage.py shell -c '
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@finddoc.com", "admin123")
    print("✅ Superuser created: username = admin, password = admin123")
else:
    print("✅ Superuser already exists (username = admin)")
'

echo "=== Build completed successfully ==="