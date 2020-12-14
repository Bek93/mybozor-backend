from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from shoppingmall.models import Collection, Product, CollectionImages, Logs
from shoppingmall.serializers import LocalizeSerializer
from shoppingmall.serializers.collection_serializers import CollectionSerializer, CategorySerializer, \
    CollectionAdminSerializer
from shoppingmall.serializers.image_serializers import CollectionImagesSerializer
from shoppingmall.serializers.product_serializers import ProductReadSerializer
from shoppingmall.utils.logger import Logger


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionAdminSerializer
    pagination_class = None
    logger = Logs()

    def get_serializer_context(self):
        user = self.request.user
        language = "uz"
        if user.is_authenticated and user.is_customer():
            language = user.customer.language
        if 'lang' in self.request.query_params:
            language = self.request.query_params['lang']
        return {"language": language, "request": self.request}

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True)
    def products(self, request, pk=None):
        category = self.get_object()
        user = request.user
        if user.is_customer():
            try:
                items = Product.objects.filter(category=category, is_active=True).distinct().order_by('pk')
                productReadSerializer = ProductReadSerializer(items, many=True, context=self.get_serializer_context())
                response = productReadSerializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=category.shop.id, user_id=user.id, payload_string=response, status_code=200)
                return Response(response)
            except Exception as err:
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=category.shop.id, user_id=user.id, payload_string=str(err), status_code=400)
                return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {
                "error": "Only customer is allowed method"
            }
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=category.shop.id, user_id=user.id, payload_string=data, status_code=400)
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def images(self, request, pk=None):
        serializer = CollectionImagesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        user = request.user
        if 'shopId' in request.query_params:
            shopId = request.query_params['shopId']

            try:
                user = request.user
                if user.is_authenticated and user.is_customer():
                    queryset = Collection.objects.all().filter(shop=shopId, is_active=True).order_by('pk')
                    serializer = CollectionAdminSerializer(queryset, context=self.get_serializer_context(), many=True)
                    response = serializer.data
                    Logger().d(data_string='', method=request.method, path=request.path,
                               shop_id=shopId, user_id=user.id, payload_string=response, status_code=200)
                    return Response(response)
                data = {
                    "shopId": "Please sent the fields..."
                }
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=0, user_id=user.id, payload_string=data, status_code=400)
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            except Exception as err:
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=shopId, user_id=user.id, payload_string=str(err), status_code=400)
                return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {
                "shopId": "Please sent the fields..."
            }
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=data, status_code=400)
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve' or self.action == 'products':
            return [IsAuthenticated(), ]
        if self.action == 'create' or self.action == 'update' or self.action == 'destroy':
            print(self.action, self.request.user)
            return [IsAuthenticated(), ]
        return super(CollectionViewSet, self).get_permissions()
