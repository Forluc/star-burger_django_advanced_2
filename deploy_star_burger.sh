#!/bin/bash -e

git pull
pip install -r requirements.txt
npm ci --dev
python3 manage.py collectstatic --noinput
python3 manage.py migrate

echo -e "\033[32mSucceeded"
