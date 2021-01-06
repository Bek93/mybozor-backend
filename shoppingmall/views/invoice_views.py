import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from shoppingmall.models import Invoice, Order
from shoppingmall.serializers.order_serializers import InvoiceSerializer, OrderSerializer
from shoppingmall.utils.logger import Logger

from pytz import timezone

seoul = timezone('Asia/Seoul')


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        try:
            user = request.user
            if user.is_authenticated and user.is_admin():
                queryset = Invoice.objects.all().order_by('pk')
                serializer = InvoiceSerializer(queryset, context=self.get_serializer_context(), many=True)
                response = serializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id="", user_id=user.id, payload_string=response, status_code=200)
                return Response(response, status=status.HTTP_200_OK)
            elif user.is_seller():
                queryset = Invoice.objects.filter(shop=user.seller.shop)
                serializer = InvoiceSerializer(queryset, context=self.get_serializer_context(), many=True)
                response = serializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id="", user_id=user.id, payload_string=response, status_code=200)
                return Response(response)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id="", user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def current(self, request, pk=None):
        todayDataTime = datetime.datetime.now(seoul)
        month = todayDataTime.strftime('%Y-%m')
        user = request.user
        if user.is_seller():
            try:
                invoice = Invoice.objects.get(month=month, shop=user.seller.shop.id)
            except ObjectDoesNotExist as ex:
                print(ex)
                invoice = Invoice(month=month, shop=user.seller.shop.id)
                invoice.save()
            response = InvoiceSerializer(invoice, context=self.get_serializer_context()).data
            return Response(response, status=status.HTTP_200_OK)
        elif user.is_admin():
            query_params = request.query_params
            if 'shopId' in query_params:
                shopId = query_params['shopId']
                invoice = Invoice.objects.get(month=month, shop=shopId)
            else:
                invoice = Invoice.objects.filter(month=month)
            response = InvoiceSerializer(invoice, context=self.get_serializer_context()).data
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response({"error": ["Only admins have this rights"]}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(methods=['get'], detail=True)
    def orders(self, request, pk=None):
        user = request.user
        if user.is_seller() or user.is_admin():
            query = f"""SELECT total_selling, total_referral_fee, order_number, name, id from shoppingmall_order where invoice_id={pk}"""
            response = self.my_custom_sql(query)

            titles = ['total_selling', 'total_referral_fee', 'order_number', 'name', 'id']
            datas = []
            for res in response:
                data = {}
                for i, title in enumerate(titles):
                    data[title] = res[i]

                datas.append(data)
            return Response(datas, status=status.HTTP_200_OK)
        else:
            return Response({"error": ["Only admins have this rights"]}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(methods=['get'], detail=True)
    def overview(self, request, pk=None):
        user = request.user
        if user.is_seller() or user.is_admin():
            query = f"""SELECT SUM(total_selling), SUM(total_referral_fee), COUNT(*)from shoppingmall_order where invoice_id={pk}"""
            response = self.my_custom_sql(query)
            total_referral_fee = 0
            total_selling = 0
            count = 0
            if len(response) > 0:
                row = response[0]
                total_selling = row[0]
                total_referral_fee = row[1]
                count = row[2]

            data = {
                "total_selling": total_selling,
                "total_referral_fee": total_referral_fee,
                "count": count
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": ["Only admins have this rights"]}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def my_custom_sql(self, sql):
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchall()

        return row
