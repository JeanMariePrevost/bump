import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from credentials_manager import get_password_from_keyring_or_user, prompt_for_and_save_password
from custom_logging import general_logger
from settings_manager import settings


def send_email_alert(subject, body):
    """
    Send an email alert.
    """
    general_logger.debug("email_service.py sending email alert")
    __send_smtp_email(subject, body, settings.to_email)


def send_sms_alert(subject, body):
    """
    Send an SMS alert.
    """
    general_logger.debug("email_service.py sending SMS alert")
    __send_smtp_email(subject, body, settings.smtp_target_email_for_sms)


def __send_smtp_email(subject, body, target_email):
    # Create the email
    msg = MIMEMultipart()
    msg["From"] = settings.smtp_username
    msg["To"] = target_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Get the password from the keyring or from the user if it's not stored
    try:
        password = get_password_from_keyring_or_user(settings.smtp_username)
    except Exception as e:
        print(f"Failed to get password: {e}")
        return

    # Send the email
    try:
        general_logger.debug(f"email_service.py starting to send email to {target_email}")
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, password)
            server.sendmail(settings.smtp_username, target_email, msg.as_string())
    except Exception as e:
        general_logger.error(f"Failed to send email: {e}")


if __name__ == "__main__":
    # send_email_alert("Test Subject", "Test Body")
    # send_sms_alert("Test Subject", "Test Body")
    pass
