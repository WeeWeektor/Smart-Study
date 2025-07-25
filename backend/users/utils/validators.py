from django.core.validators import EmailValidator, RegexValidator

email_validator = EmailValidator(message='Некоректний формат електронної пошти.')
phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{10,15}$',
    message='Номер телефону має містити від 10 до 15 цифр, з префіксом.'
)
