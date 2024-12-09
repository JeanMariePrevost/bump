import { NavbarComponent } from "./NavbarComponent.js";
import { requestAppSettings } from "./PythonJsBridge.js";

// Wait for DOM content to be fully loaded before executing the fetch
document.addEventListener("DOMContentLoaded", () => {
  // Add the navbar to the page
  const navBar = new NavbarComponent(".navbar-container");
});

window.addEventListener("pywebviewready", function () {
  // Load the settings into the form
  // For reference:
  // settings = SimpleNamespace(
  //   general_interval=60,
  //   general_theme="dark",
  //   alerts_use_toast=True,
  //   alerts_use_email=False,
  //   alerts_use_sms=False,
  //   smtp_server="",
  //   smtp_port=587,
  //   smtp_username="",
  //   smtp_target_email="",
  //   smtp_target_email_for_sms="",
  // )
  requestAppSettings().then((settings) => {
    try {
      document.getElementById("monitoring-interval").value = settings.general_interval;
      document.getElementById("theme").value = settings.general_theme;
      document.getElementById("toasts-enabled").value = settings.alerts_use_toast.toString();
      document.getElementById("email-enabled").value = settings.alerts_use_email.toString();
      document.getElementById("sms-enabled").value = settings.alerts_use_sms.toString();
      document.getElementById("smtp-server").value = settings.smtp_server;
      document.getElementById("smtp-port").value = settings.smtp_port;
      document.getElementById("username").value = settings.smtp_username;
      document.getElementById("to-email").value = settings.smtp_target_email;
      document.getElementById("to-email-for-sms").value = settings.smtp_target_email_for_sms;
    } catch (error) {
      console.error("Error loading settings into form: ", error);
    }
  });
});
