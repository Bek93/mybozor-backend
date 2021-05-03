from rest_framework import serializers, fields
from rest_framework.exceptions import ValidationError

from shoppingmall.models import Seller, Customer, Admin, Province
from shoppingmall.serializers import ProvinceSerializer
from shoppingmall.serializers.shop_serializers import ShopSerializer, ShopReadSerializer
from shoppingmall.utils.image_utils import Base64ImageField


class SellerSerializer(serializers.ModelSerializer):
    shop = ShopReadSerializer(read_only=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(SellerSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Seller
        fields = (
            'id', 'shop', 'username', 'email', 'name', 'password', 'language', 'is_shop_admin',
            'is_shop_staff', 'is_shop_owner', 'shop', 'date_joined')
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):

        try:
            user = Seller.objects.create_shop_owner(**validated_data)
        except ValidationError as err:
            raise ValidationError(err)

        return user


class MemberSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(MemberSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Seller
        fields = (
            'id', 'shop', 'username', 'email', 'name', 'password', 'language', 'is_shop_admin',
            'is_shop_staff', 'is_shop_owner', 'shop', 'date_joined')
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        try:
            user = Seller.objects.create_shop_owner(**validated_data)
        except ValidationError as err:
            raise ValidationError(err)

        return user


class CustomerSerializer(serializers.ModelSerializer):
    province = ProvinceSerializer(read_only=True)
    province_id = serializers.IntegerField(write_only=True)
    address_image = Base64ImageField(max_length=None, use_url=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(CustomerSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Customer
        fields = (
            'id', 'username', 'password', "name", "shop", "province", "province_id", "phone_number", "type", "address",
            "address_image", "gender", "language", "deleted")
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):

        try:
            user = Customer.objects.create_customer(**validated_data)
        except ValidationError as err:
            raise ValidationError(err)

        return user


class AdminSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(AdminSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Admin
        fields = (
            'id', 'username', 'password', "name", "email", "is_admin", "is_staff")
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):

        try:
            user = Customer.objects.create_customer(**validated_data)
        except ValidationError as err:
            raise ValidationError(err)

        return user
