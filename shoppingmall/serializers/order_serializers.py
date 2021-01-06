from django.db import connection
from rest_framework import serializers, fields

from shoppingmall.models import Order, Product, User, Shop, Invoice
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


class InvoiceSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(InvoiceSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Invoice
        fields = (
            'id', 'shop', 'month', 'status', 'invoice_number', 'details', 'date_created')

    def get_details(self, obj):
        query = f"""SELECT SUM(total_selling), SUM(total_referral_fee), COUNT(*)from shoppingmall_order where invoice_id={obj.id}"""
        response = self.my_custom_sql(query)
        total_referral_fee = 0
        total_selling = 0
        count = 0
        if len(response) > 0:
            row = response[0]
            total_selling = row[0]
            total_referral_fee = row[1]
            count = row[2]

        data = {
            "total_selling": total_selling,
            "total_referral_fee": total_referral_fee,
            "count": count
        }
        return data

    def my_custom_sql(self, sql):
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchall()

        return row


class OrderSerializer(serializers.ModelSerializer):
    products = fields.SerializerMethodField(read_only=True)
    invoice = InvoiceSerializer(read_only=True)

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
            'status', 'delivery', 'payment', 'deleted', 'invoice', 'accepted_by',
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
            'status', 'delivery', 'payment', 'deleted', 'invoice', 'accepted_by',
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
            'status', 'delivery', 'payment', 'deleted', 'invoice', 'accepted_by',
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
