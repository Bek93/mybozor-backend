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
        data = request.data
        user = request.user
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            data['shop'] = shopId
            # images = req.pop("images")
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            try:
                self.perform_create(serializer)
            except Exception as err:
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=shopId, user_id=user.id, payload_string=str(err), status_code=400)
                return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
            response = serializer.data
            Logger().d(data_string=data, method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=201)
            return Response(response, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        user = request.user
        try:
            instance = self.get_object()
            data = request.data

            images = []
            if 'images' in data:
                images = data.pop("images")

            for image in images:
                if not str(image['image']).startswith('http'):
                    image['product'] = instance.pk
                    image['shop'] = instance.shop.pk
                    image = ProductImageSerializer(data=image)
                    image.is_valid(True)
                    image.save()

            options = []
            if 'options' in data:
                options = data.pop("options")

            if options:
                for option in options:
                    try:
                        if 'id' in option:
                            optionObject = Options.objects.get(id=option['id'])
                            values = option.pop("values")
                            optionSerializer = OptionSerializer(optionObject, data=option, partial=False)
                            optionSerializer.is_valid(True)
                            optionSerializer.save()

                            for value in values:
                                if 'id' in value:
                                    valueObject = OptionValue.objects.get(id=value['id'])
                                    optionValueSerializer = OptionValueSerializer(valueObject, data=value,
                                                                                  partial=False)
                                    optionValueSerializer.is_valid(True)
                                    optionValueSerializer.save()
                                else:
                                    value['option'] = option
                                    valueObject = OptionValue.objects.create(**value)
                                    valueObject.save()
                        else:
                            option['product'] = instance
                            values = option.pop("values")
                            optionObject = Options.objects.create(**option)
                            optionObject.save()
                            for value in values:
                                value['option'] = optionObject
                                valueObject = OptionValue.objects.create(**value)
                                valueObject.save()

                    except ValidationError as err:
                        raise ValidationError(err)

            serializer = ProductCreateSerializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            response = serializer.data
            Logger().d(data_string=data, method=request.method, path=request.path,
                       shop_id=response['shop'], user_id=user.id, payload_string=response, status_code=200)
            return Response(request.data)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=kwargs['pk'], user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user
        query_params = request.query_params
        if user.is_seller():
            shopId = str(user.seller.shop.id)
            is_active = None
            if 'active' in query_params:
                is_active = query_params['active'] == 'true'
            try:

                if user.is_seller():
                    if is_active is None:
                        queryset = Product.objects.all().filter(shop=shopId).order_by("pk")
                    else:
                        queryset = Product.objects.all().filter(shop=shopId, is_active=is_active).order_by("pk")
                    page = self.paginate_queryset(queryset)
                    if page is not None:
                        serializer = ProductReadSerializer(page, context=self.get_serializer_context(), many=True)
                        response = serializer.data
                        Logger().d(data_string='', method=request.method, path=request.path,
                                   shop_id=shopId, user_id=user.id, payload_string=response, status_code=200)
                        return self.get_paginated_response(serializer.data)
                    serializer = ProductReadSerializer(queryset, context=self.get_serializer_context(), many=True)
                    response = serializer.data
                    Logger().d(data_string='', method=request.method, path=request.path,
                               shop_id=shopId, user_id=user.id, payload_string=response, status_code=200)
                    return Response(serializer.data)
            except Exception as err:
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=shopId, user_id=user.id, payload_string=str(err), status_code=400)
                return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {
                "users": "Online seller can access the endpoint"
            }
            return Response(data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        try:
            if request.user.is_seller():
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
