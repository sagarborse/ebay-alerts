import json
import logging
from celery.schedules import crontab
from django.conf import settings
from django.utils import timezone
from redis import Redis
from notifications.models import Notification, SendUpdate
from notifications.utils import (store_product, send_notification, send_report, formatted_report)
from core.celery import app

logger = logging.getLogger(__name__)


@app.task
def send_user_notification(notify_id: int) -> None:
    try:
        notification = Notification.objects.get(id=notify_id)
    except Notification.DoesNotExist:
        logger.error(f"Notification doesn't exist {notify_id}")
    else:
        logging.info(f"get ebay products for  {notification.id}")
        products = store_product(notification.id)

        logging.info(f"sending notification to {notification.email} for"
                     f" notification id {notification.id}")
        subject = f" Notification for your search :  {notification.search_text}"
        send_notification(subject, notification, products,
                          "email_templates/product_notification.html")
        SendUpdate.objects.create(notification=notification)


@app.task
def product_user_notification():
    notifications = Notification.objects.all()
    for notify in notifications:
        send_notification.delay(notification=notify.id)
        try:
            last_update = notify.update_set.latest('timestamp').timestamp
        except SendUpdate.DoesNotExist:
            last_update = None

        time_diff = (timezone.now() - last_update).seconds / 60 if \
            last_update else float('inf')
        if time_diff >= notify.time_interval:
            send_notification.delay(notification=notify.id)


@app.task()
def product_amount_change_alert():
    redis = Redis(settings.REDIS_HOST)
    notifications = Notification.objects.all()
    for notify in notifications:
        report = send_report(notify)

        if report['two_perc_decrease']:
            send_notification(
                subject="Price Drop Alert 2% !!!",
                notify=notify,
                products=report['two_perc_decrease'],
                template="email_templates/price_notification.html"
            )

        # Report to the broker so can be read by Team B
        report = formatted_report(report)
        report['alert_id'] = notify.id
        report['email'] = notify.email
        redis.rpush(settings.NOTIFICATION_QUEUE, json.dumps(report))


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(),  # every minute
        product_user_notification.s(),
    )
    sender.add_periodic_task(
        crontab(),
        product_amount_change_alert.s()
    )
