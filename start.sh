#!/bin/bash

cd /app/conclave-web
source backend/venv/bin/activate
export LC_ALL=en_US.utf8
gunicorn wsgi:app