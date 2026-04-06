import asyncio
from unittest.mock import Mock, AsyncMock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from users.services import profile_update_service
from users.services.profile_update_service import update_user_data, update_user_profile


class TestProfileUpdateService(TestCase):
    def setUp(self):
        self.user = Mock()
        self.user.name = "Test"
        self.user.surname = "User"
        self.user.phone_number = None
        self.user.save = Mock()

    @patch('users.services.profile_update_service.sync_to_async')
    def test_update_user_data_name_and_surname(self, mock_sync_to_async):
        mock_sync_to_async.return_value = AsyncMock()

        data = {
            'name': 'NewName',
            'surname': 'NewSurname'
        }

        asyncio.run(profile_update_service.update_user_data(self.user, data))

        self.assertEqual(self.user.name, 'NewName')
        self.assertEqual(self.user.surname, 'NewSurname')
        mock_sync_to_async.assert_called_once_with(self.user.save)

    @patch('users.services.profile_update_service.sync_to_async')
    def test_update_user_data_empty_name_surname(self, mock_sync_to_async):
        mock_sync_to_async.return_value = AsyncMock()

        data = {'name': '', 'surname': ''}

        asyncio.run(update_user_data(self.user, data))

        self.assertEqual(self.user.name, "Test")
        self.assertEqual(self.user.surname, "User")

        mock_sync_to_async.assert_not_called()

    @patch("users.services.profile_update_service.sync_to_async")
    @patch("users.services.profile_update_service.phone_validator")
    def test_update_user_data_valid_phone(self, mock_phone_validator, mock_sync_to_async):
        mock_sync_to_async.return_value = AsyncMock()
        mock_phone_validator.return_value = None

        data = {
            'phone_number': '+380123456789'
        }

        asyncio.run(profile_update_service.update_user_data(self.user, data))

        self.assertEqual(self.user.phone_number, '+380123456789')
        mock_phone_validator.assert_called_once_with('+380123456789')

    @patch("users.services.profile_update_service.sync_to_async")
    def test_update_user_data_phone_none(self, mock_sync_to_async):
        mock_sync_to_async.return_value = AsyncMock()

        data = {
            'phone_number': None
        }

        asyncio.run(profile_update_service.update_user_data(self.user, data))

        self.assertIsNone(self.user.phone_number)

    @patch("users.services.profile_update_service.sync_to_async")
    def test_update_user_data_phone_empty_string(self, mock_sync_to_async):
        mock_sync_to_async.return_value = AsyncMock()

        data = {
            'phone_number': '   '
        }

        asyncio.run(profile_update_service.update_user_data(self.user, data))

        self.assertIsNone(self.user.phone_number)

    @patch("users.services.profile_update_service.sync_to_async")
    @patch("users.services.profile_update_service.phone_validator")
    def test_update_user_data_invalid_phone(self, mock_phone_validator, mock_sync_to_async):
        mock_sync_to_async.return_value = AsyncMock()
        mock_phone_validator.side_effect = ValidationError(["Invalid phone number"])

        data = {
            'phone_number': 'invalid_phone'
        }

        with self.assertRaises(ValidationError) as cm:
            asyncio.run(profile_update_service.update_user_data(self.user, data))

        self.assertIn("Invalid phone number", str(cm.exception))

    @patch("users.services.profile_update_service.sync_to_async")
    @patch("users.services.profile_update_service.UserSettings")
    def test_update_user_settings_regular_data(self, mock_UserSettings, mock_sync_to_async):
        mock_user_settings = Mock()
        mock_UserSettings.objects.get_or_create.return_value = (mock_user_settings, True)
        mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func())

        data = {
            'email_notifications': True,
            'push_notifications': False,
            'deadline_reminders': True,
            'show_profile_to_others': False,
            'show_achievements': True
        }

        asyncio.run(profile_update_service.update_user_settings(self.user, data))

        self.assertTrue(mock_user_settings.email_notifications)
        self.assertFalse(mock_user_settings.push_notifications)
        self.assertTrue(mock_user_settings.deadline_reminders)
        self.assertFalse(mock_user_settings.show_profile_to_others)
        self.assertTrue(mock_user_settings.show_achievements)

    @patch("users.services.profile_update_service.sync_to_async")
    @patch("users.services.profile_update_service.UserSettings")
    def test_update_user_settings_multipart_data(self, mock_UserSettings, mock_sync_to_async):
        mock_user_settings = Mock()
        mock_UserSettings.objects.get_or_create.return_value = (mock_user_settings, False)
        mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func())

        data = {
            'email_notifications': 'true',
            'push_notifications': 'false',
            'deadline_reminders': 'True',
            'show_profile_to_others': 'FALSE'
        }

        asyncio.run(profile_update_service.update_user_settings(self.user, data, is_multipart=True))

        self.assertTrue(mock_user_settings.email_notifications)
        self.assertFalse(mock_user_settings.push_notifications)
        self.assertTrue(mock_user_settings.deadline_reminders)
        self.assertFalse(mock_user_settings.show_profile_to_others)

    @patch("users.services.profile_update_service.sync_to_async")
    @patch("users.services.profile_update_service.UserSettings")
    def test_update_user_settings_partial_data(self, mock_UserSettings, mock_sync_to_async):
        mock_user_settings = Mock(spec=['email_notifications', 'save'])
        mock_UserSettings.objects.get_or_create.return_value = (mock_user_settings, True)
        mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func())

        data = {
            'email_notifications': True,
            'other_field': 'ignored'
        }

        asyncio.run(profile_update_service.update_user_settings(self.user, data))

        self.assertTrue(mock_user_settings.email_notifications)
        self.assertFalse(hasattr(mock_user_settings, 'other_field'))

    @patch("users.services.profile_update_service.sync_to_async")
    @patch("users.services.profile_update_service.UserProfile")
    def test_update_user_profile_all_fields(self, mock_UserProfile, mock_sync_to_async):
        mock_user_profile = Mock()
        mock_UserProfile.objects.get_or_create.return_value = (mock_user_profile, True)
        mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func())

        data = {
            'bio': 'My bio',
            'location': 'Kyiv',
            'organization': 'Tech Company',
            'specialization': 'Python Developer',
            'education_level': 'Masters'
        }

        asyncio.run(profile_update_service.update_user_profile(self.user, data))

        self.assertEqual(mock_user_profile.bio, 'My bio')
        self.assertEqual(mock_user_profile.location, 'Kyiv')
        self.assertEqual(mock_user_profile.organization, 'Tech Company')
        self.assertEqual(mock_user_profile.specialization, 'Python Developer')
        self.assertEqual(mock_user_profile.education_level, 'Masters')

    @patch("users.services.profile_update_service.sync_to_async")
    @patch("users.services.profile_update_service.UserProfile")
    def test_update_user_profile_partial_fields(self, mock_UserProfile, mock_sync_to_async):
        mock_user_profile = Mock(spec=['bio', 'location', 'save'])
        mock_UserProfile.objects.get_or_create.return_value = (mock_user_profile, False)
        mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func())

        data = {
            'bio': 'Updated bio',
            'location': 'Lviv',
            'unknown_field': 'ignored'
        }

        asyncio.run(profile_update_service.update_user_profile(self.user, data))

        self.assertEqual(mock_user_profile.bio, 'Updated bio')
        self.assertEqual(mock_user_profile.location, 'Lviv')
        self.assertFalse(hasattr(mock_user_profile, 'unknown_field'))

    @patch("users.services.profile_update_service.sync_to_async")
    @patch("users.services.profile_update_service.UserProfile")
    def test_update_user_profile_empty_data(self, mock_UserProfile, mock_sync_to_async):
        mock_user_profile = Mock()
        mock_UserProfile.objects.get_or_create.return_value = (mock_user_profile, True)
        mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func())

        data = {}

        asyncio.run(profile_update_service.update_user_profile(self.user, data))

        mock_sync_to_async.assert_called()

    @patch('users.services.profile_update_service.sync_to_async')
    @patch('users.services.profile_update_service.sanitize_input')
    def test_update_user_data_name_too_long(self, mock_sanitize, mock_sync_to_async):
        """Тест перевищення довжини імені"""
        mock_sync_to_async.return_value = AsyncMock()

        data = {'name': 'a' * 101}

        with self.assertRaises(ValidationError) as context:
            asyncio.run(update_user_data(self.user, data))

        self.assertEqual(str(context.exception), "['Name too long']")

    @patch('users.services.profile_update_service.sync_to_async')
    @patch('users.services.profile_update_service.sanitize_input')
    def test_update_user_data_surname_too_long(self, mock_sanitize, mock_sync_to_async):
        """Тест перевищення довжини прізвища"""
        mock_sync_to_async.return_value = AsyncMock()

        data = {'surname': 'b' * 101}

        with self.assertRaises(ValidationError) as context:
            asyncio.run(update_user_data(self.user, data))

        self.assertEqual(str(context.exception), "['Surname too long']")

    @patch('users.services.profile_update_service.sync_to_async')
    @patch('users.services.profile_update_service.sanitize_input')
    def test_update_user_profile_set_field_to_none(self, mock_sanitize, mock_sync_to_async):
        """Тест встановлення поля профілю в None через else гілку"""
        mock_user_profile = Mock()
        mock_user_profile.bio = None
        mock_user_profile.location = None
        mock_user_profile.organization = None
        mock_user_profile.specialization = None
        mock_user_profile.education_level = None

        mock_sync_to_async.side_effect = lambda func: AsyncMock() if 'save' in str(func) else AsyncMock(
            return_value=(mock_user_profile, True))

        test_cases = [
            {'bio': None},
            {'location': ''},
            {'organization': '   '},
            {'specialization': None},
            {'education_level': ''},
        ]

        for data in test_cases:
            with self.subTest(data=data):
                asyncio.run(update_user_profile(self.user, data))

                field_name = list(data.keys())[0]
                self.assertIsNone(getattr(mock_user_profile, field_name))
