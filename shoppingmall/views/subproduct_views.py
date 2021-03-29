from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from shoppingmall.models import Collection, Product, CollectionImages, Logs, Category, Subproduct
from shoppingmall.serializers import LocalizeSerializer
from shoppingmall.serializers.collection_serializers import CollectionSerializer, CategorySerializer, \
    SubproductSerializer, ReadSubproductSerializer
from shoppingmall.serializers.product_serializers import ProductReadSerializer
from shoppingmall.utils.logger import Logger


class SubproductViewSet(viewsets.ModelViewSet):
    queryset = Subproduct.objects.all()
    serializer_class = SubproductSerializer
    pagination_class = None
    logger = Logs()

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        if user.is_admin():
            serializer = SubproductSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            response = serializer.data
            headers = self.get_success_headers(data)
            Logger().d(data_string=data, method=request.method, path=request.path,
                       shop_id=response['id'], user_id=user.id, payload_string=response, status_code=201)
            return Response(response, status=status.HTTP_201_CREATED, headers=headers)
        else:
            data = {
                "message": "Only admins can create subproduct"
            }
            return Response(data)

    def update(self, request, *args, **kwargs):
        user = request.user
        if user.is_admin():
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                data = request.data
                if 'titles' in data:
                    titles = data.pop('titles')
                    titleSerializer = LocalizeSerializer(instance.titles, data=titles, partial=False)
                    titleSerializer.is_valid(True)
                    titleSerializer.save()

                serializer = SubproductSerializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
                response = serializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=kwargs['pk'], user_id=user.id, payload_string=response, status_code=200)
                return Response(request.data)
            except Exception as err:
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=kwargs['pk'], user_id=user.id, payload_string=str(err), status_code=400)
                return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {
                "message": "Only admins can update subproduct"
            }
            return Response(data)

    @action(detail=True)
    def products(self, request, pk=None):
        user = request.user
        try:
            items = Product.objects.filter(subproduct=pk, is_approved=True).distinct().order_by('pk')
            productReadSerializer = ProductReadSerializer(items, many=True, context=self.get_serializer_context())
            response = productReadSerializer.data
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id="shopId", user_id=user.id, payload_string=response, status_code=200)
            return Response(response)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id="shopId", user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user
        try:
            queryset = Subproduct.objects.all().filter(is_active=True).order_by('pk')
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

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve' or self.action == 'products':
            return [IsAuthenticated(), ]
        if self.action == 'create' or self.action == 'update' or self.action == 'destroy':
            print(self.action, self.request.user)
            return [IsAuthenticated(), ]
        return super(SubproductViewSet, self).get_permissions()
