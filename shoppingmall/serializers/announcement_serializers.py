from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from shoppingmall.models import Announcement, Filter, Localize
from shoppingmall.serializers import LocalizeSerializer
from shoppingmall.serializers.image_serializers import ImageSerializer
from shoppingmall.utils.image_utils import Base64ImageField


class FilterSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(FilterSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Filter
        fields = ('id', 'type', 'province', 'language', 'gender', 'date_created')


class AnnouncementSerializer(serializers.ModelSerializer):
    titles = LocalizeSerializer()
    descriptions = LocalizeSerializer()
    image = Base64ImageField(max_length=None, use_url=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(AnnouncementSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Announcement
        fields = ('id', 'shop', 'titles', 'descriptions', 'type', 'image', 'total_target_count',
                  'product_id', 'is_completed', 'started_at', 'ended_at', 'date_created')

    def create(self, validated_data):
        if 'titles' in validated_data:
            titles = validated_data.pop('titles')
            new_titles = Localize.objects.create(**titles)
            validated_data['titles_id'] = new_titles.id

        if 'descriptions' in validated_data:
            descriptions = validated_data.pop('descriptions')
            new_descriptions = Localize.objects.create(**descriptions)
            validated_data['descriptions_id'] = new_descriptions.id

        try:
            announcement = Announcement.objects.create(**validated_data)
            announcement.save()
        except ValidationError as err:
            raise ValidationError(err)
        return announcement
