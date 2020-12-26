from shoppingmall.tasks import send_marketing_push_task
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response


class MarketingPushViewSet(viewsets.ModelViewSet):

    @action(methods=['post'], detail=False)
    def send_notification(self, request, pk=None):
        body = request.data

        send_marketing_push_task.delay(90193228, "Hello world")

        return Response({}, status.HTTP_200_OK)
