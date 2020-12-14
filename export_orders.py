import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
from gspread_formatting import *
import datetime
from pytz import timezone
import os

seoul = timezone('Asia/Seoul')
import phonenumbers
import dateutil.relativedelta as rdelta

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]


class ExportData:

    def __init__(self):
        module = os.environ['DJANGO_SETTINGS_MODULE']

        if module == "shoppingmall.settings.production":
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                os.path.dirname(os.path.abspath(__file__)) + "/hojibobo-pro-409180374fe9.json", scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                os.path.dirname(os.path.abspath(__file__)) + "/hojibobo-dev-cebe9ab24f75.json", scope)
        self.clientAuth = gspread.authorize(creds)

    def new_order_to_store(self, order):

        client = self.clientAuth.open("hojibobo_orders_2020")

        weekday = datetime.datetime.today().weekday()
        # today
        todayDataTime = datetime.datetime.now(seoul)
        hour = int(todayDataTime.strftime('%H'))
        title = todayDataTime.strftime('%d/%m/%Y')
        if weekday == 5 or weekday == 6:
            today = datetime.datetime.today()
            next_monday = today + rdelta.relativedelta(days=1, weekday=rdelta.MO(+1))
            title = next_monday.strftime('%d/%m/%Y')
            print(next_monday)
        elif weekday == 4:
            if hour > 14:
                today = datetime.datetime.today()
                next_monday = today + rdelta.relativedelta(days=1, weekday=rdelta.MO(+1))
                title = next_monday.strftime('%d/%m/%Y')
                print(next_monday)
        elif weekday == 0:
            if hour > 14:
                tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                title = tomorrow.strftime('%d/%m/%Y')
        else:
            if hour > 13:
                tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                title = tomorrow.strftime('%d/%m/%Y')

        try:
            sheet = client.worksheet(title=title)
        except:
            sheet = client.add_worksheet(title=title, rows=200, cols=100)

        ordercells = sheet.col_values(12)
        row = sheet.get_all_values()
        index = len(row) + 1

        orderProductText = ""
        total_buying = order['total_buying']
        total_selling = order['total_selling']
        for orderedProduct in order['products']:
            product = orderedProduct['product']
            orderProductText += " {} - {}{},".format(product['title'], orderedProduct['quantity'], product['unit'])

        buying = total_buying
        selling = total_selling
        delivery_fee = order['delivery_fee']

        phone_number = order['phone']
        try:
            x = phonenumbers.parse(phone_number, "KR")
            phone_number = phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.NATIONAL)
        except:
            pass

        buyer = "Hojibobo"
        if order['is_dealer']:
            buyer = order['user']['name']

        insertRow = [index, phone_number,
                     order['name'],
                     order['address'],
                     orderProductText,
                     buying,
                     delivery_fee,
                     selling,
                     buyer,
                     order['order_number'],
                     todayDataTime.strftime('%d/%m/%Y %H:%M:%S')
                     ]
        sheet.insert_row(insertRow, index=index)

    def new_order_to_hojibobo(self, orderedProducts, posting_date):
        client = self.clientAuth.open("hojibobo_daily_ordered_products")

        try:
            sheet = client.worksheet(title=posting_date)
            sheet.clear()
        except:
            sheet = client.add_worksheet(title=posting_date, rows=200, cols=100)

        row = sheet.get_all_values()
        index = len(row) + 1

        if index == 1:
            insertRowHeader = ["T/r", "Products", "Qauntity"]
            sheet.append_row(insertRowHeader)
            index += 1

        for orderedProduct in orderedProducts:
            product = orderedProduct['product']

            insertRow = [index - 1, f"{product['title_kr']} / {product['title_uz']}",
                         orderedProduct['quantity']]
            index = index + 1
            sheet.append_row(insertRow)

#
# order = {
#     "id": 136,
#     "user": {
#         "id": 90193228,
#         "first_name": "Sardorbek",
#         "last_name": "Numonov",
#         "username": "sardorbek93",
#         "phone_number": "+821040439398",
#         "language_code": "uz",
#         "address": "서울 용산구 신흥로 14 길 5",
#         "address_image": "/media/user_90193228/address/7d0114bc-564.jpeg",
#         "date_joined": "2020-03-14T04:42:50.076622Z"
#     },
#     "address": "서울 용산구 신흥로 14 길 5",
#     "order_number": "9019322281111235321112",
#     "products": [
#         {
#             "id": 137,
#             "order": 136,
#             "product": {
#                 "id": 5,
#                 "category": {
#                     "id": 1,
#                     "title": "Mol go'shti",
#                     "image": "http://167.99.3.253:8008/media/category/87f73e97-c7d.jpeg"
#                 },
#                 "code": "M2",
#                 "label": "N",
#                 "banner": False,
#                 "price": 13000.0,
#                 "image": {
#                     "id": 16,
#                     "image": "http://167.99.3.253:8008/media/product_M2/eb59805f-c45.jpeg",
#                     "main_image": True,
#                     "date_created": "2020-02-29T07:04:53.319723Z",
#                     "product": 5
#                 },
#                 "title": "Mol Bo'yin",
#                 "unit": "kg",
#                 "overable": False
#             },
#             "quantity": 5
#         },
#         {
#             "id": 138,
#             "order": 136,
#             "product": {
#                 "id": 6,
#                 "category": {
#                     "id": 1,
#                     "title": "Mol go'shti",
#                     "image": "http://167.99.3.253:8008/media/category/87f73e97-c7d.jpeg"
#                 },
#                 "code": "M3",
#                 "label": "N",
#                 "banner": False,
#                 "price": 14000.0,
#                 "image": {
#                     "id": 17,
#                     "image": "http://167.99.3.253:8008/media/product_M3/a0271965-b31.jpeg",
#                     "main_image": True,
#                     "date_created": "2020-02-29T07:07:46.403538Z",
#                     "product": 6
#                 },
#                 "title": "Mol Dum",
#                 "unit": "kg",
#                 "overable": False
#             },
#             "quantity": 5
#         }
#     ],
#     "status": "P",
#     "payment": "UNPAID",
#     "post_code": "",
#     "date_created": "2020-03-19T13:53:53.208352Z"
# }
#
# exportData = ExportData()
# exportData.new_order_to_albaraka(order)
