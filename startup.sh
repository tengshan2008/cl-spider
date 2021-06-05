#!/bin/bash
source /opt/venv/bin/activate
gunicorn --access-logfile - --error-logfile - server:app -c gunicorn.conf.py