from django.utils.translation import gettext


def get_verification_email_html(greeting, activation_url):
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9e9e9; border-radius: 5px;">
          <h2 style="color: #4a4a4a;">{greeting}</h2>
          <p>{gettext('Thank you for registering with SmartStudy!')}</p>
          <p>{gettext('To complete your registration and activate your account, please confirm your email address.')}</p>
          <p style="margin: 25px 0;">
            <a href="{activation_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block;">
              {gettext('Confirm email')}
            </a>
          </p>
          <p>{gettext('If you have not registered with SmartStudy, please disregard this letter.')}</p>
          <p>{gettext('Sincerely,')}<br>{gettext('The SmartStudy team')}</p>
        </div>
      </body>
    </html>
    """


def get_verification_email_plain(greeting, activation_url):
    return f"""
    {greeting}

    {gettext('Thank you for registering with SmartStudy!')}

    {gettext(
        'To complete your registration and activate your account, please confirm your email address by clicking on the link:'
    )}
    {activation_url}

    {gettext('If you have not registered with SmartStudy, please disregard this letter.')}

    {gettext('Sincerely,')}
    {gettext('The SmartStudy Team')}
    """


def get_password_reset_email_html(greeting, reset_url):
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9e9e9; border-radius: 5px;">
          <h2 style="color: #4a4a4a;">{greeting}</h2>
          <p>{gettext('You have received this letter because a request has been made to reset the password for your SmartStudy account.')}</p>
          <p>{gettext('To reset your password, please follow the link below:')}</p>
          <p style="margin: 25px 0;">
            <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block;">
              {gettext('Reset password')}
            </a>
          </p>
          <p>{gettext('If you did not request a password reset, please ignore this email.')}</p>
          <p>{gettext('Sincerely,')}<br>{gettext('The SmartStudy team')}</p>
        </div>
      </body>
    </html>
    """


def get_password_reset_email_plain(greeting, reset_url):
    return f"""
    {greeting}

    {gettext(
        'You have received this letter because a request has been made to reset the password for your SmartStudy account.'
    )}

    {gettext('To reset your password, please follow this link:')}
    {reset_url}

    {gettext('If you did not request a password reset, please ignore this email.')}

    {gettext('Sincerely,')}
    {gettext('The SmartStudy Team')}
    """
