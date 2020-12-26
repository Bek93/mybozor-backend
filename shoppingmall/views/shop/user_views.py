from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from shoppingmall.models import User, Seller
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from django.utils.crypto import get_random_string

from shoppingmall.utils.logger import Logger

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

from shoppingmall.serializers.users_serializers import SellerSerializer


class ShopUserViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        try:
            user = request.user
            if user.is_authenticated and user.is_admin():
                queryset = Seller.objects.all().order_by('pk')
                serializer = SellerSerializer(queryset, context=self.get_serializer_context(), many=True)
                response = serializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id="", user_id=user.id, payload_string=response, status_code=200)
                return Response(response)
            else:

                queryset = Seller.objects.filter(organization=user.seller.organization)
                serializer = SellerSerializer(queryset, context=self.get_serializer_context(), many=True)
                response = serializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id="", user_id=user.id, payload_string=response, status_code=200)
                return Response(response)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id="", user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    """
    Create a model instance.
    """

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except Exception as err:
            Logger().d(data, 'POST', request.get_full_path, '', 0, str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        response = serializer.data
        user = User.objects.get(id=response["id"])
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        response['token'] = token
        Logger().d(data, 'POST', request.get_full_path, '', user.id, response, status_code=201)
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = SellerSerializer(instance, context=self.get_serializer_context())
        return Response(serializer.data)

    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = SellerSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny(), ]
        elif self.action == 'retrieve' or self.action == 'update':
            return [IsAuthenticated(), ]
        return super(ShopUserViewSet, self).get_permissions()
