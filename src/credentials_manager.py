import tkinter
from tkinter import simpledialog
import keyring

KEYRING_SERVICE_NAME = "BUMP SMTP Credentials"

# TODO - Allow changing the password through the GUI? Right now, if it exists, it will ALWAYS load without prompting the user
# You can use the force_prompt_user parameter to force the user to enter the password again


def get_password_from_keyring_or_user(for_username: str, force_prompt_user: bool = False) -> str:
    """
    Get the value for a key from keyring. If the key does not exist, prompt the user for the value and store it in keyring.
    """
    value = keyring.get_password(KEYRING_SERVICE_NAME, for_username)
    if value is None or force_prompt_user:
        title = "Enter SMTP Password"
        message = f"We could not find a password stored for {for_username}.\n\nPlease enter the password, which will be stored through the OS credentials/keyring service."
        value = prompt_for_and_save_password(for_username=for_username, title=title, message=message)
    return value


def prompt_for_and_save_password(for_username: str, title: str, message: str) -> str:
    """
    Prompt the user for a password using a tkinter dialog and store it in keyring.
    Will overwrite any existing password stored for the given username.
    Returns:
        str: The password entered by the user.
    """
    # Prompt user for a password using tkinter
    root = tkinter.Tk()
    root.withdraw()  # Hide the root window

    password = PasswordDialog(parent=root, title=title, message=message).result

    keyring.set_password(KEYRING_SERVICE_NAME, for_username, password)
    return password


class PasswordDialog(simpledialog.Dialog):
    """
    A simple dialog to prompt the user for a password. The password is stored in the result attribute after the dialog is closed.
    """

    def __init__(self, parent, title, message: str):
        self.result = None
        self.title_str = title
        self.message_str = message
        super().__init__(parent)
        # self.body(parent, message)

    def body(self, master):
        self.title(self.title_str)

        # Adjust dialog size
        # self.geometry("300x140")  # Width x Height in pixels

        # Add label with proper padding
        tkinter.Label(master, text=self.message_str).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        # Add entry field for the password
        self.password_var = tkinter.StringVar()
        self.password_entry = tkinter.Entry(master, textvariable=self.password_var, show="*", width=40)
        self.password_entry.grid(row=1, column=0, padx=20, pady=(10, 15))

        return self.password_entry  # Focus the password entry box by default

    def apply(self):
        self.result = self.password_var.get()  # Retrieve the entered password
