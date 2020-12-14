from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view


@api_view(['POST'])
def save_medical(request):
    # ----- YAML below for Swagger -----
    """
    description: This API deletes/uninstalls a device.
    parameters:
      - name: name
        type: string
        required: true
        location: form
      - name: bloodgroup
        type: string
        required: true
        location: form
      - name: birthmark
        type: string
        required: true
        location: form
    """
    ...
    ...
