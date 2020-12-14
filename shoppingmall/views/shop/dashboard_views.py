from django.db import connection

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shoppingmall.serializers.image_serializers import ImageSerializer
from ...models import ProductImages, Images  # , BannerImage
from ...serializers.product_serializers import DailyOrderedProductSerializer


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
            query_params = request.query_params
            if 'shopId' in query_params:
                monthly_query = f"""SELECT 
               SUM(total_selling)                       as selling,
               SUM(total_buying)                        as buying,
               (SUM(total_selling) - SUM(total_buying)) as profit, month
               FROM (SELECT total_selling, total_buying, to_char(date_created, 'YYYY-MM') as month, date_created
               from shoppingmall_order where deleted = false and shop_id='{query_params['shopId']}' and status = 'A' OR status = 'S') as orders group by month order by month;
                """
                response = self.my_custom_sql(monthly_query)
                titles = ['selling', 'buying', 'profit', 'month']
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
                    "month": month,
                    "selling": selling,
                    "buying": buying,
                    "profit": profit,
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                data = {
                    "shopId": "Please sent the fields..."
                }
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def daily_profit(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            query_params = request.query_params
            if 'shopId' in query_params:
                daily_query = f"""SELECT SUM(total_selling)                       as selling,
               SUM(total_buying)                        as buying,
               (SUM(total_selling) - SUM(total_buying)) as profit,
               sana
        FROM (SELECT total_selling, total_buying, to_char(date_created, 'YYYY-MM-DD') as sana, date_created
              from shoppingmall_order
              where deleted = false and shop_id='{query_params['shopId']}' and status = 'A'
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
                    "shopId": "Please sent the fields..."
                }
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def daily_order_count(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            query_params = request.query_params
            if 'shopId' in query_params:
                query = f"""SELECT * FROM (SELECT COUNT(*) as quantity, to_char(date_created, 'YYYY-MM-DD') as sana
                 from shoppingmall_order
                 where deleted=false and shop_id='{query_params['shopId']}' group by sana ) as orders where sana between to_char(now() - INTERVAL '30 days', 'YYYY-MM-DD') and 
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
                    "shopId": "Please sent the fields..."
                }
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def monthly_order_count(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            query_params = request.query_params
            if 'shopId' in query_params:

                query = f"""SELECT COUNT(*), to_char(date_created, 'YYYY-MM') as sana 
                 from shoppingmall_order where deleted = false and shop_id='{query_params['shopId']}' group by sana order by sana;
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
                    "shopId": "Please sent the fields..."
                }
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def order_count_by_status(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            query_params = request.query_params
            if 'shopId' in query_params:

                query = f"""SELECT count(*), status from shoppingmall_order where deleted=false and shop_id='{query_params['shopId']}' group by status;
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
                    "shopId": "Please sent the fields..."
                }
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def order_count_by_delivery_status(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            query_params = request.query_params
            if 'shopId' in query_params:
                query = f"""SELECT count(*), delivery from shoppingmall_order where deleted=false and 
                shop_id='{query_params['shopId']}' and delivery='P' or delivery='S' group by delivery;
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
                    "shopId": "Please sent the fields..."
                }
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def live_time_popular_products(self, request, *args, **kwargs):
        user = request.user
        if user.is_seller():
            query_params = request.query_params
            if 'shopId' in query_params:
                query = f"""SELECT SUM(quantity) as quantity, product_id
                    from shoppingmall_orderedproduct where order_id in (Select id from shoppingmall_order where \
                    shop_id='{query_params['shopId']}') group by product_id order by quantity desc
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
                    "shopId": "Please sent the fields..."
                }
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data = {
                "user": "Please sent the fields..."
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], detail=False)
    def monthly_ordered_product(self, request, *args, **kwargs):
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
