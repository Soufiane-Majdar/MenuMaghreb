#!/bin/bash

# Install dependencies
pip3.12 install -r requirements.txt

# Make migrations
python3.12 manage.py migrate 

# Create static files directory
# mkdir -p staticfiles

# Collect static files
# python3.12 manage.py collectstatic --noinput 

# # Copy admin static files
# cp -r /usr/local/lib/python3.12/site-packages/django/contrib/admin/static/admin staticfiles/static/

# # Copy Jazzmin static files
# cp -r /usr/local/lib/python3.12/site-packages/jazzmin/static/jazzmin staticfiles/static/

# Set permissions
# chmod -R 755 staticfiles/
# Command to create superuser
echo "Creating superuser..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = "soufiane"
email = "soufiane.majdar@gmail.com"
password = "s_mjr3145@dev"
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created: Username=\\'\$username\\', Email=\\'\$email\\'")
else:
    print("Superuser already exists: Email=\\'\$email\\'")
EOF