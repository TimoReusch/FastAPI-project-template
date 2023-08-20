from .mail_engine import text, button
from src.config.config import FRONTEND_URL, APP_NAME


def reset_password_template(reset_token: str, user_id: int, name: str):
    link = FRONTEND_URL + "auth/change-password/?id=" + format(user_id) + "&token=" + format(reset_token)
    introduction_html = text(f"""
    Hey {name},<br>
    <br>
    please follow this link to reset your password for {APP_NAME}:
    """)

    button_html = button("Reset password", link)

    subtext_html = text("This link is valid for one hour.")

    body_html = f"""
        {introduction_html}
        {button_html}
        {subtext_html}
    """

    return body_html
