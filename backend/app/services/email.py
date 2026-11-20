"""Configurable SMTP transport. Never logs message bodies or credentials."""
import smtplib
import ssl
from email.message import EmailMessage
from app.core.config import settings


class EmailDeliveryError(RuntimeError):
    pass


def send_otp(email: str, code: str) -> None:
    if settings.EMAIL_PROVIDER == "development" and settings.ENVIRONMENT == "development":
        return
    if settings.EMAIL_PROVIDER != "smtp" or not settings.SMTP_HOST or not settings.SMTP_FROM:
        raise EmailDeliveryError("Email delivery is not configured")
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = email
    message["Subject"] = "ROOT404 — Your sign-in code"
    message.set_content(f"Your ROOT404 code is {code}. It expires in {settings.OTP_EXPIRE_MINUTES} minutes. Do not share this code.")
    try:
        transport = smtplib.SMTP_SSL if settings.SMTP_SSL else smtplib.SMTP
        kwargs = {"context": ssl.create_default_context()} if settings.SMTP_SSL else {}
        with transport(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10, **kwargs) as smtp:
            if not settings.SMTP_SSL:
                smtp.starttls(context=ssl.create_default_context())
            if settings.SMTP_USERNAME:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryError("Email delivery unavailable") from exc
