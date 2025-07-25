def get_verification_email_html(greeting, activation_url):
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9e9e9; border-radius: 5px;">
          <h2 style="color: #4a4a4a;">{greeting}</h2>
          <p>Дякуємо за реєстрацію в системі SmartStudy!</p>
          <p>Для завершення реєстрації та активації облікового запису, будь ласка, підтвердіть свою електронну пошту.</p>
          <p style="margin: 25px 0;">
            <a href="{activation_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block;">
              Підтвердити електронну пошту
            </a>
          </p>
          <p>Якщо ви не реєструвались на SmartStudy, проігноруйте цей лист.</p>
          <p>З повагою,<br>Команда SmartStudy</p>
        </div>
      </body>
    </html>
    """

def get_verification_email_plain(greeting, activation_url):
    return f"""
    {greeting}

    Дякуємо за реєстрацію в системі SmartStudy!

    Для завершення реєстрації та активації облікового запису, будь ласка, підтвердіть свою електронну пошту за посиланням:
    {activation_url}

    Якщо ви не реєструвались на SmartStudy, проігноруйте цей лист.

    З повагою,
    Команда SmartStudy
    """

def get_password_reset_email_html(greeting, reset_url):
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9e9e9; border-radius: 5px;">
          <h2 style="color: #4a4a4a;">{greeting}</h2>
          <p>Ви отримали цей лист, оскільки надійшов запит на відновлення пароля для вашого облікового запису в системі SmartStudy.</p>
          <p>Щоб скинути пароль, будь ласка, перейдіть за посиланням нижче:</p>
          <p style="margin: 25px 0;">
            <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block;">
              Скинути пароль
            </a>
          </p>
          <p>Якщо ви не запитували відновлення пароля, проігноруйте цей лист.</p>
          <p>З повагою,<br>Команда SmartStudy</p>
        </div>
      </body>
    </html>
    """

def get_password_reset_email_plain(greeting, reset_url):
    return f"""
    {greeting}

    Ви отримали цей лист, оскільки надійшов запит на відновлення пароля для вашого облікового запису в системі SmartStudy.

    Щоб скинути пароль, будь ласка, перейдіть за посиланням:
    {reset_url}

    Якщо ви не запитували відновлення пароля, проігноруйте цей лист.

    З повагою,
    Команда SmartStudy
    """
