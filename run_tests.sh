#!/bin/bash
echo "Running run_tests.sh"
cd src
echo "Will run python tests"
python manage.py test tests/
