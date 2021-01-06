import pytz
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from shoppingmall.models import Localize, Options, OptionValue, DeliveryPolicy, Province


class DateTimeFieldWihTZ(serializers.DateTimeField):
    '''Class to make output of a DateTime Field timezone aware
    '''

    def to_representation(self, value):
        value = timezone.localtime(value, timezone=timezone.utc)
        return super(DateTimeFieldWihTZ, self).to_representation(value)


class LocalizeSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(LocalizeSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Localize
        fields = ('id', 'type', 'uz', 'en', 'kr', 'ru', 'date_created')
        ordering = ['-date_created']


class OptionValueSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(OptionValueSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = OptionValue
        fields = ('id', 'option', 'title', 'value', 'date_created')
        ordering = ['-date_created']


class OptionSerializer(serializers.ModelSerializer):
    values = OptionValueSerializer(many=True)

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(OptionSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Options
        fields = ('id', 'product', 'values', 'buying', 'selling', 'quantity', 'date_created')
        ordering = ['-date_created']


class OptionReadSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(OptionReadSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Options
        fields = ('id', 'product', 'values', 'buying', 'selling', 'quantity', 'date_created')
        ordering = ['-date_created']

    def get_values(self, obj):
        values = OptionValue.objects.filter(option=obj.id)
        if values:
            return OptionValueSerializer(values, many=True, context=self.context).data


class LogSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(LogSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Options
        fields = ('id', 'request_size', 'response_size', 'status_code', 'server_type', 'method',
                  'path', 'data_string', 'payload_string', 'app_id', 'user_id', 'date_created')
        ordering = ['-date_created']


class DeliveryPolicySerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(DeliveryPolicySerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = DeliveryPolicy
        fields = ('id', 'shop', 'type', 'unit_from', 'unit_to', 'fee', 'currency', 'comment', 'date_created')


class ProvinceSerializer(serializers.ModelSerializer):
    province = LocalizeSerializer()

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(ProvinceSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = DeliveryPolicy
        fields = ('id', 'province', 'date_created')

    def create(self, validated_data):

        if 'province' in validated_data:
            province = validated_data.pop('province')
            new_province = Localize.objects.create(**province)
            validated_data['province_id'] = new_province.id

        try:
            province = Province.objects.create(**validated_data)
            province.save()
        except ValidationError as err:
            raise ValidationError(err)

        return province

    def update(self, instance, validated_data):

        if 'province' in validated_data:
            province = validated_data.pop('province')
            if instance.province:
                provinceSerializer = LocalizeSerializer(instance.province, data=province, partial=False)
                provinceSerializer.is_valid(True)
                provinceSerializer.save()
            else:
                new_province = Localize.objects.create(**province)
                validated_data['province_id'] = new_province.id
        instance = super(ProvinceSerializer, self).update(instance, validated_data)
        return instance
