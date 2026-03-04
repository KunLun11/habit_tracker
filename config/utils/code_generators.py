import secrets


def email_confirmation_code_generate() -> str:
    return "".join(secrets.choice("0123456789") for i in range(6))


def phone_confiramtion_code_generate() -> str:
    return "".join(secrets.choice("0123456789") for i in range(4))
