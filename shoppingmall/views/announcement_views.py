from django.db import connection
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from shoppingmall.models import Category, Announcement, Customer, Filter
from shoppingmall.serializers.announcement_serializers import AnnouncementSerializer
from shoppingmall.serializers.users_serializers import CustomerSerializer
from shoppingmall.utils.logger import Logger
from shoppingmall.tasks import send_announcements


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        if user.is_seller():
            serializer = AnnouncementSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            response = serializer.data
            headers = self.get_success_headers(data)
            Logger().d(data_string=data, method=request.method, path=request.path,
                       shop_id=response['id'], user_id=user.id, payload_string=response, status_code=201)

            # send_announcements.delay(response['id'])
            return Response(data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def my_custom_sql(self, sql):
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchall()

        return row

    @action(detail=True, methods=['post'])
    def filter(self, request, pk=None):
        data = request.data
        user = request.user
        if user.is_seller():
            instance = self.get_object()
            filter = Filter.objects.create(**data)
            instance.filter = filter
            instance.save()
            headers = self.get_success_headers(data)
            send_announcements.delay(instance.id)
            return Response(data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False)
    def customer_filter(self, request, pk=None):
        user = request.user
        try:
            params = request.query_params
            if user.is_authenticated and user.is_seller():
                query_params = ''
                if 'province' in params:
                    if len(query_params) > 0:
                        query_params += " and "
                    query_params += " province_id=" + params['province']
                if 'language' in params:
                    if len(query_params) > 0:
                        query_params += " and "
                    query_params += f" language='{params['language']}'"
                if 'gender' in params:
                    if len(query_params) > 0:
                        query_params += " and "
                    query_params += f" gender='{params['gender']}'"

                if len(query_params) > 0:
                    query_params = "where " + query_params

                query = f"""SELECT count(*) as customer_count from shoppingmall_customer
                  {query_params}"""

                result = self.my_custom_sql(query)
                row = result[0]
                response = {
                    "customer_count": row[0]
                }

                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id="", user_id=user.id, payload_string=response, status_code=200)
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id="", user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve' or self.action == 'products' or self.action == 'create' or self.action == 'update' or self.action == 'destroy':
            return [IsAuthenticated(), ]
        return super(AnnouncementViewSet, self).get_permissions()
