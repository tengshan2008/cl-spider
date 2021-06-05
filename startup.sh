#!/bin/bash
source /opt/venv/bin/activate
gunicorn --access-logfile - --error-logfile - wsgi:application -c gunicorn.conf.py