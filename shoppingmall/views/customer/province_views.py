from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from shoppingmall.models import Collection, Product, CollectionImages, Logs, Province
from shoppingmall.serializers import LocalizeSerializer, ProvinceSerializer
from shoppingmall.serializers.collection_serializers import CollectionSerializer, CategorySerializer, \
    CollectionAdminSerializer
from shoppingmall.serializers.image_serializers import CollectionImagesSerializer
from shoppingmall.serializers.product_serializers import ProductReadSerializer
from shoppingmall.utils.logger import Logger


class ProvinceViewSet(viewsets.ModelViewSet):
    serializer_class = ProvinceSerializer
    pagination_class = None
    logger = Logs()

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.is_admin():
            datas = request.data
            responses = []
            for data in datas:
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                try:
                    self.perform_create(serializer)
                except Exception as err:
                    Logger().d(data_string='', method=request.method, path=request.path,
                               shop_id='', user_id=0, payload_string=str(err), status_code=400)
                    return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

                response = serializer.data
                Logger().d(data_string=data, method=request.method, path=request.path,
                           shop_id=response['id'], user_id=user.id, payload_string=response, status_code=201)
                responses.append(data)

            return Response(responses, status=status.HTTP_201_CREATED)
        else:
            data = {
                "user": "Only admins can create"
            }
            return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        user = request.user
        if user.is_admin():
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = ProvinceSerializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                response = serializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=kwargs['pk'], user_id=user.id, payload_string=response, status_code=200)
                return Response(serializer.data)
            except Exception as err:
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=kwargs['pk'], user_id=user.id, payload_string=str(err), status_code=400)
                return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {
                "user": "Only admins can create"
            }
            return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = Province.objects.all().order_by('pk')
        serializer = ProvinceSerializer(queryset, context=self.get_serializer_context(), many=True)
        response = serializer.data
        Logger().d(data_string='', method=request.method, path=request.path,
                   shop_id='', user_id=user.id, payload_string=response, status_code=200)
        return Response(response)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return [AllowAny(), ]
        if self.action == 'create' or self.action == 'update' or self.action == 'destroy':
            print(self.action, self.request.user)
            return [IsAuthenticated(), ]
        return super(ProvinceViewSet, self).get_permissions()
