#!/bin/sh

echo "Starting Service"
if [[ ! -e logs/ebay-alerts.log ]]; then
    mkdir -p logs
    touch logs/ebay-alerts.log
    chmod +x logs/ebay-alerts.log
fi
if [[ ! -e logs/gunicorn-access.logs ]]; then
    touch logs/gunicorn-access.logs
    chmod +x logs/gunicorn-access.logs
fi
if [[ ! -e logs/gunicorn-errors.logs ]]; then
    touch logs/gunicorn-errors.logs
    chmod +x logs/gunicorn-errors.logs
fi
cd /ebay-alerts/src
python -u manage.py makemigrations
python -u manage.py migrate
python -u manage.py test tests/
#python  manage.py collectstatic --noinput

python -u /ebay-alerts/src/manage.py runserver 0.0.0.0:80


#In production
#gunicorn --workers=${WORKERS} -b 0.0.0.0:${APP_PORT} --access-logfile /ebay-alerts/logs/gunicorn-access.logs --error-logfile /ebay-alerts/logs/gunicorn-errors.logs core.wsgi

