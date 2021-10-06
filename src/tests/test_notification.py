import json
import os
from unittest import mock
from core.settings import BASE_DIR
from django.test import TestCase
from notifications.models import Notification
from notifications.utils import autoclave_data, store_product


class TestProductPriceChangeAlert(TestCase):
    def setUp(self):
        # Setup run before every test method.

        # Save data in test database
        # Sample product for no price changes
        self.ebay_response = mock_response()
        self.product_alert = Notification.objects.create(email="sagarborse90@gmail.com", search_text="mobile", frequency=2)

    def test_autoclave_data(self):
        response = autoclave_data(self.ebay_response[0])
        self.assertEqual(type(response), tuple,
                         "Response from autoclave_data is product and amount data")
        self.assertEqual(response[0]['ebay_prd_id'], self.ebay_response[0]
        ["itemId"][0], "Ebay item id is transformed as ebay_prd_id in response"
                         )
        self.assertEqual(response[0]['img_url'], self.ebay_response[0]
        ["viewItemURL"][0], "Ebay image url")
        self.assertEqual(response[1], self.ebay_response[0]
        ["sellingStatus"][0]["currentPrice"][0]["__value__"],
                         "Ebay product price")

    @mock.patch('notifications.utils.get_product_info')
    def test_get_product_info(self, mock_get_product_info):
        mock_get_product_info.return_value = self.ebay_response
        products = store_product(self.product_alert.id)
        self.assertEqual(len(products), 20, 'Product got saved in db')
        self.assertEqual(products[0].notification_id, self.product_alert.id,
                         'Product got saved for created alert')


def mock_response():
    file_path = os.path.join(os.path.join(BASE_DIR, 'tests'), 'mock_response.json')
    with open(file_path) as json_file:
        data = json.load(json_file)
    return data
