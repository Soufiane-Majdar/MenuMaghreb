#!/bin/bash

# Install dependencies
pip3.12 install -r requirements.txt

# Make migrations
python3.12 manage.py migrate 

# Create static files directory
mkdir -p staticfiles_build

# Collect static files
python3.12 manage.py collectstatic --noinput --clear

# Copy admin static files
cp -r /usr/local/lib/python3.12/site-packages/django/contrib/admin/static/admin staticfiles_build/static/

# Copy Jazzmin static files
cp -r /usr/local/lib/python3.12/site-packages/jazzmin/static/jazzmin staticfiles_build/static/

# Set permissions
chmod -R 755 staticfiles_build/
