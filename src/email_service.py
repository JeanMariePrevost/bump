import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml

from my_utils import util
from credentials_manager import get_password_from_keyring_or_user, prompt_for_and_save_password
from custom_logging import general_logger


def load_configs() -> None:
    """
    Set module-level variables from the email_config.yaml file.
    """
    # Read from /email_config.yaml
    global smtp_server, smtp_port, username, from_email, to_email, to_email_for_sms
    with open(util.resource_path("config/email_config.yaml"), "r") as file:
        config = yaml.safe_load(file)
        smtp_server = config.get("smtp_server")
        smtp_port = config.get("smtp_port")
        username = config.get("username")
        from_email = config.get("from_email")
        to_email = config.get("to_email")
        to_email_for_sms = config.get("to_email_for_sms")


def send_email_alert(subject, body):
    """
    Send an email alert.
    """
    load_configs()
    __send_smtp_email(subject, body, to_email)


def send_sms_alert(subject, body):
    """
    Send an SMS alert.
    """
    load_configs()
    __send_smtp_email(subject, body, to_email_for_sms)


def __send_smtp_email(subject, body, target_email):
    # Create the email
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = target_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Get the password from the keyring or from the user if it's not stored
    try:
        password = get_password_from_keyring_or_user(username)
    except Exception as e:
        print(f"Failed to get password: {e}")
        return

    # Send the email
    try:

        # DEBUG!!
        print(
            f"SMTP would normally proceed with the following parameters: {smtp_server}, {smtp_port}, {username}, {from_email}, {target_email}, {subject}, {body}, (password hidden)"
        )

        general_logger.debug("email_service.py starting to send email")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(from_email, target_email, msg.as_string())
    except Exception as e:
        general_logger.error(f"Failed to send email: {e}")


load_configs()

if __name__ == "__main__":
    # send_email_alert("Test Subject", "Test Body")
    # send_sms_alert("Test SMS Body")
