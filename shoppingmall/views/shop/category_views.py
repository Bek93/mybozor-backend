from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from shoppingmall.models import Collection, Product, CollectionImages, Logs, Category, Subproduct
from shoppingmall.serializers import LocalizeSerializer
from shoppingmall.serializers.collection_serializers import CollectionSerializer, CategorySerializer, \
    ReadCategorySerializer, ReadSubproductSerializer
from shoppingmall.serializers.product_serializers import ProductReadSerializer
from shoppingmall.utils.logger import Logger


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = ReadCategorySerializer
    pagination_class = None
    logger = Logs()

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True)
    def products(self, request, pk=None):
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            try:
                category = Category.objects.get(id=int(pk))  # retrieve an object by pk provided
                items = Product.objects.filter(category=category.pk).distinct().order_by('pk')
                productReadSerializer = ProductReadSerializer(items, many=True, context=self.get_serializer_context())
                response = productReadSerializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=shopId, user_id=user.id, payload_string=response, status_code=200)
                return Response(response)
            except Exception as err:
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=shopId, user_id=user.id, payload_string=str(err), status_code=400)
                return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {
                "user": "Only sellers can access the endpoint"
            }
            return Response(data)

    @action(detail=True)
    def subproduct(self, request, pk=None):
        user = request.user
        try:
            queryset = Subproduct.objects.all().filter(is_active=True, category=pk).order_by('pk')
            user = request.user
            if user.is_authenticated and user.is_admin():
                queryset = Subproduct.objects.all().order_by('pk')
                serializer = ReadSubproductSerializer(queryset, context=self.get_serializer_context(), many=True)

            else:
                serializer = ReadSubproductSerializer(queryset, context=self.get_serializer_context(), many=True)
            response = serializer.data
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id="", user_id=user.id, payload_string=response, status_code=200)
            return Response(response)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id="", user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user
        try:
            queryset = Category.objects.all().filter(is_active=True, parent_id='0').order_by('pk')
            user = request.user
            if user.is_authenticated and user.is_admin():
                queryset = Category.objects.all().filter(is_active=True, parent_id='0').order_by('pk')
                serializer = ReadCategorySerializer(queryset, context=self.get_serializer_context(), many=True)

            else:
                serializer = ReadCategorySerializer(queryset, context=self.get_serializer_context(), many=True)
            response = serializer.data
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id="", user_id=user.id, payload_string=response, status_code=200)
            return Response(response)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id="", user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve' or self.action == 'products':
            return [IsAuthenticated(), ]
        if self.action == 'create' or self.action == 'update' or self.action == 'destroy':
            print(self.action, self.request.user)
            return [IsAuthenticated(), ]
        return super(CategoryViewSet, self).get_permissions()
