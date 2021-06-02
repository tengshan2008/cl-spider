#!/bin/sh
source /opt/venv/bin/activate
gunicorn wsgi:application -c gunicorn.conf.py