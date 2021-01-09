from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from shoppingmall.models import User, Shop, DeliveryPolicy
from rest_framework.permissions import AllowAny, IsAuthenticated

from shoppingmall.serializers import DeliveryPolicySerializer
from shoppingmall.serializers.shop_serializers import ShopSerializer, ShopReadSerializer, ShopConfigSerializer
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
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

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

    def list(self, request, *args, **kwargs):
        user = request.user
        try:
            if user.is_authenticated and user.is_admin():

                queryset = Shop.objects.all().order_by('-status')
                serializer = ShopReadSerializer(queryset, context=self.get_serializer_context(), many=True)
                response = serializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=0, user_id=user.id, payload_string=response, status_code=200)
                return Response(response, status=status.HTTP_200_OK)
            else:
                data = {
                    "user": "the user is not admin"
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        data = request.data
        user = request.user
        if user.is_admin():
            instance = self.get_object()
            instance.status = "approved"
            instance.save()
            response = ShopReadSerializer(instance, context=self.get_serializer_context()).data
            Logger().d(data, 'POST', request.get_full_path, '', user.id, response, status_code=201)
            return Response(response, status=status.HTTP_200_OK)
        else:
            data = {
                "user": "the user is not admin"
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

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
