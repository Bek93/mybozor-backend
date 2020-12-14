from rest_framework import serializers, fields
from shoppingmall.models import ProductImages, CollectionImages, Images
from shoppingmall.utils.image_utils import Base64ImageField


class ImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None, use_url=True
    )

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ImageSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Images
        fields = ['id', 'shop', 'type', 'image', 'date_created']
        ordering = ['-date_created']


class CollectionImagesSerializer(serializers.ModelSerializer):
    telegram_image = Base64ImageField(max_length=None, use_url=True)
    app_image = Base64ImageField(max_length=None, use_url=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(CollectionImagesSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = CollectionImages
        fields = ['id', 'shop', 'category', 'telegram_image', 'app_image', 'language', 'date_created']
        ordering = ['-date_created']


class ProductImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ProductImageSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = ProductImages
        fields = ['id', 'shop', 'product', 'image', 'is_main', 'date_created']
        ordering = ['-date_created']


