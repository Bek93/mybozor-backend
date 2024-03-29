import datetime
import json
import os

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shoppingmall.models import Order, Product, Options, Shop, OrderedProduct
from shoppingmall.serializers.order_serializers import OrderSerializer, OrderedProductSerializer
from firebase_notify import FirebaseNotify
from shoppingmall.serializers.shop_serializers import ShopReadSerializer
from shoppingmall.utils.config import getNewOrderNumber
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

    def retrieve(self, request, *args, **kwargs):

        user = request.user
        if user.is_seller():
            instance = self.get_object()
            serializer = OrderSerializer(instance, context=self.get_serializer_context())
            response = serializer.data
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=response['shop'], user_id=user.id, payload_string=response, status_code=200)
            return Response(response)
        else:
            response = {"error": ["Only customer can access"]}
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=403)
            return Response(response, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False)
    def history(self, request, pk=None):
        user = request.user
        if user.is_seller():
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
        if user.is_seller():
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
        user = request.user.seller
        if user.is_seller():
            data = request.data
            data['user'] = user.pk
            shop = Shop.objects.get(id=data['shop'])
            shop = ShopReadSerializer(shop, context=self.get_serializer_context()).data
            products = data.pop('products')
            serializer = OrderSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            data = serializer.data
            order = Order.objects.get(id=data['id'])
            savedProductCount = 0
            total_selling = 0
            total_buying = 0
            total_referral_fee = 0
            quantity_amount = 0
            for product in products:
                try:
                    rProduct = Product.objects.get(pk=product['product_id'])
                    if str(rProduct.shop.id) == shop['id']:
                        orderedProduct = OrderedProduct(order=order, product=rProduct,
                                                        quantity=product['quantity'],
                                                        buying=rProduct.buying,
                                                        selling=rProduct.selling,
                                                        referral_fee=rProduct.referral_fee
                                                        )
                        orderedProduct.save()
                        total_buying += rProduct.buying * product['quantity']
                        total_selling += rProduct.selling * product['quantity']
                        total_referral_fee += rProduct.referral_fee * product['quantity']
                        quantity_amount += product['quantity']
                        savedProductCount = savedProductCount + 1
                except Exception as ex:
                    print(ex)
                    continue

            if savedProductCount == 0:
                order.delete()
                data = {
                    "message": "Product is over"
                }
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

            delivery_policy = shop['delivery_policy']
            delivery_fee = 0
            for policy in delivery_policy:
                if policy['unit_from'] < quantity_amount <= policy['unit_to']:
                    delivery_fee = policy['fee']
            order.total_buying = total_buying
            order.total_selling = total_selling
            order.delivery_fee = delivery_fee
            order.total_referral_fee = total_referral_fee

            order.order_number = getNewOrderNumber(order.id)
            order.save()
            order_serializer = OrderSerializer(order, context=self.get_serializer_context())
            headers = self.get_success_headers(order_serializer.data)
            response = order_serializer.data
            response['shop'] = shop

            # tlg = TelegramNotify()
            # try:
            #     tlg.send_new_order(data)
            # except:
            #     pass
            # try:
            #     tlg.send_sms_to_customer(data)
            # except:
            #     pass

            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=shop['id'], user_id=user.id, payload_string=response, status_code=200)

            return Response(data, status=status.HTTP_201_CREATED, headers=headers)

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
        if user.is_seller():
            query_params = request.query_params
            if 'shopId' in query_params:
                shopId = query_params['shopId']
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

                queryset = Order.objects.filter(shop=shopId)
                if from_date and to_date:
                    queryset = queryset.filter(date_created__date__range=[from_date, to_date])
                if payment:
                    queryset = queryset.filter(payment=payment)

                if statusOrder:
                    queryset = queryset.filter(status=statusOrder)
                queryset = queryset.order_by('-date_created')
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = OrderSerializer(page, context=self.get_serializer_context(), many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = OrderSerializer(queryset, context=self.get_serializer_context(), many=True)
                return Response(serializer.data)
            else:
                data = {
                    "shopId": "Please sent the fields..."
                }
                return Response(data)
        else:
            response = {"error": ["Only customer can access"]}
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=403)
            return Response(response, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['post'], detail=True)
    def approve(self, request, pk=None):
        if request.user.is_seller():
            obj = self.get_object()
            obj.status = 'A'
            obj.posting_date = self.getDeliveryDate()
            obj.save()
            try:
                obj_ser = OrderSerializer(obj, context=self.get_serializer_context()).data
                for orderedProduct in obj_ser['products']:
                    rProduct = Product.objects.get(pk=orderedProduct['product']['id'])
                    if rProduct.overable:
                        if rProduct.quantity >= orderedProduct["quantity"]:
                            rProduct.quantity -= orderedProduct["quantity"]
                            rProduct.save()

                        if rProduct.has_option:
                            if orderedProduct['option']:
                                option = Options.objects.get(pk=orderedProduct['option'])
                                if option.quantity >= orderedProduct["quantity"]:
                                    option.quantity -= orderedProduct["quantity"]
                                    option.save()
                        else:
                            continue

                # tlg.send_order_accepted_message(obj_ser_kr, obj_ser)
            except Exception as ex:
                print(ex)
                pass
            return Response({"Approved"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": ["Only admins have this rights"]}, status=status.HTTP_406_NOT_ACCEPTABLE)

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

    @action(methods=['post'], detail=True)
    def paid(self, request, pk=None):
        if request.user.is_seller():
            obj = self.get_object()
            obj.payment = 'paid'
            obj.save()
            obj_ser = OrderSerializer(obj, context=self.get_serializer_context()).data
            if obj_ser['type'] == 'T':
                try:
                    tlg = TelegramNotify()
                    # tlg.send_order_paid_message_to_users(obj_ser)
                except Exception as ex:
                    print(ex)
                    pass
            elif obj_ser['type'] == 'A':
                fcm = FirebaseNotify()
                # fcm.send_order_paid_message_to_users(obj_ser)

            return Response({"PAID"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": ["Only admins have this rights"]}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(methods=['post'], detail=True)
    def sent(self, request, pk=None):
        if request.user.is_staff:
            obj = self.get_object()
            obj.status = 'S'
            todayDataTime = datetime.datetime.now(seoul)
            todayDataTime = todayDataTime + datetime.timedelta(days=1)
            day = todayDataTime.strftime('%d-%m-%Y')

            obj.arrivingDate = day
            if 'post_code' in request.data:
                post_number = request.data['post_code']
                obj.post_code = post_number
            obj.save()

            return Response({"Sent"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": ["Only admins have this rights"]}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(methods=['post'], detail=True)
    def sent_and_notify(self, request, pk=None):
        if request.user.is_staff:
            obj = self.get_object()
            obj.status = 'S'
            todayDataTime = datetime.datetime.now(seoul)
            todayDataTime = todayDataTime + datetime.timedelta(days=1)
            day = todayDataTime.strftime('%d-%m-%Y')

            obj.arrivingDate = day
            if 'post_number' in request.query_params:
                post_number = request.query_params['post_number']
                obj.post_code = post_number
            obj.save()
            language = obj.language
            context = {"language": language, "request": self.request}
            obj_ser = OrderSerializer(obj, context=context).data

            if obj_ser['type'] == 'T':
                try:
                    tlg = TelegramNotify()
                    tlg.send_order_sent_message(obj_ser)
                except Exception as ex:
                    print(ex)
                    pass
            return Response({"Sent"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": ["Only admins have this rights"]}, status=status.HTTP_406_NOT_ACCEPTABLE)
