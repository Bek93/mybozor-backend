from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from shoppingmall.models import User, Shop, Organization
from rest_framework.permissions import AllowAny, IsAuthenticated

from shoppingmall.serializers.organization_serializers import OrganizationSerializer
from shoppingmall.serializers.shop_serializers import ShopSerializer
from shoppingmall.utils.logger import Logger

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    """
    Create a model instance.
    """

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = OrganizationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except Exception as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        response = serializer.data
        organization = Organization.objects.get(id=response["id"])
        user = request.user
        if user.is_seller():
            user.seller.organization = organization
            user.seller.save()
        headers = self.get_success_headers(serializer.data)
        Logger().d(data_string=data, method=request.method, path=request.path,
                   shop_id=0, user_id=user.id, payload_string=response, status_code=201)
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrganizationSerializer(instance, context=self.get_serializer_context())
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        user = request.user
        try:
            user = request.user
            if user.is_authenticated and user.is_admin():
                queryset = Organization.objects.all().order_by('pk')
                serializer = OrganizationSerializer(queryset, context=self.get_serializer_context(), many=True)
                response = serializer.data
                Logger().d(data_string='', method=request.method, path=request.path,
                           shop_id="", user_id=user.id, payload_string=response, status_code=200)
                return Response(response)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id="", user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        user = request.user
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = OrganizationSerializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            response = serializer.data
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=kwargs['pk'], user_id=user.id, payload_string=response, status_code=200)
            return Response(response)
        except Exception as err:
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=kwargs['pk'], user_id=user.id, payload_string=str(err), status_code=400)
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
