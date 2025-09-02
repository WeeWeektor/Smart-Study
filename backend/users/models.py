import uuid
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
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
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    surname = models.CharField(max_length=100, verbose_name=_('Surname'))
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Phone number'))
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    is_verified_email = models.BooleanField(default=False, verbose_name=_('Is email verified'))
    role = models.CharField(max_length=50, verbose_name=_('Role'), choices=[
        ('admin', _('Admin')),
        ('student', _('Student')),
        ('teacher', _('Teacher')),
    ])
    is_active = models.BooleanField(default=False, verbose_name=_('Is active'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Is staff'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']
    objects = CustomUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile', verbose_name=_('User'))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_picture = models.URLField(max_length=500, blank=True, null=True, verbose_name=_('Profile Picture'))
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Location'))
    organization = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('Organization'))
    specialization = models.CharField(max_length=150, blank=True, null=True, verbose_name=_('Specialization'))
    education_level = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Education Level'), choices=[
        ('bachelor', _('Bachelor')),
        ('master', _('Master')),
        ('doctor of science', _('Doctor of Science')),
        ('diploma', _('Diploma')),
        ('certificate', _('Certificate')),
    ])
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name=_('About me'))

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"{_('Profile')} {self.user.name} {self.user.surname}"


class UserSettings(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='settings', verbose_name=_('User'))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_notifications = models.BooleanField(default=True, verbose_name=_('Email notifications'))
    push_notifications = models.BooleanField(default=True, verbose_name=_('Push notifications'))
    deadline_reminders = models.BooleanField(default=True, verbose_name=_('Deadline reminders'))
    show_profile_to_others = models.BooleanField(default=True, verbose_name=_('Show profile to others'))
    show_achievements = models.BooleanField(default=True, verbose_name=_('Show achievements'))

    class Meta:
        verbose_name = _('User Settings')
        verbose_name_plural = _('User Settings')
