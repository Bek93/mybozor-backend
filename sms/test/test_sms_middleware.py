import os
import unittest

from django.core.exceptions import ImproperlyConfigured
from mock import Mock, patch
from sms.middleware import (
    MESSAGE,
    MessageClient,
    TwilioNotificationsMiddleware,
    load_admins_file,
    load_twilio_config
)


class TestSmsMiddleWare(unittest.TestCase):
    @patch('sms.middleware.load_twilio_config')
    @patch('sms.middleware.load_admins_file')
    def test_notify_exception(self, mock_load_admins_file, mock_load_twilio_config):
        # Given
        admin_number = '+12035442316'
        sending_number = '+821040439398'

        mock_load_admins_file.return_value = [
            {'name': 'Some name', 'phone_number': admin_number}
        ]

        mock_message_client = Mock(spec=MessageClient)
        mock_load_twilio_config.return_value = (
            sending_number,
            '4ccou1s1d',
            'som3tok3n',
        )

        middleware = TwilioNotificationsMiddleware(None)
        middleware.client = mock_message_client

        exception_message = 'Some exception message'

        # When
        middleware.process_exception(None, 'Some exception message')

        # Then
        mock_message_client.send_message.assert_called_once_with(
            MESSAGE.format(exception_message), admin_number
        )
