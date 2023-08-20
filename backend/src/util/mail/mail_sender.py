from .mail_engine import send_mail
from .templates import *
from pydantic import EmailStr
from src.config.config import APP_NAME


async def send_password_reset_mail(mail: EmailStr, user_id: int, reset_token: str, user_name: str):
    await send_mail(
        mail,
        f"{APP_NAME} - Passwort reset",
        reset_password_template(reset_token, user_id, user_name)
    )
