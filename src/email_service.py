import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import simpledialog
from my_utils import util
import yaml


def load_configs() -> None:
    """
    Set module-level variables from the email_config.yaml file.
    """
    # Read from /email_config.yaml
    global smtp_server, smtp_port, username, from_email, to_email, subject, body
    with open(util.resource_path("config/email_config.yaml"), "r") as file:
        config = yaml.safe_load(file)
        smtp_server = config.get("smtp_server")
        smtp_port = config.get("smtp_port")
        username = config.get("username")
        from_email = config.get("from_email")
        to_email = config.get("to_email")


class PasswordDialog(simpledialog.Dialog):
    """
    A simple dialog to prompt the user for a password. The password is stored in the result attribute after the dialog is closed.
    """

    def body(self, master):
        self.title("Enter Password")

        # Adjust dialog size
        self.geometry("300x140")  # Width x Height in pixels

        # Add label with proper padding
        tk.Label(master, text="Please enter the sending email account to enable SMTP:").grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        # Add entry field for the password
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(master, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=1, column=0, padx=20, pady=(0, 15))

        return self.password_entry  # Focus the password entry box by default

    def apply(self):
        self.result = self.password_var.get()  # Retrieve the entered password


def send_email():
    # Debug values
    subject = "SubjectGoesHere"  # The subject simply gets placed in parentheses for SMS, i.e. the message is "(subject) body"
    body = "This is the actual message."

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Send the email
    try:
        # Prompt user for a password using tkinter
        root = tk.Tk()
        root.withdraw()  # Hide the root window

        password = PasswordDialog(root).result

        # DEBUG!!
        print(
            f"SMTP would normally proceed with the following parameters: {smtp_server}, {smtp_port}, {username}, {from_email}, {to_email}, {subject}, {body}, {password}"
        )

        # print("Starting to send email...")
        # with smtplib.SMTP(smtp_server, smtp_port) as server:
        #     server.starttls()
        #     print("Logging in...")
        #     server.login(username, password)
        #     print("Sending email...")
        #     server.sendmail(from_email, to_email, msg.as_string())
        # print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    load_configs()
    send_email()
