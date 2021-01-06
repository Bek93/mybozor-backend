from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from shoppingmall.models import Shop, ShopConfig, DeliveryPolicy
from shoppingmall.serializers import DeliveryPolicySerializer
from shoppingmall.utils.config import default_shop_config


class ShopConfigSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ShopConfigSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = ShopConfig
        fields = (
            'id', 'telegram_store', 'telegram_new_order',
            'telegram_accept', 'sms_enabled', 'telegram_enabled', 'app_enabled',
            'date_created')


class ShopSerializer(serializers.ModelSerializer):
    config = ShopConfigSerializer()
    delivery_policy = DeliveryPolicySerializer(many=True, write_only=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ShopSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Shop
        fields = (
            'id', 'name', 'bank', 'country', 'city', 'province', 'phone_number', 'postal_code',
            'address', 'delivery_policy', 'sell_option', 'config', 'status', 'date_created')

    def create(self, validated_data):
        new_config = ShopConfig.objects.create(**default_shop_config)
        validated_data['config_id'] = new_config.id

        delivery_policy = None
        if "delivery_policy" in validated_data:
            delivery_policy = validated_data.pop('delivery_policy')
        new_shop = Shop.objects.create(**validated_data)

        if delivery_policy:
            try:
                for policy in delivery_policy:
                    policy['shop'] = new_shop
                    DeliveryPolicy.objects.create(**policy)
            except Exception as ex:
                print(ex)

        return new_shop

    def get_delivery_policy(self, obj):
        deliveryPolicy = DeliveryPolicy.objects.filter(product=obj).order_by('pk')
        deliveryPolicy_data = DeliveryPolicySerializer(deliveryPolicy, many=True, context=self.context).data
        return deliveryPolicy_data

    def get_config(self, obj):

        if obj.config:
            is_customer = False
            if hasattr(self.context, 'is_customer'):
                is_customer = self.context['is_customer']

            if not is_customer:
                shopConfig = ShopConfig.objects.get(id=obj.config.id)
                return ShopConfigSerializer(shopConfig).data


class ShopReadSerializer(serializers.ModelSerializer):
    config = serializers.SerializerMethodField()
    delivery_policy = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ShopReadSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Shop
        fields = (
            'id', 'name', 'bank', 'country', 'city', 'province', 'phone_number', 'postal_code',
            'address', 'delivery_policy', 'sell_option', 'config', 'status', 'date_created')

    def get_delivery_policy(self, obj):
        deliveryPolicy = DeliveryPolicy.objects.filter(shop=obj.pk).order_by('pk')
        deliveryPolicy_data = DeliveryPolicySerializer(deliveryPolicy, many=True, context=self.context).data
        return deliveryPolicy_data

    def get_config(self, obj):

        if obj.config:
            is_customer = False
            if hasattr(self.context, 'is_customer'):
                is_customer = self.context['is_customer']

            if not is_customer:
                shopConfig = ShopConfig.objects.get(id=obj.config.id)
                return ShopConfigSerializer(shopConfig, context=self.context).data
