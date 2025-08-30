import asyncio
import json
from django.test import TestCase
from unittest.mock import patch, AsyncMock
from django.http import JsonResponse

from users import user_utils
from users.utils.email_templates import (
    get_verification_email_plain,
    get_verification_email_html,
)


class DummyUser:
    def __init__(self, email, name=None):
        self.email = email
        self.name = name


class TestSyncFunctions(TestCase):
    def test_error_response(self):
        response = user_utils.error_response("Test error", status=422)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 422)
        data = json.loads(response.content.decode())
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["message"], "Test error")

    def test_success_response_with_data(self):
        data = {"key": "value"}
        response = user_utils.success_response(data=data, message="Done")
        resp_data = json.loads(response.content.decode())
        self.assertEqual(resp_data["status"], "success")
        self.assertEqual(resp_data["message"], "Done")
        self.assertEqual(resp_data["key"], "value")

    def test_success_response_without_data(self):
        response = user_utils.success_response()
        resp_data = json.loads(response.content.decode())
        self.assertEqual(resp_data["status"], "success")
        self.assertEqual(resp_data["message"], "Successfully")

    def test_generate_activation_token(self):
        email = "user@example.com"
        token = user_utils.generate_activation_token(email)
        self.assertIsInstance(token, str)
        self.assertIn(email, token)


class TestAsyncFunctions(TestCase):
    def setUp(self):
        self.user = DummyUser(email="test@example.com", name="Alice")

    @patch("users.user_utils.sync_to_async")
    def test_send_template_email_happy_path(self, mock_sync):
        mock_send = AsyncMock()
        mock_sync.return_value = mock_send

        async def runner():
            await user_utils.send_template_email(
                user=self.user,
                subject="Subject",
                url_path="/verify/",
                html_template_func=get_verification_email_html,
                plain_template_func=get_verification_email_plain
            )

        asyncio.run(runner())
        mock_sync.assert_called_once()
        mock_send.assert_awaited_once()

    @patch("users.user_utils.sync_to_async")
    def test_send_template_email_without_name(self, mock_sync):
        mock_send = AsyncMock()
        mock_sync.return_value = mock_send
        user_no_name = DummyUser(email="test@example.com", name=None)

        async def runner():
            await user_utils.send_template_email(
                user=user_no_name,
                subject="Test",
                url_path="/path/",
                html_template_func=get_verification_email_html,
                plain_template_func=get_verification_email_plain
            )

        asyncio.run(runner())
        mock_sync.assert_called_once()
        mock_send.assert_awaited_once()

    @patch("users.user_utils.generate_activation_token", return_value=None)
    @patch("users.user_utils.sync_to_async")
    def test_send_template_email_raises_value_error_if_no_token(self, mock_sync, mock_token):
        mock_send = AsyncMock()
        mock_sync.return_value = mock_send

        async def runner():
            with self.assertRaises(ValueError) as cm:
                await user_utils.send_template_email(
                    user=self.user,
                    subject="Subject",
                    url_path="/",
                    html_template_func=get_verification_email_html,
                    plain_template_func=get_verification_email_plain
                )
            self.assertIn("Unable to create activation token", str(cm.exception))

        asyncio.run(runner())

    @patch("users.user_utils.send_template_email", new_callable=AsyncMock)
    def test_send_verification_email_calls_template_email(self, mock_send_template):
        async def runner():
            await user_utils.send_verification_email(self.user)

        asyncio.run(runner())
        mock_send_template.assert_awaited_once()
        _, kwargs = mock_send_template.call_args
        self.assertEqual(kwargs["user"], self.user)
        self.assertIn("/api/auth/verify-email/", kwargs["url_path"])

    @patch("users.user_utils.send_template_email", new_callable=AsyncMock)
    def test_send_password_reset_email_calls_template_email(self, mock_send_template):
        async def runner():
            await user_utils.send_password_reset_email(self.user)

        asyncio.run(runner())
        mock_send_template.assert_awaited_once()
        _, kwargs = mock_send_template.call_args
        self.assertEqual(kwargs["user"], self.user)
        self.assertIn("/api/auth/reset-password/", kwargs["url_path"])
