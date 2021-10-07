# Ebay-Alerts
Sytem which provided alerts for price drop of a product on ebay with other metrics

##Technologies
Django, Django DRF, Swagger, Postgres, Redis, Celery, Docker

##Setup
1.Rename env.txt file to .env file and add appropriate values of all the envioronment varibles.
2. Build docker image : docker-compose build
3. run docker : docker-compose up


##Run Test
$. python manage.py test tests/
or 
$. ./run_tests.sh


##Endpoint
1. http://127.0.0.1:5000
2. Swagger : http://127.0.0.1:8000/api-documentation


