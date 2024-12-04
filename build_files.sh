#!/bin/bash
pip3.12 install -r requirements.txt

# make migrations
python3.12 manage.py migrate 
python3.12 manage.py collectstatic --noinput
