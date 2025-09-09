from django.utils.translation import gettext_lazy as _

LEVELS = [
    ('beginner', _('Beginner')),
    ('intermediate', _('Intermediate')),
    ('advanced', _('Advanced')),
]
VALID_CATEGORY_LEVELS = {key for key, _ in LEVELS}

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
VALID_CATEGORIES_CHOICES = {key for key, _ in CATEGORY_CHOICES}

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
VALID_CATEGORIES_LESSONS = {key for key, _ in CATEGORY_LESSONS}

CERTIFICATE_STATUS = [
    ('active', _('Active')),
    ('revoked', _('Revoked')),
    ('expired', _('Expired')),
]
VALID_CERTIFICATE_STATUS = {key for key, _ in CERTIFICATE_STATUS}
