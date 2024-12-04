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
chmod -R 755 staticfiles/
