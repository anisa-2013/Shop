#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput

python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if username and password:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email or ""}
    )
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    if email:
        user.email = email
    user.set_password(password)
    user.save()
    print("Superuser configured successfully.")
else:
    print("Superuser environment variables not set; skipping.")
PY