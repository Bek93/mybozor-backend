from rest_framework import serializers, fields
from rest_framework.exceptions import ValidationError

from shoppingmall.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(OrganizationSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Organization
        fields = ('id', 'name', 'country', 'plan', 'date_created')
