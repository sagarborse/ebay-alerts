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
4. Event driven architecture makes the system is highly available and components are loosely coupled. 
6. Swagger brings api documentation really well.
8. Docker is used toi dockerized the app. to make system platform independent and easily deployable in Cloud.


## Logic
 
 1st Phase : 
 a. Impletmented a service which gets all the products from ebay for user created notifications
 b.  Notifications table is used to store product notifications
 c. SendUpdate table is used to tracked already send notifications
 d. Amount table is used to keep track of changes/ logs in product amount.
 
 2nd Phase:
 a. This service is schedule for alternate days
 b. Notifications are schedule for price change if any / two percent change in price etc
 c. For Team B can subscribe to the queue to get information about user notifications or amount changes.
 d. Team B implementation is added as a consumer in team_b_implementation folder in repo


