from django.core.signing import TimestampSigner

signer = TimestampSigner()


def generate_activation_token(email):
    return signer.sign(email)
