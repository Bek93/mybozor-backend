from django.core.exceptions import ValidationError
from rest_framework import serializers, fields

from shoppingmall.models import ProductImages, Product, Localize, Options, OptionValue, DeliveryPolicy, Category, \
    Subproduct, Classification
from shoppingmall.serializers import OptionSerializer, OptionReadSerializer, DeliveryPolicySerializer
from shoppingmall.serializers.collection_serializers import CollectionAdminSerializer, \
    LocalizeSerializer, CategorySerializer, SubproductSerializer, ReadSubproductSerializer, ClassificationSerializer
from shoppingmall.serializers.image_serializers import ProductImageSerializer


class ProductCreateSerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()
    descriptions = LocalizeSerializer()
    options = OptionSerializer(many=True, write_only=True)
    images = ProductImageSerializer(many=True, write_only=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ProductCreateSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields = (
            'id', 'shop', 'titles', 'descriptions', 'subproduct', 'collection', 'buying', 'selling', 'referral_fee',
            'quantity', 'has_delivery_fee', 'infinite', 'unit', 'label', 'banner', 'has_option', 'options', 'images',
            'is_active', 'currency', 'condition', 'brand', 'made_in'
        )
        ordering = ['-date_created']

    def create(self, validated_data):
        if 'titles' in validated_data:
            titles = validated_data.pop('titles')
            new_titles = Localize.objects.create(**titles)
            validated_data['titles_id'] = new_titles.id

        if 'descriptions' in validated_data:
            descriptions = validated_data.pop('descriptions')
            new_descriptions = Localize.objects.create(**descriptions)
            validated_data['descriptions_id'] = new_descriptions.id

        images = []
        if 'images' in validated_data:
            images = validated_data.pop("images")

        options = []
        if 'options' in validated_data:
            options = validated_data.pop("options")

        subproduct = validated_data['subproduct']
        validated_data['referral_fee'] = subproduct.category.classification.referral_rate * validated_data['selling']

        try:
            product = Product.objects.create(**validated_data)
            product.save()
        except ValidationError as err:
            raise ValidationError(err)

        if images:
            for image_data in images:
                try:
                    image_data['product'] = product.pk
                    image_data['shop'] = product.shop.pk
                    image = ProductImageSerializer(data=image_data)
                    image.is_valid(True)
                    image.save()
                except ValidationError as err:
                    raise ValidationError(err)

        if options:
            for option in options:
                try:
                    option['product'] = product
                    values = option.pop("values")
                    optionObject = Options.objects.create(**option)
                    optionObject.save()
                    for value in values:
                        value['option'] = optionObject
                        valueObject = OptionValue.objects.create(**value)
                        valueObject.save()
                except ValidationError as err:
                    raise ValidationError(err)

        return product

    def update(self, instance, validated_data):
        if 'titles' in validated_data:
            titles = validated_data.pop('titles')
            if instance.titles:
                titleSerializer = LocalizeSerializer(instance.titles, data=titles, partial=False)
                titleSerializer.is_valid(True)
                titleSerializer.save()
            else:
                new_titles = Localize.objects.create(**titles)
                validated_data['titles_id'] = new_titles.id

        if 'descriptions' in validated_data:
            descriptions = validated_data.pop('descriptions')
            if instance.descriptions:
                descriptionSerializer = LocalizeSerializer(instance.descriptions, data=descriptions, partial=False)
                descriptionSerializer.is_valid(True)
                descriptionSerializer.save()
            else:
                new_descriptions = Localize.objects.create(**descriptions)
                validated_data['descriptions_id'] = new_descriptions.id

        instance = super(ProductCreateSerializer, self).update(instance, validated_data)
        return instance


class ProductReadSerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()
    descriptions = LocalizeSerializer()
    image = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    collection = CollectionAdminSerializer()
    classification = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    subproduct = SubproductSerializer()
    options = serializers.SerializerMethodField()
    delivery_policy = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ProductReadSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields = (
            'id', 'shop', 'titles', 'descriptions', 'classification', 'category', 'subproduct', 'collection', 'buying',
            'selling', 'referral_fee', 'quantity', 'has_delivery_fee', 'infinite', 'unit', 'delivery_policy', 'label',
            'banner', 'has_option', 'options', 'images', 'image', 'is_active', 'currency', 'condition', 'brand',
            'made_in'
        )
        ordering = ['-date_created']

    def get_image(self, obj):
        image = ProductImages.objects.filter(product=obj, is_main=True)
        img = ProductImageSerializer(image, many=True, context=self.context).data
        if len(img) > 0:
            return img[0]
        return None

    def get_delivery_policy(self, obj):
        deliveryPolicy = DeliveryPolicy.objects.filter(shop=obj.shop.pk).order_by('pk')
        deliveryPolicy_data = DeliveryPolicySerializer(deliveryPolicy, many=True, context=self.context).data
        return deliveryPolicy_data

    def get_images(self, obj):
        image = ProductImages.objects.filter(product=obj).order_by('pk')
        img = ProductImageSerializer(image, many=True, context=self.context).data
        return img

    def get_classification(self, obj):
        if obj.subproduct and obj.subproduct.category:
            classification = Classification.objects.get(id=obj.subproduct.category.classification_id)
            return ClassificationSerializer(classification, context=self.context).data

    def get_category(self, obj):
        if obj.subproduct and obj.subproduct.category:
            category = Category.objects.get(id=obj.subproduct.category_id)
            return CategorySerializer(category, context=self.context).data

    def get_options(self, obj):
        options = Options.objects.filter(product=obj.id)
        return OptionReadSerializer(options, many=True, context=self.context).data


class ProductSerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()
    descriptions = LocalizeSerializer()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ProductSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields = (
            'id', 'shop', 'titles', 'descriptions', 'subproduct', 'collection', 'buying', 'selling', 'referral_fee',
            'quantity', 'has_delivery_fee', 'infinite', 'unit', 'label', 'banner', 'has_option', 'is_active', 'currency'
        )
        ordering = ['-date_created']


class DashboardProductSerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(DashboardProductSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields = (
            'id', 'shop', 'titles')
        ordering = ['-date_created']


from rest_framework import serializers


class DailyOrderedProductSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    quantity = serializers.IntegerField()
    month = serializers.StringRelatedField()
    product_id = serializers.IntegerField()
    product = serializers.SerializerMethodField()

    def get_product(self, obj):
        item = Product.objects.get(pk=obj['product_id'])
        return ProductSerializer(item, context=self.context).data
