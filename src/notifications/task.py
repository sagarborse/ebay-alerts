import json
import logging

from celery.schedules import crontab
from django.conf import settings
from django.utils import timezone
from redis import Redis

from notifications.models import Notification, SendUpdate
from notifications.utils import (
    save_ebay_product,
    send_notification,
    get_product_price_change_report,
    serialize_reports
)
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
        products = save_ebay_product(notification.id)

        logging.info(f"sending notification to {notification.email} for"
                     f" notification id {notification.id}")
        subject = f" Notification for your search :  {notification.search_text}"
        send_notification(subject, notification, products,
                                "emails/prodnotify.html")
        SendUpdate.objects.create(alert=notification)


@app.task
def product_user_notification():
    logging.info("Checking for alert")
    notifications = Notification.objects.all()
    for notify in notifications:
        try:
            last_update = notify.update_set.latest('timestamp').timestamp
        except SendUpdate.DoesNotExist:
            last_update = None

        time_diff = (timezone.now() - last_update).seconds/60 if \
            last_update else float('inf')
        if time_diff >= notify.time_interval:
            # this difference can be little un-accurate
            send_notification.delay(notification=notify.id)


@app.task()
def product_price_change_alert():
    """
    Send price change alert to user and Team B
    :return:
    """
    redis = Redis(settings.REDIS_HOST)
    notifications = Notification.objects.all()
    for notify in notifications:
        report = get_product_price_change_report(notify)

        if True:
            # sending 2% decrease alert to the user, if any
            send_notification(
                subject="2% price drop!",
                alert=notify,
                products=report['decreased_2_per'],
                template="emails/price_change.html"
            )

        # Report to the broker so can be read by Team B
        report = serialize_reports(report)
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
        # At 12:00 on every 2nd day-of-month from
        # 1 through 31  https://crontab.guru/#0_12_1-31/2_*_*
        # crontab(
        #     minute='0',
        #     hour='12',
        #     day_of_month='1-31/2',
        #     month_of_year='*',
        #     day_of_week='*'
        # ),
        crontab(),
        product_price_change_alert.s()
    )
