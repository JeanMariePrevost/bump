import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from common.credentials_manager import get_password_from_keyring_or_user, prompt_for_and_save_password
from common.custom_logging import get_general_logger
from common.settings_manager import settings


def send_email_alert(subject, body):
    """
    Send an email alert.
    """
    get_general_logger().debug("email_service.py sending email alert")
    __send_smtp_email(subject, body, settings.smtp_target_email)


def send_sms_alert(subject, body):
    """
    Send an SMS alert.
    """
    get_general_logger().debug("email_service.py sending SMS alert")
    __send_smtp_email(subject, body, settings.smtp_target_email_for_sms)


def __send_smtp_email(subject, body, target_email):
    # Create the email
    msg = MIMEMultipart()
    try:
        msg["From"] = settings.smtp_username
        msg["To"] = target_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
    except Exception as e:
        get_general_logger().error(f"Failed to create email: {e}")
        return

    # Get the password from the keyring or from the user if it's not stored
    try:
        password = get_password_from_keyring_or_user(settings.smtp_username)
    except Exception as e:
        get_general_logger().error(f"Failed to get SMTP password: {e}")
        return

    # If any requirement is missing, log and return
    if not settings.smtp_server or not settings.smtp_port or not settings.smtp_username or not target_email or not password:
        get_general_logger().warning("Trying to send email/SMS alerts, but SMTP settings are missing or invalid")
        return

    # Send the email
    try:
        get_general_logger().debug(f"email_service.py starting to send email to {target_email}")
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, password)
            server.sendmail(settings.smtp_username, target_email, msg.as_string())
    except Exception as e:
        get_general_logger().error(f"Could not perform SMTP operation: {e}")
        return
