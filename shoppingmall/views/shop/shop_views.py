from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from shoppingmall.models import User, Shop, DeliveryPolicy
from rest_framework.permissions import AllowAny, IsAuthenticated

from shoppingmall.serializers import DeliveryPolicySerializer
from shoppingmall.serializers.shop_serializers import ShopSerializer, ShopReadSerializer, ShopConfigSerializer
from shoppingmall.serializers.users_serializers import SellerSerializer, MemberSerializer
from shoppingmall.utils.logger import Logger

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]

    """
    Create a model instance.
    """

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        if user.is_seller():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                self.perform_create(serializer)
            except Exception as err:
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id='', user_id=user.id, payload_string=str(err), status_code=400)
                return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
            headers = self.get_success_headers(serializer.data)
            response = serializer.data
            user.seller.shop = Shop.objects.get(id=response['id'])
            user.seller.save()
            Logger().d(data_string=data, method=request.method, path=request.path,
                       shop_id=response['id'], user_id=user.id, payload_string=response, status_code=201)
            return Response(response, status=status.HTTP_201_CREATED, headers=headers)
        else:
            data = {
                "organization": "Please create organization first"
            }
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id='', user_id=user.id, payload_string=data, status_code=400)
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def config(self, request, pk=None):
        user = request.user
        try:
            if user.is_seller():
                data = request.data
                shop = self.get_object()
                config = shop.config
                serializer = ShopConfigSerializer(config, data=data, partial=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                response = serializer.data
                headers = self.get_success_headers(serializer.data)
                Logger().d(data_string=data, method=request.method, path=request.path,
                           shop_id=pk, user_id=user.id, payload_string=response, status_code=201)
                return Response(response, status=status.HTTP_201_CREATED, headers=headers)
            else:
                data = {
                    "user": "the user is not seller"
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=pk, user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def delivery_policy(self, request, pk=None):
        user = request.user
        try:
            if user.is_seller():
                delivery_policy = request.data
                shop = self.get_object()
                response = []
                if delivery_policy:
                    try:
                        for policy in delivery_policy:
                            if 'id' in policy:
                                dp = DeliveryPolicy.objects.get(id=policy['id'])
                                optionSerializer = DeliveryPolicySerializer(dp, data=policy, partial=False)
                                optionSerializer.is_valid(True)
                                optionSerializer.save()
                            else:
                                policy['shop'] = pk
                                dps = DeliveryPolicy.objects.filter(shop=pk)
                                if len(dps) > 0:
                                    for dp in dps:
                                        if dp.unit_to < policy['unit_from']:
                                            optionSerializer = DeliveryPolicySerializer(data=policy)
                                            optionSerializer.is_valid(True)
                                            optionSerializer.save()
                                            response.append(optionSerializer.data)
                                        else:
                                            data = {
                                                "user": "Please check delivery policy type unit_from, unit_to"
                                            }
                                            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
                                else:
                                    optionSerializer = DeliveryPolicySerializer(data=policy)
                                    optionSerializer.is_valid(True)
                                    optionSerializer.save()
                                    response.append(optionSerializer.data)

                    except Exception as ex:
                        print(ex)
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=0, user_id=user.id, payload_string=response, status_code=200)
                return Response(response)
            else:
                data = {
                    "user": "the user is not seller"
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=pk, user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        try:
            instance = self.get_object()
            serializer = ShopReadSerializer(instance, context=self.get_serializer_context())
            response = serializer.data
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=kwargs['pk'], user_id=user.id, payload_string=response, status_code=200)
            return Response(serializer.data)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=kwargs['pk'], user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def member(self, request, pk=None):
        data = request.data
        user = request.user
        data['shop'] = pk
        serializer = MemberSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except Exception as err:
            Logger().d(data, 'POST', request.get_full_path, '', 0, str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        response = serializer.data
        Logger().d(data, 'POST', request.get_full_path, '', user.id, response, status_code=201)
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        user = request.user
        try:
            if user.is_authenticated and user.is_seller():
                queryset = Shop.objects.get(id=user.seller.shop.id)
                serializer = ShopReadSerializer(queryset, context=self.get_serializer_context())
                response = serializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=response['id'], user_id=user.id, payload_string=response, status_code=200)
                return Response(response)
            else:
                data = {
                    "user": "the user is not seller"
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"error": ["Only admins have this rights"]}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        user = request.user
        try:
            data = request.data
            delivery_policy = None
            if "delivery_policy" in data:
                delivery_policy = data.pop('delivery_policy')

            if delivery_policy:
                try:
                    for policy in delivery_policy:
                        dp = DeliveryPolicy.objects.get(id=policy['id'])
                        optionSerializer = DeliveryPolicySerializer(dp, data=policy, partial=False)
                        optionSerializer.is_valid(True)
                        optionSerializer.save()
                except Exception as ex:
                    print(ex)

            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = ShopSerializer(instance, data=data, partial=partial)
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
