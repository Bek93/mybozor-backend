from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from shoppingmall.models import Collection, CollectionImages, Localize, Category
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


class CategorySerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()
    children = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(CategorySerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Category
        fields = ('id', 'parent_id', 'titles', 'is_active', 'children', 'date_created')
        ordering = ['-date_created']

    def create(self, validated_data):

        if 'titles' in validated_data:
            titles = validated_data.pop('titles')
            new_titles = Localize.objects.create(**titles)
            validated_data['titles_id'] = new_titles.id

        try:
            category = Category.objects.create(**validated_data)
            category.save()
        except ValidationError as err:
            raise ValidationError(err)

        return category

    def get_titles(self, obj):
        if obj.titles:
            titles = Localize.objects.get(id=obj.titles.id)
            return LocalizeSerializer(titles).data

    def get_children(self, obj):
        if obj:
            children = Category.objects.filter(parent_id=obj.id)
            return CategorySerializer(children, many=True).data


class ReadCategorySerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()
    parent = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ReadCategorySerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Category
        fields = ('id', 'parent_id', 'parent', 'titles', 'is_active', 'date_created')
        ordering = ['-date_created']

    def get_titles(self, obj):
        if obj.titles:
            titles = Localize.objects.get(id=obj.titles.id)
            return LocalizeSerializer(titles).data

    def get_parent(self, obj):
        if obj:
            if obj.parent_id > 0:
                parent = Category.objects.get(id=obj.parent_id)
                return ReadCategorySerializer(parent).data


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
