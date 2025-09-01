import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext
from django.utils.html import strip_tags


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(gettext('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Name')
    surname = models.CharField(max_length=100, verbose_name='Surname')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Phone number')
    email = models.EmailField(unique=True, verbose_name='Email')
    is_verified_email = models.BooleanField(default=False, verbose_name='Is email verified')
    role = models.CharField(max_length=50, verbose_name='Role', choices=[
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ])
    is_active = models.BooleanField(default=False, verbose_name='Is active')
    is_staff = models.BooleanField(default=False, verbose_name='Is staff')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def clean(self):
        if self.name:
            self.name = strip_tags(self.name)
        if self.surname:
            self.surname = strip_tags(self.surname)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile', verbose_name='User')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_picture = models.URLField(max_length=500, blank=True, null=True, verbose_name='Profile Picture')
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='Location')
    organization = models.CharField(max_length=200, blank=True, null=True, verbose_name='Organization')
    specialization = models.CharField(max_length=150, blank=True, null=True, verbose_name='Specialization')
    education_level = models.CharField(max_length=100, blank=True, null=True, verbose_name='Education Level', choices=[
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('doctor of science', 'Doctor of Science'),
        ('diploma', 'Diploma'),
        ('certificate', 'Certificate'),
    ])
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name='About me')

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{gettext("Profile")} {self.user.name} {self.user.surname}"

    def clean(self):
        if self.bio:
            self.bio = strip_tags(self.bio)
        if self.location:
            self.location = strip_tags(self.location)
        if self.organization:
            self.organization = strip_tags(self.organization)
        if self.specialization:
            self.specialization = strip_tags(self.specialization)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class UserSettings(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='settings', verbose_name='User')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_notifications = models.BooleanField(default=True, verbose_name='Email notifications')
    push_notifications = models.BooleanField(default=True, verbose_name='Push notifications')
    deadline_reminders = models.BooleanField(default=True, verbose_name='Deadline reminders')
    show_profile_to_others = models.BooleanField(default=True, verbose_name='Show profile to others')
    show_achievements = models.BooleanField(default=True, verbose_name='Show achievements')

    class Meta:
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'
