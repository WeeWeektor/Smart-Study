from django.utils.translation import gettext_lazy as _

COURSE_LEVELS = [
    ('starting', _('Starting')),
    ('intermediate', _('Intermediate')),
    ('advanced', _('Advanced')),
]

USER_ROLES = [
    ('admin', _('Admin')),
    ('student', _('Student')),
    ('teacher', _('Teacher')),
]

CATEGORY_CHOICES = [
    ('programming', _('Programming')),
    ('data_science', _('Data Science')),
    ('design', _('Design')),
    ('marketing', _('Marketing')),
    ('business', _('Business')),
    ('personal_development', _('Personal Development')),
    ('health_fitness', _('Health & Fitness')),
    ('music', _('Music')),
    ('photography', _('Photography')),
    ('language_learning', _('Language Learning')),
]

CATEGORY_LESSONS = [
    ('video', _('Video')),
    ('document', _('Document')),
    ('pdf', _('PDF')),
    ('image', _('Image')),
    ('link', _('Link')),
    ('code', _('Code')),
    ('text', _('Text')),
    ('custom', _('Custom')),
]

CERTIFICATE_STATUS = [
    ('active', _('Active')),
    ('revoked', _('Revoked')),
    ('expired', _('Expired')),
]
