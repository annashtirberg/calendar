from fastapi.templating import Jinja2Templates
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import EmailStr

from config import get_settings

templates = Jinja2Templates(directory="templates")

CALENDAR_SITE_NAME = "Calendar"  # application name
CALENDAR_HOME_PAGE = "calendar.com"  # link to the home page of the application
CALENDAR_REGISTRATION_PAGE = r"calendar\registration.com"  # link to the application registration page


def verify_email_pattern(email: str) -> bool:
    return EmailStr.validate(email)


async def send_fast_email(msg: MessageSchema):
    settings = get_settings()
    mail_conf = ConnectionConfig(
        MAIL_USERNAME=settings.smtp_username,
        MAIL_PASSWORD=settings.smtp_password,
        MAIL_FROM=settings.smtp_from_email,
        MAIL_PORT=settings.smtp_port,
        MAIL_SERVER=settings.smtp_server,
        MAIL_TLS=settings.smtp_use_tls,
        MAIL_SSL=settings.smtp_use_ssl,
        USE_CREDENTIALS=settings.smtp_use_credentials,
    )
    fast_mail = FastMail(mail_conf)
    await fast_mail.send_message(msg)


async def send_fast_email_invitation(sender_name: str, recipient_name: str, recipient_mail: str):
    if not verify_email_pattern(recipient_mail):
        return False

    template = templates.get_template("invite_mail.html")
    html = template.render(recipient=recipient_name, sender=sender_name,
                           site_name=CALENDAR_SITE_NAME, registration_link=CALENDAR_REGISTRATION_PAGE,
                           home_link=CALENDAR_HOME_PAGE, addr_to=recipient_mail)

    message = MessageSchema(
        subject="Invitation",
        recipients=[recipient_mail],
        body=html,
        subtype="html",
    )

    await send_fast_email(message)
    return True