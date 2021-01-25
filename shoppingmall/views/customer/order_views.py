import datetime
import json
import os

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shoppingmall.models import Order, Product
from shoppingmall.serializers.order_serializers import OrderSerializer, OrderedProductSerializer, OrderDetailsSerializer
from firebase_notify import FirebaseNotify
from shoppingmall.serializers.product_serializers import ProductCreateSerializer
from shoppingmall.utils.logger import Logger
from telegram_notify import TelegramNotify

from pytz import timezone

seoul = timezone('Asia/Seoul')

import dateutil.relativedelta as rdelta

conf = {
    "hojibobo_users": [
        90193228,
        813757388
    ]
}


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().filter(deleted=False).order_by('-date_created')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        user = self.request.user
        language = "uz"
        if user.is_authenticated and user.is_customer():
            language = user.customer.language
        if 'lang' in self.request.query_params:
            language = self.request.query_params['lang']
        return {"language": language, "request": self.request}

    def retrieve(self, request, *args, **kwargs):

        user = request.user
        if user.is_customer():
            instance = self.get_object()
            serializer = OrderDetailsSerializer(instance, context=self.get_serializer_context())
            response = serializer.data
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id="", user_id=user.id, payload_string=response, status_code=200)
            return Response(response)
        else:
            response = {"error": ["Only customer can access"]}
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=403)
            return Response(response, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['put'])
    def receipt(self, request, pk=None):
        user = request.user
        if user.is_customer():
            data = request.data
            instance = self.get_object()
            serializer = OrderSerializer(instance, data=data, partial=False)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            response = {"message": ["Updated"]}
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=200)
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {"error": ["Only customer can access"]}
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=403)
            return Response(response, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False)
    def history(self, request, pk=None):
        user = request.user
        if user.is_customer():
            orders = Order.objects.filter(user=request.user).distinct().order_by('-date_created')
            response = OrderSerializer(orders, context=self.get_serializer_context(), many=True).data

            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=200)
            return Response(response)
        else:
            response = {"error": ["Only customer can access"]}
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=403)
            return Response(response, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['post'], detail=True)
    def cancel(self, request, pk=None):
        user = request.user
        if user.is_customer():
            obj = self.get_object()
            obj.status = 'C'
            obj.save()
            response = OrderSerializer(obj, context=self.get_serializer_context()).data
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=200)
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response({"error": ["Only customer can access"]}, status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def getDeliveryDate(self):
        weekday = datetime.datetime.today().weekday()
        todayDataTime = datetime.datetime.now(seoul)
        hour = int(todayDataTime.strftime('%H'))
        title = todayDataTime.strftime('%Y-%m-%d')
        if weekday == 5 or weekday == 6:
            today = datetime.datetime.today()
            next_monday = today + rdelta.relativedelta(days=1, weekday=rdelta.MO(+1))
            title = next_monday.strftime('%Y-%m-%d')
            print(next_monday)
        elif weekday == 4:
            if hour > 17:
                today = datetime.datetime.today()
                next_monday = today + rdelta.relativedelta(days=1, weekday=rdelta.MO(+1))
                title = next_monday.strftime('%Y-%m-%d')
                print(next_monday)

        else:
            if hour > 17:
                tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                title = tomorrow.strftime('%Y-%m-%d')

        return title

    """
    List a queryset.
    """

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_customer():

            queryset = Order.objects.filter(user=user.pk).order_by(
                '-date_created', '-is_paid')
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = OrderSerializer(page, context=self.get_serializer_context(), many=True)
                return self.get_paginated_response(serializer.data)

            serializer = OrderSerializer(queryset, context=self.get_serializer_context(), many=True)

            return Response(serializer.data)
        else:
            response = {"error": ["Only customer can access"]}
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=403)
            return Response(response, status=status.HTTP_403_FORBIDDEN)
