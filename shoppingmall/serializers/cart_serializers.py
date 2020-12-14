from rest_framework import serializers, fields
from rest_framework.serializers import BaseSerializer

from . import  OptionReadSerializer
from .product_serializers import ProductReadSerializer
from ..models import Cart


class CartSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(CartSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'shop', 'product', 'quantity', 'option', 'date_created')
        ordering = ['-date_created']


class CartDetailSerializer(serializers.ModelSerializer):
    product = ProductReadSerializer(read_only=True)
    option = OptionReadSerializer(read_only=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(CartDetailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'shop', 'product', 'option', 'quantity', 'date_created')
        ordering = ['-date_created']

