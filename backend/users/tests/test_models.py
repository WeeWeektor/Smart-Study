import uuid

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
        expected = f"User {user.name} {user.surname}"
        self.assertEqual(str(user), expected)

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

    def test_user_uuid_primary_key(self):
        """Тест UUID первинного ключа"""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertTrue(isinstance(user.id, uuid.UUID))

    def test_user_email_uniqueness(self):
        """Тест унікальності email"""
        CustomUser.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(
                email='test@example.com',
                name='Jane',
                surname='Doe',
                password='password456',
                role='teacher'
            )

    def test_user_default_values(self):
        """Тест значень за замовчуванням"""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertFalse(user.is_verified_email)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertIsNotNone(user.created_at)

    def test_custom_manager_get_with_profile_and_settings(self):
        """Тест кастомного менеджера"""
        user = CustomUser.objects.create_user(**self.user_data)
        UserProfile.objects.create(user=user)
        UserSettings.objects.create(user=user)

        retrieved_user = CustomUser.objects.get_with_profile_and_settings(id=user.id)
        self.assertEqual(retrieved_user, user)

    def test_user_phone_number_optional(self):
        """Тест опціонального номера телефону"""
        user_data = self.user_data.copy()
        user_data['phone_number'] = '+380123456789'
        user = CustomUser.objects.create_user(**user_data)
        self.assertEqual(user.phone_number, '+380123456789')

    def test_user_meta_verbose_names(self):
        """Тест verbose_name моделі"""
        self.assertEqual(CustomUser._meta.verbose_name, 'User')
        self.assertEqual(CustomUser._meta.verbose_name_plural, 'Users')

    def test_user_indexes_exist(self):
        """Тест наявності індексів"""
        indexes = [index.name for index in CustomUser._meta.indexes]
        self.assertTrue(len(indexes) > 0)


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

    def test_profile_uuid_primary_key(self):
        """Тест UUID первинного ключа профілю"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertTrue(isinstance(profile.id, uuid.UUID))

    def test_profile_one_to_one_relationship(self):
        """Тест зв'язку один-до-одного з користувачем"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(self.user.profile, profile)

    def test_profile_cascade_delete(self):
        """Тест каскадного видалення профілю при видаленні користувача"""
        profile = UserProfile.objects.create(user=self.user)
        user_id = self.user.id
        profile_id = profile.id

        self.user.delete()

        self.assertFalse(CustomUser.objects.filter(id=user_id).exists())
        self.assertFalse(UserProfile.objects.filter(id=profile_id).exists())

    def test_valid_education_levels(self):
        """Тест валідних рівнів освіти"""
        valid_levels = ['bachelor', 'master', 'doctor of science', 'diploma', 'certificate']

        for level in valid_levels:
            profile = UserProfile(user=self.user, education_level=level)
            try:
                profile.full_clean()
            except ValidationError:
                self.fail(f"ValidationError raised for valid education level: {level}")

    def test_profile_picture_url_field(self):
        """Тест URL поля для фото профілю"""
        profile = UserProfile.objects.create(
            user=self.user,
            profile_picture='https://example.com/avatar.jpg'
        )
        self.assertEqual(profile.profile_picture, 'https://example.com/avatar.jpg')

    def test_bio_max_length(self):
        """Тест що довгий текст зберігається без обрізання"""
        long_bio = 'x' * 501
        profile = UserProfile.objects.create(user=self.user, bio=long_bio)

        self.assertEqual(len(profile.bio), 501)
        self.assertTrue(profile.bio.endswith('x'))

    def test_bio_field_max_length_property(self):
        """Тест що поле має правильний max_length"""
        bio_field = UserProfile._meta.get_field('bio')
        self.assertEqual(bio_field.max_length, 500)

    def test_bio_full_clean_validation(self):
        """Тест що full_clean не викидає помилку для TextField"""
        long_bio = 'x' * 501
        profile = UserProfile(user=self.user, bio=long_bio)

        try:
            profile.full_clean()
            self.assertEqual(len(profile.bio), 501)
        except ValidationError:
            self.fail("ValidationError не повинна виникати для TextField")

    def test_bio_field_type(self):
        """Тест типу поля bio"""
        bio_field = UserProfile._meta.get_field('bio')
        self.assertEqual(bio_field.__class__.__name__, 'TextField')
        self.assertTrue(bio_field.blank)
        self.assertTrue(bio_field.null)

    def test_profile_meta_verbose_names(self):
        """Тест verbose_name моделі профілю"""
        self.assertEqual(UserProfile._meta.verbose_name, 'User Profile')
        self.assertEqual(UserProfile._meta.verbose_name_plural, 'User Profiles')


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

    def test_settings_uuid_primary_key(self):
        """Тест UUID первинного ключа налаштувань"""
        settings_obj = UserSettings.objects.create(user=self.user)
        self.assertTrue(isinstance(settings_obj.id, uuid.UUID))

    def test_settings_str_method(self):
        """Тест __str__ методу налаштувань"""
        settings_obj = UserSettings.objects.create(user=self.user)
        expected = f"Settings {self.user.name} {self.user.surname}"
        self.assertEqual(str(settings_obj), expected)

    def test_settings_cascade_delete(self):
        """Тест каскадного видалення налаштувань при видаленні користувача"""
        settings_obj = UserSettings.objects.create(user=self.user)
        user_id = self.user.id
        settings_id = settings_obj.id

        self.user.delete()

        self.assertFalse(CustomUser.objects.filter(id=user_id).exists())
        self.assertFalse(UserSettings.objects.filter(id=settings_id).exists())

    def test_settings_default_values(self):
        """Тест значень за замовчуванням для налаштувань"""
        settings_obj = UserSettings.objects.create(user=self.user)
        self.assertTrue(settings_obj.email_notifications)
        self.assertTrue(settings_obj.push_notifications)
        self.assertTrue(settings_obj.deadline_reminders)
        self.assertTrue(settings_obj.show_profile_to_others)
        self.assertTrue(settings_obj.show_achievements)

    def test_settings_boolean_fields(self):
        """Тест булевих полів налаштувань"""
        settings_obj = UserSettings(
            user=self.user,
            email_notifications=False,
            push_notifications=True,
            deadline_reminders=False,
            show_profile_to_others=True,
            show_achievements=False
        )
        settings_obj.save()

        self.assertFalse(settings_obj.email_notifications)
        self.assertTrue(settings_obj.push_notifications)
        self.assertFalse(settings_obj.deadline_reminders)
        self.assertTrue(settings_obj.show_profile_to_others)
        self.assertFalse(settings_obj.show_achievements)

    def test_settings_meta_verbose_names(self):
        """Тест verbose_name моделі налаштувань"""
        self.assertEqual(UserSettings._meta.verbose_name, 'User Settings')
        self.assertEqual(UserSettings._meta.verbose_name_plural, 'User Settings')

    def test_settings_unique_per_user(self):
        """Тест унікальності налаштувань для кожного користувача"""
        UserSettings.objects.create(user=self.user)

        with self.assertRaises(Exception):
            UserSettings.objects.create(user=self.user)
