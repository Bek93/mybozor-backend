from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from shoppingmall.models import Collection, CollectionImages, Localize, Category, Classification, Subproduct
from shoppingmall.serializers import LocalizeSerializer
from shoppingmall.serializers.image_serializers import CollectionImagesSerializer
from shoppingmall.utils.image_utils import Base64ImageField


class CollectionSerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()
    images = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(CollectionSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Collection
        fields = ('id', 'titles', 'images', 'date_created')
        ordering = ['-date_created']

    def get_images(self, obj):
        images = CollectionImages.objects.filter(category=obj.pk)
        return CollectionImagesSerializer(images, many=True).data


class ClassificationSerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ClassificationSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Classification
        fields = ('id', 'titles', 'is_active', 'referral_rate', 'date_created')
        ordering = ['-date_created']

    def create(self, validated_data):
        if 'titles' in validated_data:
            titles = validated_data.pop('titles')
            titles['type'] = 'classification'
            new_titles = Localize.objects.create(**titles)
            validated_data['titles_id'] = new_titles.id

        try:
            classification = Classification.objects.create(**validated_data)
            classification.save()
        except ValidationError as err:
            raise ValidationError(err)

        return classification


class CategorySerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(CategorySerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Category
        fields = ('id', 'classification', 'titles', 'is_active', 'date_created')
        ordering = ['-date_created']

    def create(self, validated_data):

        if 'titles' in validated_data:
            titles = validated_data.pop('titles')
            titles['type'] = 'category'
            new_titles = Localize.objects.create(**titles)
            validated_data['titles_id'] = new_titles.id

        try:
            category = Category.objects.create(**validated_data)
            category.save()
        except ValidationError as err:
            raise ValidationError(err)

        return category


class ReadCategorySerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()
    classification = ClassificationSerializer()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ReadCategorySerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Category
        fields = ('id', 'classification', 'titles', 'is_active', 'date_created')
        ordering = ['-date_created']


class ReadClassificationSerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()
    categories = ReadCategorySerializer(many=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ReadClassificationSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Classification
        fields = ('id', 'titles', 'is_active', 'referral_rate', 'categories', 'date_created')
        ordering = ['-date_created']

    def create(self, validated_data):
        if 'titles' in validated_data:
            titles = validated_data.pop('titles')
            titles['type'] = 'classification'
            new_titles = Localize.objects.create(**titles)
            validated_data['titles_id'] = new_titles.id

        try:
            classification = Classification.objects.create(**validated_data)
            classification.save()
        except ValidationError as err:
            raise ValidationError(err)

        return classification


class SubproductSerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(SubproductSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Subproduct
        fields = ('id', 'category', 'titles', 'is_active', 'date_created')
        ordering = ['-date_created']

    def create(self, validated_data):
        if 'titles' in validated_data:
            titles = validated_data.pop('titles')
            titles['type'] = 'category'
            new_titles = Localize.objects.create(**titles)
            validated_data['titles_id'] = new_titles.id

        try:
            subproduct = Subproduct.objects.create(**validated_data)
            subproduct.save()
        except ValidationError as err:
            raise ValidationError(err)

        return subproduct


class ReadSubproductSerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()
    category = ReadCategorySerializer()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ReadSubproductSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Subproduct
        fields = ('id', 'category', 'titles', 'is_active', 'date_created')
        ordering = ['-date_created']


class CollectionAdminSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField(read_only=True)
    titles = LocalizeSerializer()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(CollectionAdminSerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):

        if 'titles' in validated_data:
            titles = validated_data.pop('titles')
            new_titles = Localize.objects.create(**titles)
            validated_data['titles_id'] = new_titles.id

        try:
            collection = Collection.objects.create(**validated_data)
            collection.save()
        except ValidationError as err:
            raise ValidationError(err)

        return collection

    class Meta:
        model = Collection
        fields = (
            'id', 'shop', 'parent_id', 'titles', 'is_active', 'images', 'date_created')
        ordering = ['-date_created']

    def get_titles(self, obj):
        if obj.titles:
            titles = Localize.objects.get(id=obj.titles.id)
            return LocalizeSerializer(titles).data

    def get_images(self, obj):
        images = CollectionImages.objects.filter(collection=obj.pk)
        return CollectionImagesSerializer(images, many=True, context=self.context).data
