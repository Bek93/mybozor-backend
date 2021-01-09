from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from shoppingmall.serializers.product_serializers import ProductCreateSerializer, ProductReadSerializer
from ...models import Product, Options, OptionValue
from ...serializers import OptionSerializer, OptionValueSerializer
from ...serializers.image_serializers import ProductImageSerializer
from ...utils.logger import Logger


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        user = request.user
        query_params = request.query_params
        if user.is_admin():
            is_active = None
            if 'active' in query_params:
                is_active = query_params['active'] == 'true'
            try:

                if user.is_admin():
                    if is_active is None:
                        queryset = Product.objects.all().order_by("pk")
                    else:
                        queryset = Product.objects.all().filter(is_active=is_active).order_by("pk")
                    page = self.paginate_queryset(queryset)
                    if page is not None:
                        serializer = ProductReadSerializer(page, context=self.get_serializer_context(), many=True)
                        response = serializer.data
                        Logger().d(data_string='', method=request.method, path=request.path,
                                   shop_id="", user_id=user.id, payload_string=response, status_code=200)
                        return self.get_paginated_response(serializer.data)
                    serializer = ProductReadSerializer(queryset, context=self.get_serializer_context(), many=True)
                    response = serializer.data
                    Logger().d(data_string='', method=request.method, path=request.path,
                               shop_id="", user_id=user.id, payload_string=response, status_code=200)
                    return Response(serializer.data)
            except Exception as err:
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id="", user_id=user.id, payload_string=str(err), status_code=400)
                return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {
                "users": "Only admin can access the endpoint"
            }
            return Response(data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        try:
            if request.user.is_admin():
                instance = self.get_object()
                serializer = ProductReadSerializer(instance, context=self.get_serializer_context())
                response = serializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=0, user_id=user.id, payload_string=response, status_code=200)
                return Response(serializer.data)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve' or self.action == 'new':
            return [AllowAny(), ]
        if self.action == 'create' or self.action == 'update' or self.action == 'destroy':
            return [IsAuthenticated(), ]
        return super(ProductViewSet, self).get_permissions()
