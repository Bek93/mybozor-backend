import datetime
import json
import os

from django.db import connection
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


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().filter(deleted=False).order_by('-date_created')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        if user.is_admin():
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

    """
    List a queryset.
    """

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_admin():
            query_params = request.query_params
            from_date = None
            to_date = None
            if 'from' in query_params:
                from_date = query_params['from']

            if 'to' in query_params:
                to_date = query_params['to']
            payment = None
            if 'payment' in query_params:
                payment = query_params['payment']
            statusOrder = None
            if 'status' in query_params:
                statusOrder = query_params['status']

            shop = None
            if 'shop' in query_params:
                shop = query_params['shop']

            deleted = False
            if 'deleted' in query_params:
                deleted = query_params['deleted']
            queryset = Order.objects.filter(deleted=deleted)
            if from_date and to_date:
                queryset = queryset.filter(date_created__date__range=[from_date, to_date])
            if payment:
                queryset = queryset.filter(payment=payment)
            if shop:
                queryset = queryset.filter(shop=shop)
            if statusOrder:
                queryset = queryset.filter(status=statusOrder)
            queryset = queryset.order_by('-date_created', )
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = OrderDetailsSerializer(page, context=self.get_serializer_context(), many=True)
                return self.get_paginated_response(serializer.data)

            serializer = OrderDetailsSerializer(queryset, context=self.get_serializer_context(), many=True)
            return Response(serializer.data)

        else:
            response = {"error": ["Only seller can access"]}
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=403)
            return Response(response, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['get'], detail=False)
    def overview(self, request, pk=None):
        if request.user.is_admin():
            user = request.user
            query = f"""SELECT count(*), status from shoppingmall_order group by status;"""
            with connection.cursor() as cursor:
                cursor.execute(query)
                response = cursor.fetchall()
            quantity = []
            datas = {}
            data = {}
            for res in response:

                if res[1] == 'P':
                    data['pending'] = res[0]

                if res[1] == 'A':
                    data['accept'] = res[0]

            datas["status"] = data

            query = f"""SELECT count(*), delivery from shoppingmall_order where status='A' group by delivery;"""
            with connection.cursor() as cursor:
                cursor.execute(query)
                response = cursor.fetchall()

            data = {}
            for res in response:
                if res[1] == 'P':
                    data['preparing'] = res[0]

                if res[1] == 'S':
                    data['sent'] = res[0]
            datas["delivery"] = data

            return Response(datas, status=status.HTTP_200_OK)
        else:
            return Response({"error": ["Only admin have this rights"]}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def destroy(self, request, *args, **kwargs):
        response = {"error": ["Only admin can access"]}
        return Response(response, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        response = {"error": ["Only admin can access"]}
        return Response(response, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        response = {"error": ["Only admin can access"]}
        return Response(response, status=status.HTTP_404_NOT_FOUND)
