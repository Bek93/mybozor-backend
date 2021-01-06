from django.db import connection

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shoppingmall.serializers.image_serializers import ImageSerializer
from ...models import ProductImages, Images, Product  # , BannerImage
from ...serializers.product_serializers import DailyOrderedProductSerializer, DashboardProductSerializer


class DashboardViewSet(viewsets.ModelViewSet):
    queryset = Images.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def my_custom_sql(self, sql):
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchall()

        return row

    @action(methods=['get'], detail=False)
    def monthly_profit(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            monthly_query = f"""SELECT 
               SUM(total_selling)                       as selling,
               SUM(total_buying)                        as buying,
               (SUM(total_selling) - SUM(total_buying)) as profit, SUM(total_referral_fee) as referral_fee, month
               FROM (SELECT total_selling, total_buying, total_referral_fee, to_char(date_created, 'YYYY-MM') as month, date_created
               from shoppingmall_order where deleted = false and shop_id='{shopId}' and status = 'A' OR status = 'S') as orders group by month order by month;
                """
            response = self.my_custom_sql(monthly_query)
            titles = ['selling', 'buying', 'profit', 'referral_fee', 'month']
            selling = []
            buying = []
            profit = []
            referral_fee = []
            month = []
            for res in response:
                for i, title in enumerate(titles):
                    if i == 0:
                        selling.append(res[i])
                    elif i == 1:
                        buying.append(res[i])
                    elif i == 2:
                        profit.append(res[i])
                    elif i == 3:
                        referral_fee.append(res[i])
                    elif i == 4:
                        month.append(res[i])

            data = {
                "month": month,
                "selling": selling,
                "buying": buying,
                "referral_fee": referral_fee,
                "profit": profit,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def daily_profit(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            daily_query = f"""SELECT SUM(total_selling)                       as selling,
           SUM(total_buying)                        as buying,
           (SUM(total_selling) - SUM(total_buying)) as profit,
           sana
    FROM (SELECT total_selling, total_buying, to_char(date_created, 'YYYY-MM-DD') as sana, date_created
          from shoppingmall_order
          where deleted = false and shop_id='{shopId}' and status = 'A'
             OR status = 'S' ) as orders where sana between to_char(now() - INTERVAL '30 days', 'YYYY-MM-DD') and 
             to_char(NOW(), 'YYYY-MM-DD') group by sana order by sana;
            """
            response = self.my_custom_sql(daily_query)
            titles = ['selling', 'buying', 'profit', 'days']
            quantity = []
            selling = []
            buying = []
            profit = []
            month = []
            for res in response:
                for i, title in enumerate(titles):
                    if i == 0:
                        selling.append(res[i])
                    elif i == 1:
                        buying.append(res[i])
                    elif i == 2:
                        profit.append(res[i])
                    elif i == 3:
                        month.append(res[i])

            data = {
                "days": month,
                "selling": selling,
                "buying": buying,
                "profit": profit,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def daily_order_count(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            query = f"""SELECT * FROM (SELECT COUNT(*) as quantity, to_char(date_created, 'YYYY-MM-DD') as sana
             from shoppingmall_order
             where deleted=false and shop_id='{shopId}' group by sana ) as orders where sana between to_char(now() - INTERVAL '30 days', 'YYYY-MM-DD') and 
             to_char(NOW(), 'YYYY-MM-DD') order by sana;
               """

            response = self.my_custom_sql(query)
            quantity = []
            days = []
            titles = ['count', 'date']
            for res in response:
                for i, title in enumerate(titles):
                    if i == 0:
                        quantity.append(res[i])
                    elif i == 1:
                        days.append(res[i])

            data = {
                "days": days,
                "quantity": quantity,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def monthly_order_count(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            query = f"""SELECT COUNT(*), to_char(date_created, 'YYYY-MM') as sana 
             from shoppingmall_order where deleted = false and shop_id='{shopId}' group by sana order by sana;
               """
            response = self.my_custom_sql(query)
            quantity = []
            days = []
            titles = ['count', 'date']
            for res in response:
                data = {}
                for i, title in enumerate(titles):
                    if i == 0:
                        quantity.append(res[i])
                    elif i == 1:
                        days.append(res[i])

            data = {
                "months": days,
                "quantity": quantity,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def order_count_by_status(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)

            query = f"""SELECT count(*), status from shoppingmall_order where deleted=false and shop_id='{shopId}' group by status;
                   """
            response = self.my_custom_sql(query)
            quantity = []
            days = []
            titles = ['count', 'status']
            for res in response:
                data = {}
                for i, title in enumerate(titles):
                    if i == 0:
                        quantity.append(res[i])
                    elif i == 1:
                        days.append(res[i])

            data = {
                "status": days,
                "quantity": quantity,
            }
            return Response(data, status=status.HTTP_200_OK)

        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def order_count_by_delivery_status(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            query = f"""SELECT count(*), delivery from shoppingmall_order where deleted=false and 
            shop_id='{shopId}' and delivery='P' or delivery='S' group by delivery;
                       """
            response = self.my_custom_sql(query)
            quantity = []
            days = []
            titles = ['count', 'delivery']
            for res in response:
                data = {}
                for i, title in enumerate(titles):
                    if i == 0:
                        quantity.append(res[i])
                    elif i == 1:
                        days.append(res[i])

            data = {
                "status": days,
                "quantity": quantity,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def live_time_popular_products(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            query = f"""SELECT SUM(quantity) as quantity, product_id
                from shoppingmall_orderedproduct where order_id in (Select id from shoppingmall_order where \
                shop_id='{shopId}') group by product_id order by quantity desc
               """
            response = self.my_custom_sql(query)
            titles = ["quantity", "product_id"]
            datas = []
            for res in response:
                data = {}
                for i, title in enumerate(titles):
                    data[title] = res[i]

                serializer = DailyOrderedProductSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                datas.append(serializer.data)
            return Response(datas, status=status.HTTP_200_OK)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def monthly_ordered_product(self, request, *args, **kwargs):

        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            query = """ SELECT * FROM (SELECT SUM(quantity) as quantity, product_id, to_char(date_created, 'YYYY-MM') as sana
                from shoppingmall_orderedproduct group by product_id) group by sana order by sana
                   """
            response = self.my_custom_sql(query)
            titles = ['quantity', 'product_id', 'date']
            datas = []
            for res in response:
                data = {}
                for i, title in enumerate(titles):
                    data[title] = res[i]

                datas.append(data)
            return Response(datas, status=status.HTTP_200_OK)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def monthly_total_referral_fee(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            query = f""" SELECT SUM(total_referral_fee), to_char(date_created, 'YYYY-MM') as sana
            FROM shoppingmall_order
            where shop_id = '{shopId}' group by sana;
                               """
            response = self.my_custom_sql(query)
            titles = ['total_referral_fee', 'month']
            datas = []
            for res in response:
                data = {}
                for i, title in enumerate(titles):
                    data[title] = res[i]

                datas.append(data)
            return Response(datas, status=status.HTTP_200_OK)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def daily_total_referral_fee(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            query = f""" SELECT SUM(total_referral_fee), to_char(date_created, 'YYYY-MM-DD') as sana
                FROM shoppingmall_order
                where shop_id = '{shopId}' group by sana;
                                   """
            response = self.my_custom_sql(query)
            titles = ['total_referral_fee', 'days']
            datas = []
            for res in response:
                data = {}
                for i, title in enumerate(titles):
                    data[title] = res[i]

                datas.append(data)
            return Response(datas, status=status.HTTP_200_OK)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def shop_view_count(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            query = f""" SELECT COUNT(*), to_char(date_created, 'YYYY-MM-DD') as sana
                    FROM shoppingmall_shopview
                    where shop_id = '{shopId}' group by sana;
                                       """
            response = self.my_custom_sql(query)
            titles = ['count', 'days']
            datas = []
            counts = []
            days = []
            for res in response:
                data = {}
                for i, title in enumerate(titles):
                    if i == 0:
                        counts.append(res[i])
                    elif i == 1:
                        days.append(res[i])

            data = {
                "counts": counts,
                "days": days
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def product_view_count_monthly(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            query = f""" SELECT * FROM (SELECT COUNT(*), to_char(date_created, 'YYYY-MM') as sana, product_id
                        FROM shoppingmall_productview
                        where shop_id = '{shopId}' group by sana, product_id) as product_view where sana between to_char(now() - INTERVAL '30 days', 'YYYY-MM-DD') and 
             to_char(NOW(), 'YYYY-MM-DD')
                                           """
            response = self.my_custom_sql(query)
            titles = ['count', 'days', 'product_id']
            counts = []
            products = []
            if len(response) > 0:

                for res in response:
                    data = {}
                    for i, title in enumerate(titles):

                        if title == 'days':
                            print(res[i])
                        elif title == 'count':
                            counts.append(res[i])
                        elif title == 'product_id':
                            product = Product.objects.get(id=res[i])
                            products.append(DashboardProductSerializer(product,
                                                                       context=self.get_serializer_context()).data)

            data = {
                "counts": counts,
                "products": products
            }
            return Response(data, status=status.HTTP_200_OK)

        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
