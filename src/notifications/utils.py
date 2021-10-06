import logging
from decimal import Decimal
from typing import List, Tuple, Dict

import requests
from django.core.mail import EmailMessage
from django.db.models import Max, ObjectDoesNotExist
from django.db.models.functions import Coalesce
from django.template.loader import get_template
from django.utils import timezone

from notifications.models import Product, Amount, Notification
from core.settings import EBAY_APP_ID, EBAY_SANDBOX_URL, EMAIL_HOST_USER

logger = logging.getLogger(__name__)


def autoclave_data(ebay_item: dict) -> Tuple[dict, float]:
    data = {
        'ebay_prd_id': ebay_item['itemId'][0],
        'title': ebay_item["title"][0],
        'img_url': ebay_item["viewItemURL"][0],
        "location": ebay_item["location"][0]
    }
    amount: float = ebay_item["sellingStatus"][0]["currentPrice"][
        0]["__value__"]

    return data, amount


def get_product_info(search_text: str, sorted_by: str = 'amount', limit: int = 20) -> List[dict]:
    ebay_url = EBAY_SANDBOX_URL.format(EBAY_APP_ID, search_text, sorted_by,
                                    limit)

    response = requests.get(ebay_url)
    response = response.json()

    product_data = []
    if response["findItemsByKeywordsResponse"][0]["ack"][0] == 'Success':
        product_data = response["findItemsByKeywordsResponse"][0][
            "searchResult"][0]["item"]
    else:
        logger.error("Error: {} in fetching product for :{}".format(
            response["errorMessage"], search_text))

    return product_data


def store_product(notification_id: int) -> List[Product]:
    notification = Notification.objects.get(id=notification_id)
    ebay_items = get_product_info(notification.search_text)
    autoclave = [autoclave_data(item) for item in ebay_items]
    products = []
    for product_data, amount in autoclave:
        product, _ = Product.objects.get_or_create(
            ebay_prd_id=product_data['ebay_prd_id'],
            notification=notification,
            defaults=product_data
        )

        try:
            # get last price
            last_price = product.amount_set.latest('timestamp')
        except ObjectDoesNotExist:
            _ = Amount.objects.create(amount=amount, product=product)
        else:
            if last_price.amount != Decimal(amount).quantize(Decimal('.01')):
                # create price, if there is some change inn price
                _ = Amount.objects.create(amount=amount, product=product)
        products.append(product)

    # sort by price, as it'll be mostly 20 products , this should be fine
    products = sorted(products, key=lambda p: float(p.amount))

    return products


def send_notification(subject: str, notify: Notification, products: List[Product], template: str) -> int:
    """
    Sends Email notifications
    """
    message = get_template(template).render({
        'products': products,
        'notification': notify
    })
    mail = EmailMessage(
        subject=subject,
        body=message,
        from_email=EMAIL_HOST_USER,
        to=[notify.email],
    )

    mail.content_subtype = "html"
    return mail.send()

def send_report(notify: Notification) -> Dict[str, List[Product]]:
    PRODUCT_PRICE_CHANGE_DAYS = 2
    now = timezone.now()
    from_date = now - timezone.timedelta(days=int(PRODUCT_PRICE_CHANGE_DAYS))
    report = {
        'decreased_2_per': [],
        'decreased': [],
        'no_change': []
    }
    products = Product.objects.filter(notification=notify)
    for product in products:
        last_max_price = product.amount_set.filter(
            timestamp=from_date.date(),
        ).aggregate(
            max_price=Coalesce(Max('price'), Decimal('0.0'))
        )['max_price']
        current_amount = product.amount
        if current_amount < last_max_price:
            decrease = last_max_price - current_amount
            decrease_perc = (decrease / last_max_price) * Decimal('100.00')
            if decrease_perc >= 2:
                report['decreased_2_per'].append(product)
            else:
                report['decreased'].append(product)
        elif current_amount == last_max_price:
            report['no_change'].append(product)
    return report


def serialize_reports(report: dict) -> dict:
    ser = {}
    for report, products in report.items():
        ser[report] = [p.dict() for p in products]
    ser['timestamp'] = timezone.now().isoformat()
    return ser
