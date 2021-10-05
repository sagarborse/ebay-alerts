#!/bin/bash
echo "Starting Celery Shore"
if [[ ! -e logs/shore.log ]]; then
    mkdir -p logs
    touch logs/shore.log
    chmod +x logs/shore.log
fi

cd src
celery -A core worker -l info -Q ${NOTIFICATION_QUEUE} --concurrency=${CELERY_CONCURRENCY}