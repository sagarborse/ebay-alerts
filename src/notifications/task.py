import json
import logging

from celery.schedules import crontab
from django.conf import settings
from django.utils import timezone
from redis import Redis

from alerts.models import ProductAlert, Update
from alerts.utils import (
    save_ebay_product,
    send_alert_notification,
    get_product_price_change_report,
    serialize_reports
)
from taskapp.celery import app

logger = logging.getLogger(__name__)


@app.task
def send_notification(alert_id: int) -> None:
    """
    fetch products from ebay and send email notification
    :param alert_id: alert id
    :return: None
    """
    try:
        alert = ProductAlert.objects.get(id=alert_id)
    except ProductAlert.DoesNotExist:
        logger.error(f"alert does not exist by id {alert_id}")
    else:
        logging.info(f"fetching ebay products for alert id {alert.id}")
        products = save_ebay_product(alert.id)

        logging.info(f"sending email notification to {alert.email} for"
                     f" alert id {alert.id}")
        # Send email notification here and save update
        subject = f" New alert for your product {alert.search_phrase}"
        send_alert_notification(subject, alert, products,
                                "emails/product_alert.html")
        Update.objects.create(alert=alert)


@app.task
def product_alert_notification():
    """
    Check for periodic alert notification
    :return: None
    """
    logging.info("Checking for alert")
    alerts = ProductAlert.objects.all()
    for alert in alerts:
        try:
            last_update = alert.update_set.latest('timestamp').timestamp
        except Update.DoesNotExist:
            last_update = None

        time_diff = (timezone.now() - last_update).seconds/60 if \
            last_update else float('inf')
        if time_diff >= alert.time_interval:
            # this difference can be little un-accurate
            send_notification.delay(alert_id=alert.id)


@app.task()
def product_price_change_alert():
    """
    Send price change alert to user and Team B
    :return:
    """
    redis = Redis(settings.REDIS_HOST)
    alerts = ProductAlert.objects.all()
    for alert in alerts:
        report = get_product_price_change_report(alert)

        if report['decreased_2_per']:
            # sending 2% decrease alert to the user, if any
            send_alert_notification(
                subject="2% price drop!",
                alert=alert,
                products=report['decreased_2_per'],
                template="emails/price_change.html"
            )

        # push to report to queue which can be listened by team B
        report = serialize_reports(report)
        report['alert_id'] = alert.id
        report['email'] = alert.email
        redis.rpush(settings.PRICE_REPORT_REDIS_QUEUE, json.dumps(report))


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(),  # every minute
        product_alert_notification.s(),
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
