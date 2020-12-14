import datetime
import os
from pytz import timezone

seoul = timezone('Asia/Seoul')
from export_orders import ExportData

import dateutil.relativedelta as rdelta


class FirebaseNotify:

    def __init__(self):
        print("Hey")
        module = os.environ['DJANGO_SETTINGS_MODULE']
        self.production = module == "shoppingmall.settings.production"

    def getDeliveryDate(self):
        weekday = datetime.datetime.today().weekday()
        todayDataTime = datetime.datetime.now(seoul)
        hour = int(todayDataTime.strftime('%H'))
        title = todayDataTime.strftime('%d/%m/%Y')
        if weekday == 5 or weekday == 6:
            today = datetime.datetime.today()
            next_monday = today + rdelta.relativedelta(days=1, weekday=rdelta.MO(+1))
            title = next_monday.strftime('%d/%m/%Y')
            print(next_monday)
        elif weekday == 4:
            if hour > 13:
                today = datetime.datetime.today()
                next_monday = today + rdelta.relativedelta(days=1, weekday=rdelta.MO(+1))
                title = next_monday.strftime('%d/%m/%Y')
                print(next_monday)

        else:
            if hour > 13:
                tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                title = tomorrow.strftime('%d/%m/%Y')

        return title

    def send_order_accepted_message_to_users(self, order):
        if self.production:
            topic = order["user"]["id"]
        else:
            topic = "dev-" + str(order["user"]["id"])

        from fcm_django.fcm import fcm_send_topic_message

        deliveryDate = self.getDeliveryDate()
        message_body = ""
        if order["language"] == "uz":
            message_body = "Buyurmantingiz qabul qilindi"
            message_body += f"\nBuyurtma raqami: {order['order_number']}"
            message_body += f"\nBuyurtma jo’natilish sanasi: {deliveryDate}"
        if order["language"] == "ru":
            message_body = "Ваш заказ был принят"
            message_body += f"\nНомер заказа: {order['order_number']}"
            message_body += f"Дата отправки заказа {deliveryDate}"
        if order["language"] == "en":
            message_body = "Your order accepted"
            message_body += f"\nOrder number: {order['order_number']}"
            message_body += f"\nOrder sent date: {deliveryDate}"
        fcm_send_topic_message(topic_name=topic, message_body=message_body, message_title='Hojibobo')

    def send_order_paid_message_to_users(self, order):
        if self.production:
            topic = order["user"]["id"]
        else:
            topic = "dev-" + str(order["user"]["id"])

        from fcm_django.fcm import fcm_send_topic_message

        message_body = ""
        if order["language"] == "uz":
            message_body = "To'lovingiz tasdiqlandi"
            message_body += f"\nBuyurtma raqami: {order['order_number']}"
        if order["language"] == "ru":
            message_body = "Ваш заказ был принят"
            message_body += f"\nНомер заказа: {order['order_number']}"
        if order["language"] == "en":
            message_body = "Your payment confirmed"
            message_body += f"\nOrder number: {order['order_number']}"
        fcm_send_topic_message(topic_name=topic, message_body=message_body, message_title='Hojibobo')
