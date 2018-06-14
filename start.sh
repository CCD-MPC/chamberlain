#!/bin/bash

cd /app/conclave-web
source backend/venv/bin/activate
gunicorn wsgi:app