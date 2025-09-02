from django.core.exceptions import ValidationError
from django.test import TestCase

from users.models import CustomUser, UserProfile, UserSettings


class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'name': 'John',
            'surname': 'Doe',
            'password': 'password123',
            'role': 'student'
        }

    def test_create_user(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.name, self.user_data['name'])
        self.assertEqual(user.surname, self.user_data['surname'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertEqual(user.role, self.user_data['role'])
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_active)

    def test_create_superuser(self):
        superuser = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='adminpass'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.role, 'admin')

    def test_create_user_without_email_raises_error(self):
        with self.assertRaisesMessage(ValueError, 'The Email field must be set'):
            CustomUser.objects.create_user(email='', password='pass')

    def test_user_str_method(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(str(user), user.email)

    def test_invalid_role_raises_validation_error(self):
        user = CustomUser(
            email='invalid@example.com',
            name='Test',
            surname='User',
            role='invalid_role'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_update_user_fields(self):
        user = CustomUser.objects.create_user(**self.user_data)
        user.name = 'UpdatedName'
        user.surname = 'UpdatedSurname'
        user.role = 'teacher'
        user.is_active = True
        user.save()
        updated_user = CustomUser.objects.get(email=self.user_data['email'])
        self.assertEqual(updated_user.name, 'UpdatedName')
        self.assertEqual(updated_user.surname, 'UpdatedSurname')
        self.assertEqual(updated_user.role, 'teacher')
        self.assertTrue(updated_user.is_active)


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='user@example.com',
            password='password123',
            name='Alice',
            surname='Smith',
            role='student'
        )

    def test_create_profile(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertIsNone(profile.location)
        self.assertIsNone(profile.organization)
        self.assertIsNone(profile.specialization)
        self.assertIsNone(profile.education_level)
        self.assertIsNone(profile.bio)
        self.assertIsNone(profile.profile_picture)

    def test_profile_str_method(self):
        profile = UserProfile.objects.create(user=self.user)
        expected_str = f"Profile {self.user.name} {self.user.surname}"
        self.assertEqual(str(profile), expected_str)

    def test_invalid_education_level_raises_validation_error(self):
        profile = UserProfile(user=self.user, education_level='invalid_level')
        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_update_profile_fields(self):
        profile = UserProfile.objects.create(user=self.user)
        profile.location = 'Kyiv'
        profile.organization = 'KPI'
        profile.specialization = 'Computer Science'
        profile.education_level = 'master'
        profile.bio = 'Hello world'
        profile.profile_picture = 'https://example.com/pic.png'
        profile.save()
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.location, 'Kyiv')
        self.assertEqual(updated_profile.organization, 'KPI')
        self.assertEqual(updated_profile.specialization, 'Computer Science')
        self.assertEqual(updated_profile.education_level, 'master')
        self.assertEqual(updated_profile.bio, 'Hello world')
        self.assertEqual(updated_profile.profile_picture, 'https://example.com/pic.png')


class UserSettingsModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='settingsuser@example.com',
            password='password123',
            name='Bob',
            surname='Johnson',
            role='teacher'
        )

    def test_create_user_settings(self):
        settings_obj = UserSettings.objects.create(user=self.user)
        self.assertEqual(settings_obj.user, self.user)
        self.assertTrue(settings_obj.email_notifications)
        self.assertTrue(settings_obj.push_notifications)
        self.assertTrue(settings_obj.deadline_reminders)
        self.assertTrue(settings_obj.show_profile_to_others)
        self.assertTrue(settings_obj.show_achievements)

    def test_one_to_one_relationship(self):
        settings_obj = UserSettings.objects.create(user=self.user)
        self.assertEqual(settings_obj.user.settings, settings_obj)

    def test_update_settings_fields(self):
        settings_obj = UserSettings.objects.create(user=self.user)
        settings_obj.email_notifications = False
        settings_obj.push_notifications = False
        settings_obj.deadline_reminders = False
        settings_obj.show_profile_to_others = False
        settings_obj.show_achievements = False
        settings_obj.save()
        updated_settings = UserSettings.objects.get(user=self.user)
        self.assertFalse(updated_settings.email_notifications)
        self.assertFalse(updated_settings.push_notifications)
        self.assertFalse(updated_settings.deadline_reminders)
        self.assertFalse(updated_settings.show_profile_to_others)
        self.assertFalse(updated_settings.show_achievements)
