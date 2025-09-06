"""BaseModel
Клас: абстрактна база для моделей з UUID primary key.

Поля:
- id: UUIDField — первинний ключ, генерується за замовчуванням через uuid.uuid4, не редагується.

Meta:
- abstract = True
"""

import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
