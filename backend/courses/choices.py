from django.utils.translation import gettext_lazy as _

LEVELS = [
    ('beginner', _('Beginner')),
    ('intermediate', _('Intermediate')),
    ('advanced', _('Advanced')),
]
VALID_CATEGORY_LEVELS = {key for key, _ in LEVELS}

COMPLETED_STATUS = [
    ('not_started', _('Not Started')),
    ('in_progress', _('In Progress')),
    ('completed', _('Completed')),
]
VALID_COMPLETED_STATUS = {key for key, _ in COMPLETED_STATUS}

SORTING_OPTIONS = [
    ('most_popular', '-details__number_completed'),
    ('highest_rated', '-details__rating'),
    ('newest', '-published_at'),
    ('oldest', 'published_at'),
]
VALID_SORTING_OPTIONS = {key for key, _ in SORTING_OPTIONS}
SORTING_DICT = dict(SORTING_OPTIONS)

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
    ('video', _('Video')),              # Відеоурок: лекції, демонстрації, скринкасти
    ('audio', _('Audio')),              # Аудіоуроки: подкасти, голосові пояснення
    ('document', _('Document')),        # Текстові документи: DOCX, TXT, Google Docs
    ('presentation', _('Presentation')), # Презентації: PPTX, Keynote, Google Slides
    ('link', _('Link')),                # Зовнішнє посилання на ресурс або матеріал
    ('custom', _('Custom')),            # Кастомний тип уроку для розширень
]
VALID_CATEGORIES_LESSONS = {key for key, _ in CATEGORY_LESSONS}

CERTIFICATE_STATUS = [
    ('active', _('Active')),
    ('revoked', _('Revoked')),
    ('expired', _('Expired')),
]
VALID_CERTIFICATE_STATUS = {key for key, _ in CERTIFICATE_STATUS}
