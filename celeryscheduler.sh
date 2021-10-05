#!/bin/bash
echo "Starting Celery Scheduler for Shore"
if [[ ! -e logs/shore.log ]]; then
    mkdir -p logs
    touch logs/shore.log
    chmod +x logs/shore.log
fi
cd src
celery -A core beat -l info