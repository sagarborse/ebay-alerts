# Ebay-Alerts
Sytem which provides notifications for price drop of a product on ebay with other metrics.

## Technologies
Django, Django DRF, Swagger, Postgres, Redis, Celery, Docker

## Setup
1. Rename env.txt file to .env file and add appropriate values of all the envioronment varibles.
2. Build docker image : docker-compose build
3. run docker : docker-compose up


## Run Test
$. python manage.py test tests/
or 
$. ./run_tests.sh


## Endpoint
1. http://127.0.0.1:5000
2. Swagger : http://127.0.0.1:8000/api-documentation


## Description

1.Framework used is Django Rest framework as it is suitable to build and connect with other apps like postgres / API development / Celery.
2. Using Celery primarily for event driven architecture along with Redis Queue. As per the use case Celery can be used to schedule as well as helps in queue management via workers.
3. Event driven architecture makes the system is highly available and components are loosely coupled. 
4. Swagger brings api documentation really well.
5. Docker is used toi dockerized the app. to make system platform independent and easily deployable in Cloud.


