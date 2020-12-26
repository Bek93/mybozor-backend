from __future__ import absolute_import, unicode_literals

from time import sleep
from django.utils import timezone

from celery import shared_task
from django.db import connection

from shoppingmall.models import Announcement, Filter, Customer
from telegram_notify import TelegramNotify

telegram = TelegramNotify()


@shared_task
def add(x, y):
    return x + y


@shared_task
def send_marketing_push_task(userId, message):
    print(userId, message)
    for i in range(1, 100):
        telegram.sendMessage(userId, message)
    return "Done"


@shared_task
def send_bulk_customer(customers, announcement):
    message = announcement.titles.uz + "\n" + announcement.descriptions.uz
    for customer in customers:
        telegram.sendMessage(90193228, message)
    return "Done"


@shared_task
def send_announcements(announcementId):
    announcement = Announcement.objects.get(id=announcementId)
    customers = filteredCustomers(filter=announcement.filter)
    announcement.started_at = timezone.now()
    announcement.save()
    total_target_count = 0
    while len(customers) > 0:
        send_bulk_customer(customers, announcement)
        total_target_count += len(customers)
        customers = filteredCustomers(filter=announcement.filter, offset=len(customers))

    announcement.is_completed = True
    announcement.total_target_count = total_target_count
    announcement.ended_at = timezone.now()
    announcement.save()


def my_custom_sql(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()

    return row


def filteredCustomers(filter, limit=100, offset=0):
    query_params = ''

    if filter.type == 'filter':
        if filter.province:
            if len(query_params) > 0:
                query_params += " and "
            query_params += " province_id=" + str(filter.province)
        if filter.language:
            if len(query_params) > 0:
                query_params += " and "
            query_params += f" language='{filter.language}'"
        if filter.gender:
            if len(query_params) > 0:
                query_params += " and "
            query_params += f" gender='{filter.gender}'"

        if len(query_params) > 0:
            query_params = "where " + query_params

        query_params += f" limit {limit} offset {offset}"
        query = f"""SELECT username FROM shoppingmall_user where id in (SELECT user_ptr_id from shoppingmall_customer
                          {query_params})"""

    result = my_custom_sql(query)

    customers = []
    for row in result:
        customers.append(row[0])

    print(len(customers))
    print(customers)
    return customers
