#!/bin/sh
python3.11 -m venv "${VENV_PATH}"
. venv/bin/activate
python3.11 -m pip install --no-cache-dir --upgrade pip wheel
python3.11 -m pip install --no-cache-dir -r requirements-cicd.txt
python3.11 -m pip install --no-cache-dir -r app/requirements.txt
# Apply Testing environment variables from .env.unittests file
set -a && . ./.env.unittests && set +a
cd app/
python3.11 manage.py test