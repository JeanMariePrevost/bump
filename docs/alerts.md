# Alerts and Notifications

BUMP provides basic alert / notifications capabilities to keep you informed about the status of your monitored resources. You can configure these settings via the GUI in the **"Settings"** tab, or manually in the **"./config/app_config.yaml"** file.

---

## Enabling / Disabling Alerts Globally
- You can set the global state of each alert type (toast, email, SMS) in the settings panel.

---

## Configuring SMTP Settings
BUMP uses SMTP to send both email and SMS alerts through email-to-SMS services offered by most providers.

SMTP server settings will be provided by your service provider, and include:

- SMTP Server (e.g. smtp.gmail.com)
- SMTP Port (e.g. 587)
- Username (e.g. your.email@example.com)
- SMTP Password \*
- Target email address for email alerts
- Target email address for email-to-SMS alerts (e.g. yournumber@txt.twilio.com, yournumber@vtext.com, etc.)

**\* Notes on password management**

- The SMTP password is entered during setup by clicking the **"Change"** button in the settings.
- It is securely stored using the OS credentials manager via the [keyring library](https://pypi.org/project/keyring/)
- The password is never stored in plaintext in the configuration file.
- We recommend using a designated account and password specifically for this service to ensure proper security and access control.
