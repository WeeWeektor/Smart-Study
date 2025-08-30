import json
from unittest.mock import patch, AsyncMock, Mock
from django.test import RequestFactory, TestCase

from users.services import oauth_service


class DummyUser:
    def __init__(self, email, name="Alice", surname="Smith", role="student"):
        self.email = email
        self.name = name
        self.surname = surname
        self.role = role
        self.is_verified_email = False
        self.is_active = False

    def save(self):
        self.is_verified_email = True
        self.is_active = True


class TestOAuthService(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.post('/oauth/login')
        self.existing_user = DummyUser(email="existing@example.com")
        self.new_user_email = "new@example.com"

    @patch("users.services.oauth_service.settings")
    @patch("users.services.oauth_service.httpx.AsyncClient")
    async def test_verify_facebook_token_success(self, mock_client, mock_settings):
        mock_settings.SOCIAL_AUTH_FACEBOOK_KEY = "test_app_id"
        mock_settings.SOCIAL_AUTH_FACEBOOK_SECRET = "test_app_secret"

        mock_async_client = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_async_client

        debug_response = Mock()
        debug_response.json.return_value = {"data": {"is_valid": True}}

        user_response = Mock()
        user_response.json.return_value = {
            "id": "123",
            "email": "fb@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }

        mock_async_client.get.side_effect = [debug_response, user_response]

        result = await oauth_service.verify_facebook_token("valid_token")

        self.assertEqual(result["email"], "fb@example.com")
        self.assertEqual(result["sub"], "123")
        self.assertEqual(result["given_name"], "John")
        self.assertEqual(result["family_name"], "Doe")

    @patch("users.services.oauth_service.settings")
    @patch("users.services.oauth_service.httpx.AsyncClient")
    async def test_verify_facebook_token_invalid(self, mock_client, mock_settings):
        mock_settings.SOCIAL_AUTH_FACEBOOK_KEY = "test_app_id"
        mock_settings.SOCIAL_AUTH_FACEBOOK_SECRET = "test_app_secret"

        mock_async_client = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_async_client

        debug_response = Mock()
        debug_response.json.return_value = {"data": {"is_valid": False}}
        mock_async_client.get.return_value = debug_response

        with self.assertRaises(ValueError) as cm:
            await oauth_service.verify_facebook_token("bad_token")
        self.assertIn("Invalid Facebook token", str(cm.exception))

    @patch("users.services.oauth_service.settings")
    @patch("users.services.oauth_service.httpx.AsyncClient")
    async def test_verify_facebook_token_api_error(self, mock_client, mock_settings):
        mock_settings.SOCIAL_AUTH_FACEBOOK_KEY = "test_app_id"
        mock_settings.SOCIAL_AUTH_FACEBOOK_SECRET = "test_app_secret"

        mock_async_client = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_async_client

        debug_response = Mock()
        debug_response.json.return_value = {"data": {"is_valid": True}}

        mock_async_client.get.side_effect = [debug_response, Exception("HTTP Error")]

        with self.assertRaises(Exception):
            await oauth_service.verify_facebook_token("bad_token")

    @patch("users.services.oauth_service.cache")
    @patch("users.services.oauth_service.get_user_model")
    @patch("users.services.oauth_service.id_token")
    @patch("users.services.oauth_service.settings")
    @patch("users.services.oauth_service.login", new=lambda *a, **k: None)
    @patch("users.services.oauth_service.warm_user_cache", new_callable=AsyncMock)
    async def test_google_existing_user(
            self, mock_warm, mock_settings, mock_id_token, mock_get_user_model, mock_cache
    ):
        mock_settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "test_key"
        mock_id_token.verify_oauth2_token.return_value = {
            "email": self.existing_user.email,
            "given_name": "Alice",
            "family_name": "Smith"
        }

        mock_cache.get.return_value = None
        mock_cache.set = Mock()

        self.existing_user.is_active = True
        self.existing_user.is_verified_email = True

        UserModel = Mock()
        UserModel.objects.filter.return_value.first.return_value = self.existing_user
        mock_get_user_model.return_value = UserModel

        response = await oauth_service.handle_oauth_login(
            request=self.request, token="token", provider="google",
            role="student", surname="Smith"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["user"]["email"], self.existing_user.email)

    @patch("users.services.oauth_service.cache")
    @patch("users.services.oauth_service.get_user_model")
    @patch("users.services.oauth_service.verify_facebook_token", new_callable=AsyncMock)
    @patch("users.services.oauth_service.get_allowed_roles", new_callable=AsyncMock)
    @patch("users.services.oauth_service.login", new=lambda *a, **k: None)
    @patch("users.services.oauth_service.UserSettings")
    @patch("users.services.oauth_service.warm_user_cache", new_callable=AsyncMock)
    @patch("users.services.oauth_service.invalidate_user_existence_cache", new_callable=AsyncMock)
    @patch("users.services.oauth_service.get_random_string", return_value="random_pass")
    async def test_facebook_new_user(self, mock_random, mock_invalidate, mock_warm,
                                     mock_UserSettings, mock_roles, mock_fb_verify,
                                     mock_get_user_model, mock_cache):
        mock_fb_verify.return_value = {
            "email": self.new_user_email,
            "given_name": "Bob",
            "family_name": "Builder"
        }
        mock_roles.return_value = ["student", "teacher"]

        mock_cache.get.return_value = None
        mock_cache.set = Mock()

        mock_UserSettings.objects.create.return_value = Mock()

        UserModel = Mock()
        UserModel.objects.filter.return_value.first.return_value = None
        UserModel.objects.create_user.return_value = DummyUser(
            email=self.new_user_email, name="Bob", surname="Builder", role="student"
        )
        mock_get_user_model.return_value = UserModel

        response = await oauth_service.handle_oauth_login(
            request=self.request, token="fb_token", provider="facebook",
            role="student", surname="Builder"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["user"]["email"], self.new_user_email)

    @patch("users.services.oauth_service.settings")
    @patch("users.services.oauth_service.id_token")
    @patch("users.services.oauth_service.get_user_model")
    @patch("users.services.oauth_service.cache")
    async def test_missing_role_for_new_user(self, mock_cache, mock_get_user_model,
                                             mock_id_token, mock_settings):
        mock_settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "test_key"
        mock_id_token.verify_oauth2_token.return_value = {
            "email": "newuser@example.com",
            "given_name": "New",
            "family_name": "User"
        }

        mock_cache.get.return_value = None
        mock_cache.set = Mock()

        UserModel = Mock()
        UserModel.objects.filter.return_value.first.return_value = None
        mock_get_user_model.return_value = UserModel

        response = await oauth_service.handle_oauth_login(
            request=self.request, token="token", provider="google"
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("You must specify role and surname", data["error"])

    @patch("users.services.oauth_service.cache")
    @patch("users.services.oauth_service.get_user_model")
    @patch("users.services.oauth_service.id_token")
    @patch("users.services.oauth_service.settings")
    @patch("users.services.oauth_service.get_allowed_roles", new_callable=AsyncMock)
    async def test_incorrect_role(self, mock_roles, mock_settings, mock_id_token,
                                  mock_get_user_model, mock_cache):
        mock_settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "test_key"
        mock_id_token.verify_oauth2_token.return_value = {
            "email": "newuser@example.com",
            "given_name": "New",
            "family_name": "User"
        }
        mock_roles.return_value = ["student", "teacher"]

        mock_cache.get.return_value = None
        mock_cache.set = Mock()

        UserModel = Mock()
        UserModel.objects.filter.return_value.first.return_value = None
        mock_get_user_model.return_value = UserModel

        response = await oauth_service.handle_oauth_login(
            request=self.request, token="token", provider="google",
            role="admin", surname="Test"
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("Incorrect role", data["error"])

    async def test_unknown_provider(self):
        response = await oauth_service.handle_oauth_login(
            request=self.request, token="any", provider="unknown",
            role="student", surname="Test"
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("Unknown OAuth provider", data["error"])

    @patch("users.services.oauth_service.cache")
    async def test_general_exception(self, mock_cache):
        mock_cache.get.side_effect = Exception("Unexpected error")
        mock_cache.set = Mock()

        response = await oauth_service.handle_oauth_login(
            request=self.request, token="token", provider="google",
            role="student", surname="Test"
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("Unexpected error", data["error"])