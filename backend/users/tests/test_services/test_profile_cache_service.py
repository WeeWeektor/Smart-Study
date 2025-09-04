import asyncio
from unittest.mock import patch, AsyncMock, Mock

from django.test import TestCase

from users.services import profile_cache_service


class DummyUser:
    def __init__(self, id_=1, email="user@example.com", name="Alice", surname="Smith",
                 role="student", phone_number=None, is_active=True, is_staff=False,
                 is_superuser=False, is_verified_email=True):
        self.id = id_
        self.email = email
        self.name = name
        self.surname = surname
        self.role = role
        self.phone_number = phone_number
        self.is_active = is_active
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.is_verified_email = is_verified_email


class DummySettings:
    email_notifications = True
    push_notifications = True
    deadline_reminders = True
    show_profile_to_others = True
    show_achievements = True


class DummyProfile:
    bio = "Bio"
    profile_picture = "pic.png"
    location = "Kyiv"
    organization = "Org"
    specialization = "Spec"
    education_level = "master"


class ProfileCacheServiceTestCase(TestCase):
    def setUp(self):
        self.user = DummyUser()

    @patch("users.services.profile_cache_service.cache")
    @patch("users.services.profile_cache_service.settings")
    def test_get_allowed_roles_cache_miss(self, mock_settings, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.set = Mock()
        mock_settings.ALLOWED_ROLES = ["student", "teacher"]

        roles = asyncio.run(profile_cache_service.get_allowed_roles())

        self.assertEqual(roles, ["student", "teacher"])
        mock_cache.set.assert_called_once()

    @patch("users.services.profile_cache_service.cache")
    def test_get_allowed_roles_cache_hit(self, mock_cache):
        mock_cache.get.return_value = ["student", "teacher"]

        roles = asyncio.run(profile_cache_service.get_allowed_roles())

        self.assertEqual(roles, ["student", "teacher"])

    @patch("users.services.profile_cache_service.cache")
    @patch("users.services.profile_cache_service.CustomUser")
    def test_get_user_existence_cache_exists(self, mock_CustomUser, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.set = Mock()

        mock_CustomUser.objects.get.return_value = self.user

        result = asyncio.run(profile_cache_service.get_user_existence_cache(self.user.email))

        self.assertTrue(result["exists"])
        self.assertEqual(result["id"], self.user.id)
        mock_cache.set.assert_called_once()

    @patch("users.services.profile_cache_service.cache")
    def test_get_user_existence_cache_cache_hit(self, mock_cache):
        cached_data = {"exists": True, "id": self.user.id}
        mock_cache.get.return_value = cached_data

        result = asyncio.run(profile_cache_service.get_user_existence_cache(self.user.email))

        self.assertEqual(result, cached_data)

    def test_get_user_existence_cache_no_email(self):
        result = asyncio.run(profile_cache_service.get_user_existence_cache(None))
        self.assertFalse(result["exists"])

    @patch("users.services.profile_cache_service.cache")
    @patch("users.services.profile_cache_service.CustomUser")
    def test_get_user_existence_cache_user_does_not_exist(self, mock_CustomUser, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.set = Mock()

        mock_CustomUser.DoesNotExist = Exception
        mock_CustomUser.objects.get.side_effect = mock_CustomUser.DoesNotExist("User not found")

        result = asyncio.run(profile_cache_service.get_user_existence_cache("nonexistent@example.com"))

        self.assertFalse(result["exists"])
        mock_cache.set.assert_called_once()

    @patch("users.services.profile_cache_service.cache")
    @patch("users.services.profile_cache_service.UserSettings")
    def test_get_cached_user_settings_cache_miss(self, mock_UserSettings, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.set = Mock()

        dummy_settings = DummySettings()
        mock_UserSettings.objects.get_or_create.return_value = (dummy_settings, False)

        result = asyncio.run(profile_cache_service.get_cached_user_settings(self.user))

        self.assertIsNotNone(result)
        mock_cache.set.assert_called_once()

    @patch("users.services.profile_cache_service.cache")
    def test_get_cached_user_settings_cache_hit(self, mock_cache):
        cached_settings = {"email_notifications": True}
        mock_cache.get.return_value = cached_settings

        result = asyncio.run(profile_cache_service.get_cached_user_settings(self.user))

        self.assertEqual(result, cached_settings)

    @patch("users.services.profile_cache_service.cache")
    @patch("users.services.profile_cache_service.UserSettings")
    def test_get_cached_user_settings_exception(self, mock_UserSettings, mock_cache):
        mock_cache.get.return_value = None
        mock_UserSettings.objects.get_or_create.side_effect = Exception("Database error")

        result = asyncio.run(profile_cache_service.get_cached_user_settings(self.user))

        self.assertEqual(result, {})

    @patch("users.services.profile_cache_service.cache")
    def test_get_cached_user_status_cache_miss(self, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.set = Mock()

        result = asyncio.run(profile_cache_service.get_cached_user_status(self.user))

        self.assertIsNotNone(result)
        mock_cache.set.assert_called_once()

    @patch("users.services.profile_cache_service.cache")
    def test_get_cached_user_status_cache_hit(self, mock_cache):
        cached_status = {"is_active": True, "is_verified": True}
        mock_cache.get.return_value = cached_status

        result = asyncio.run(profile_cache_service.get_cached_user_status(self.user))

        self.assertEqual(result, cached_status)

    @patch("users.services.profile_cache_service.cache")
    @patch("users.services.profile_cache_service.UserProfile")
    @patch("users.services.profile_cache_service.UserSettings")
    @patch("users.services.profile_cache_service.CustomUser")
    def test_get_cached_profile_cache_miss(self, mock_CustomUser, mock_UserSettings, mock_UserProfile, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.set = Mock()

        dummy_profile = DummyProfile()
        dummy_settings = DummySettings()
        dummy_user = DummyUser()

        mock_user_queryset = Mock()
        mock_user_queryset.get.return_value = dummy_user
        mock_CustomUser.objects.select_related.return_value = mock_user_queryset

        mock_UserProfile.objects.get_or_create.return_value = (dummy_profile, False)
        mock_UserSettings.objects.get_or_create.return_value = (dummy_settings, False)

        result = asyncio.run(profile_cache_service.get_cached_profile(self.user))

        self.assertIsNotNone(result)
        self.assertIn('user', result)
        self.assertIn('settings', result)
        self.assertIn('profile', result)

        self.assertGreaterEqual(mock_cache.set.call_count, 1)

    @patch("users.services.profile_cache_service.cache")
    def test_get_cached_profile_cache_hit(self, mock_cache):
        cached_profile = {"user": {"id": str(self.user.id)}}
        mock_cache.get.return_value = cached_profile

        result = asyncio.run(profile_cache_service.get_cached_profile(self.user))

        self.assertEqual(result, cached_profile)

    @patch("users.services.profile_cache_service.cache")
    @patch("users.services.profile_cache_service.get_cached_user_settings", new_callable=AsyncMock)
    @patch("users.services.profile_cache_service.get_cached_user_status", new_callable=AsyncMock)
    @patch("users.services.profile_cache_service.UserProfile")
    def test_get_cached_profile_exception(self, mock_UserProfile, mock_status, mock_settings, mock_cache):
        mock_cache.get.return_value = None
        mock_UserProfile.objects.get_or_create.side_effect = Exception("Database error")
        mock_settings.return_value = {}
        mock_status.return_value = {}

        result = asyncio.run(profile_cache_service.get_cached_profile(self.user))

        expected_result = {
            'user': {
                'id': str(self.user.id),
                'name': self.user.name,
                'surname': self.user.surname,
                'email': self.user.email,
                'role': self.user.role
            },
            'settings': {},
            'profile': {}
        }
        self.assertEqual(result, expected_result)

    @patch("users.services.profile_cache_service.cache")
    def test_invalidate_user_existence_cache(self, mock_cache):
        mock_cache.delete = Mock()

        asyncio.run(profile_cache_service.invalidate_user_existence_cache(self.user.email))

        mock_cache.delete.assert_called_once()

    @patch("users.services.profile_cache_service.cache")
    def test_invalidate_user_cache(self, mock_cache):
        mock_cache.delete_many = Mock()

        asyncio.run(profile_cache_service.invalidate_user_cache(self.user.id))

        mock_cache.delete_many.assert_called_once()

    @patch("users.services.profile_cache_service.invalidate_user_cache", new_callable=AsyncMock)
    @patch("users.services.profile_cache_service.invalidate_user_existence_cache", new_callable=AsyncMock)
    def test_invalidate_all_user_caches(self, mock_existence, mock_user_cache):
        asyncio.run(profile_cache_service.invalidate_all_user_caches(self.user))

        self.assertTrue(mock_existence.called or mock_user_cache.called)

    @patch("users.services.profile_cache_service.invalidate_user_cache", new_callable=AsyncMock)
    @patch("users.services.profile_cache_service.invalidate_user_existence_cache", new_callable=AsyncMock)
    @patch("users.services.profile_cache_service.logger")
    def test_invalidate_all_user_caches_with_email(self, mock_logger, mock_invalidate_existence, mock_invalidate_user):
        mock_invalidate_user.return_value = 3
        mock_invalidate_existence.return_value = True

        result = asyncio.run(profile_cache_service.invalidate_all_user_caches(1, "test@example.com"))

        mock_invalidate_user.assert_called_once_with(1)
        mock_invalidate_existence.assert_called_once_with("test@example.com")
        self.assertEqual(result, 4)
        mock_logger.info.assert_called_once()

    @patch("users.services.profile_cache_service.invalidate_user_cache", new_callable=AsyncMock)
    @patch("users.services.profile_cache_service.invalidate_user_existence_cache", new_callable=AsyncMock)
    @patch("users.services.profile_cache_service.logger")
    def test_invalidate_all_user_caches_without_email(self, mock_logger, mock_invalidate_existence,
                                                      mock_invalidate_user):
        mock_invalidate_user.return_value = 3

        result = asyncio.run(profile_cache_service.invalidate_all_user_caches(1))

        mock_invalidate_user.assert_called_once_with(1)
        mock_invalidate_existence.assert_not_called()
        self.assertEqual(result, 3)
        mock_logger.info.assert_called_once()

    @patch("users.services.profile_cache_service.cache")
    def test_invalidate_user_settings_cache(self, mock_cache):
        mock_cache.delete = Mock()

        asyncio.run(profile_cache_service.invalidate_user_settings_cache(self.user.id))

        mock_cache.delete.assert_called_once_with(f"user_settings_{self.user.id}")

    @patch("users.services.profile_cache_service.cache")
    def test_invalidate_user_profile_cache(self, mock_cache):
        mock_cache.delete = Mock()

        asyncio.run(profile_cache_service.invalidate_user_profile_cache(self.user.id))

        mock_cache.delete.assert_called_once_with(f"user_profile_{self.user.id}")

    @patch("users.services.profile_cache_service.get_cached_profile", new_callable=AsyncMock)
    @patch("users.services.profile_cache_service.get_user_existence_cache", new_callable=AsyncMock)
    def test_warm_user_cache(self, mock_existence, mock_profile):
        mock_profile.return_value = {"user": {"id": str(self.user.id)}}

        asyncio.run(profile_cache_service.warm_user_cache(self.user))

        mock_profile.assert_called_once()
        mock_existence.assert_called_once()

    @patch("users.services.profile_cache_service.get_cached_profile", new_callable=AsyncMock)
    @patch("users.services.profile_cache_service.logger")
    def test_warm_user_cache_exception(self, mock_logger, mock_profile):
        mock_profile.side_effect = Exception("Cache error")

        asyncio.run(profile_cache_service.warm_user_cache(self.user))

        mock_profile.assert_called_once_with(self.user)
        mock_logger.error.assert_called_once()
