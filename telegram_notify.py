import datetime
import json
import os
import sys

import phonenumbers
from pytz import timezone

import telegram
from telegram import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from firebase_notify import FirebaseNotify
from globals import TXT_NEW_ORDER, TXT_ACCEPTED_ORDER_SELLER, TXT_ACCEPTED_ORDER_CUSTOMER, TXT_ORDER_PAID
from sms.middleware import MessageClient

seoul = timezone('Asia/Seoul')
from export_orders import ExportData

import dateutil.relativedelta as rdelta

BTN_PAID = "Paid"
BTN_ACCEPT = "Accept"


class TelegramNotify:

    def __init__(self):
        module = os.environ['DJANGO_SETTINGS_MODULE']
        self.production = module == "shoppingmall.settings.production"

    def send_order_accepted_message(self, order, shop):
        if order['type'] == 'T':
            self.send_order_accepted_message_to_users(order, shop)
        elif order['type'] == 'A':
            fcm = FirebaseNotify()
            fcm.send_order_accepted_message_to_users(order)
        try:
            self.send_order_accepted_message_to_store(order, shop)
        except Exception as e:
            print(e)
        # exportData = ExportData()
        # exportData.new_order_to_store(order)

    def getConfiguration(self, type):
        conf = {}
        try:
            filename = '/telegrams_keys.json'
            dirname = os.path.dirname(os.path.abspath(__file__)) + filename
            with open(dirname, 'r') as keys_file:
                conf = json.load(keys_file)
        except Exception as ex:
            print(ex)

        token = None
        if not self.production:
            token = conf['annyong_store_dev']
        else:
            if type == 0:
                token = conf['annyong_store_order']
            elif type == 1:
                token = conf['annyong_store']
            elif type == 2:
                token = conf['annyong_store_accepted']

        return [token, conf]

    def send_order_accepted_message_to_users(self, order, shop):
        config = shop['config']
        token = config['telegram_accept']
        users = config['telegram_users']
        if token:
            bot = telegram.Bot(token=token)
            order_number = order['order_number']
            user = order['user']
            language_code = order['language']
            products = order['products']
            quantityAll = 0
            total = 0
            html = ""
            on = 1
            for orderedProduct in products:
                product = orderedProduct['product']
                titles = product['titles']
                selling = product['selling']
                quantity = orderedProduct['quantity']
                unit = product['unit']
                quantityText = str(quantity) + "" + unit
                quantityAll += quantity
                total_fee = selling * int(quantity)
                total = total + total_fee
                if language_code == 'ru':
                    html += "\n{}. <b>{}</b> x {}".format(on, titles[language_code], quantityText)
                else:
                    html += "\n{}. <b>{}</b> x {}".format(on, titles[language_code], quantityText)
                on = on + 1

            deliveryDate = self.getDeliveryDate()

            customer = order['user']
            telegram_id = str(customer['username']).replace("asut", "")

            html = TXT_ACCEPTED_ORDER_CUSTOMER[language_code].format(order_number, html, deliveryDate)
            bot.send_message(
                chat_id=int(telegram_id),
                text=html,
                parse_mode="HTML"
            )

    def send_order_accepted_message_to_store(self, order, shop):
        config = shop['config']
        token = config['telegram_accept']
        users = config['telegram_users']
        if token:
            bot = telegram.Bot(token=token)
            order_number = order['order_number']
            address = order['address']
            user = order['user']
            products = order['products']
            on = 1

            product_html = ""
            for orderedProduct in products:
                product = orderedProduct['product']
                titles = product['titles']
                quantity = orderedProduct['quantity']
                unit = product['unit']
                quantityText = str(quantity) + "" + unit
                product_html += "\n{}. <b>{}</b> x {}".format(on, titles['uz'], quantityText)
                on = on + 1

            html = TXT_ACCEPTED_ORDER_SELLER[order['language']].format(order_number, product_html, order['name'],
                                                                       order["phone"], address)

            for user in users:
                try:
                    bot.send_message(
                        chat_id=user,
                        text=html,
                        parse_mode="HTML"
                    )
                except:
                    continue

    def send_new_order(self, order, shop):
        config = shop['config']
        token = config['telegram_new_order']
        users = config['telegram_users']
        if token:
            bot = telegram.Bot(token=token)
            order_number = order['order_number']
            user = order['user']
            products = order['products']
            on = 1

            buttons = [[InlineKeyboardButton(BTN_PAID, callback_data="order_payment_{}_done".format(order['id'])),
                        InlineKeyboardButton(BTN_ACCEPT, callback_data="order_accept_{}_done".format(order['id']))]]

            quantityAll = 0
            product_html = ""
            for orderedProduct in products:
                product = orderedProduct['product']
                title = product['titles'][order['language']]
                price = product['selling']
                quantity = orderedProduct['quantity']
                unit = product['unit']
                quantityText = str(quantity) + "" + unit
                quantityAll += quantity

                total_fee = price * int(quantity)
                product_html += "\n   {}. <b>{}</b> x {} = {}".format(on, title,
                                                                      quantityText,
                                                                      '{:,} won'.format(
                                                                          int(total_fee)))
                on = on + 1

            total = order['total_selling']
            delivery_fee = order['delivery_fee']
            total = total + delivery_fee
            html = TXT_NEW_ORDER[order['language']].format(order_number, product_html, order['name'], int(delivery_fee),
                                                           int(total), order['address'])

            for user in users:
                try:
                    bot.send_message(
                        chat_id=int(user),
                        text=html,
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup(buttons)
                    )
                except:
                    continue

    def send_order_paid_message_to_users(self, order):
        [token, conf] = self.getConfiguration(0)
        if token:
            bot = telegram.Bot(token=token)
            order_number = order['order_number']
            language_code = order['language']
            delivery_fee = order['delivery_fee']
            total = order['total_selling']
            total = total + + delivery_fee
            customer = order['user']
            telegram_id = str(customer['username']).replace("asut", "")
            bot.send_message(
                chat_id=telegram_id,
                text=TXT_ORDER_PAID[language_code].format(order_number, '{:,} won'.format(int(total))),
                parse_mode="HTML"
            )

    def send_order_sent_message(self, order):
        [token, conf] = self.getConfiguration(1)
        if token:
            bot = telegram.Bot(token=token)
            order_number = order['order_number']
            user = order['user']
            address = user['address']
            post_code = order['post_code']
            language_code = order['language']
            products = order['products']
            html = ""
            on = 1
            for orderedProduct in products:
                product = orderedProduct['product']
                title = product['title']
                quantity = orderedProduct['quantity']
                unit = product['unit']
                quantityText = str(quantity) + "" + unit
                html += "\n{}. <b>{}</b> x {} ".format(on, title,
                                                       quantityText)
                on = on + 1

            todayDataTime = datetime.datetime.now(seoul)
            todayDataTime = todayDataTime + datetime.timedelta(days=1)
            day = todayDataTime.strftime('%d-%m-%Y')
            if language_code == 'ru':
                bot.send_message(
                    chat_id=order['telegram_user_id'],
                    text="<b>Ваш заказ был отправлен</b>\n<b>Номер заказа: </b>{}{}\n\n<b>Адрес: </b>{}\n\nДопуск: {}\n(если у TEKBE нет проблем)\n\nСпасибо за покупку.".format(
                        order_number, html,
                        address, day),
                    parse_mode="HTML"
                )
            else:
                bot.send_message(
                    chat_id=order['telegram_user_id'],
                    text="<b><u>Buyurmantingiz jo'natildi</u></b>\n<b>Buyurtma raqami: </b>{}{}\n\n<b>Manzil: </b>{}\n\nQabul qilish:  {}\n(agarda TEKBE kompaniyasida muammolar kuzatilmasa)\n\nXaridingiz uchun tashakkur.\n\nHojiBobo, bizda hizmat beminnat!".format(
                        order_number, html,
                        address,
                        day
                    ),
                    parse_mode="HTML"
                )

    def sendMessage(self, userId, message):
        [token, conf] = self.getConfiguration(1)
        if token:
            bot = telegram.Bot(token=token)
            return bot.send_message(
                chat_id=userId,
                text=message
            )

    def send_notification(self, userId, notification):
        [token, conf] = self.getConfiguration(1)
        if token:
            bot = telegram.Bot(token=token)

            if notification.image:
                bot.send_photo(
                    chat_id=userId,
                    photo=notification.image,
                    caption=notification.content
                )
            else:
                bot.send_message(
                    chat_id=userId,
                    text=notification.content
                )

    def send_sms_to_customer(self, order):
        products = order['products']
        html = f"{order['user']['name']}     \nXurmatli mijoz, " + order['name']
        total = order['total_selling']
        delivery_fee = order['delivery_fee']
        total = total + delivery_fee
        html += "\nYetkazib berish narxi: {}".format('{:,} won'.format(int(delivery_fee)))
        html += "\nUmmiy Summa: {}".format('{:,} won'.format(int(total)))
        html += f"\n{order['user']['bank_account']}"
        phone = phonenumbers.parse(order['phone'], "KR")
        phone_number = f"+{phone.country_code}{phone.national_number}"

        client = MessageClient()
        client.send_message(html, phone_number)

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

        elif weekday == 0:
            if hour > 14:
                tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                title = tomorrow.strftime('%d/%m/%Y')
        else:
            if hour > 13:
                tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                title = tomorrow.strftime('%d/%m/%Y')

        return title
