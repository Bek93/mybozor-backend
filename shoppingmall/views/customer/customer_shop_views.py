from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from shoppingmall.models import User, Shop
from rest_framework.permissions import AllowAny, IsAuthenticated

from shoppingmall.serializers.shop_serializers import ShopSerializer
from shoppingmall.utils.logger import Logger

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class CustomerShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]

    """
    Create a model instance.
    """

    def get_serializer_context(self):
        user = self.request.user
        language = 'uz'
        if user.is_authenticated and user.is_customer():
            language = user.customer.language

        return {"language": language, 'is_customer': user.is_customer(), "request": self.request}

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        try:
            instance = self.get_object()
            serializer = ShopSerializer(instance, context=self.get_serializer_context())
            response = serializer.data
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=kwargs['pk'], user_id=user.id, payload_string=response, status_code=200)
            return Response(serializer.data)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=kwargs['pk'], user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        print("start")
        user = request.user
        try:
            if user.is_authenticated and user.is_customer():
                queryset = Shop.objects.all().filter(status='approved').order_by('pk')
                serializer = ShopSerializer(queryset, context=self.get_serializer_context(), many=True)
                response = serializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=0, user_id=user.id, payload_string=response, status_code=200)
                return Response(response)
            else:
                data = {
                    "user": "the user is not seller"
                }
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id=0, user_id=user.id, payload_string=data, status_code=400)
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            print(err)
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
