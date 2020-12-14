from rest_framework import serializers, fields

from shoppingmall.models import Order, Product, User, Shop
from shoppingmall.serializers.users_serializers import CustomerSerializer, SellerSerializer
from shoppingmall.serializers.product_serializers import ProductReadSerializer
from .shop_serializers import ShopReadSerializer
from ..models import OrderedProduct


class OrderedProductSerializer(serializers.ModelSerializer):
    product = fields.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(OrderedProductSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = OrderedProduct
        fields = ('id', 'order', 'product', 'buying', 'selling', 'quantity')

    def get_product(self, obj):
        item = Product.objects.get(pk=obj.product.pk)
        return ProductReadSerializer(item, context=self.context).data


class OrderSerializer(serializers.ModelSerializer):
    products = fields.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(OrderSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Order
        fields = (
            # main info
            'id', 'order_number', 'shop', 'user', 'type', 'name', 'phone',
            'address', 'address_image',
            'language', 'products',
            # price info
            'total_buying', 'total_selling', 'delivery_fee',
            # delivery info
            'posting_date', 'shipping_date', 'post_code', 'delivery_comment',
            # status
            'status', 'delivery', 'payment', 'deleted',
            'date_created')
        ordering = ['-date_created']

    def get_products(self, obj):
        items = OrderedProduct.objects.filter(order=obj.pk)
        return OrderedProductSerializer(items, many=True, context=self.context).data


class OrderDetailsSerializer(serializers.ModelSerializer):
    products = fields.SerializerMethodField(read_only=True)
    shop = fields.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(OrderDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Order
        fields = (
            # main info
            'id', 'order_number', 'shop', 'user', 'type', 'name', 'phone',
            'address', 'address_image',
            'language', 'products',
            # price info
            'total_buying', 'total_selling', 'delivery_fee',
            # delivery info
            'posting_date', 'shipping_date', 'post_code', 'delivery_comment',
            # status
            'status', 'delivery', 'payment', 'deleted',
            'date_created')
        ordering = ['-date_created']

    def get_products(self, obj):
        items = OrderedProduct.objects.filter(order=obj.pk)
        return OrderedProductSerializer(items, many=True, context=self.context).data

    def get_shop(self, obj):
        shop = Shop.objects.filter(id=obj.shop.pk)
        return ShopReadSerializer(shop, context=self.context).data


class AdminOrderDetailSerializer(serializers.ModelSerializer):
    products = fields.SerializerMethodField(read_only=True)
    user = fields.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(AdminOrderDetailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Order
        fields = (
            # main info
            'id', 'order_number', 'shop', 'user', 'type', 'name', 'phone',
            'address',
            'address_image',
            'language', 'products', 'operator_id', 'operator',
            # price info
            'total_buying', 'total_selling', 'delivery_fee',
            # delivery info
            'posting_date', 'shipping_date', 'post_code', 'delivery_comment',
            # status
            'status', 'delivery', 'payment', 'deleted',
            'date_created')
        ordering = ['-date_created']

    def get_user(self, obj):
        user = User.objects.get(pk=obj.user.pk)
        if user.is_customer():
            return CustomerSerializer(user.customer, context=self.context).data
        elif user.is_seller():
            return SellerSerializer(user.seller, context=self.context).data

    def get_products(self, obj):
        items = OrderedProduct.objects.filter(order=obj.pk)
        return OrderedProductSerializer(items, many=True, context=self.context).data
