import { NavbarComponent } from "./NavbarComponent.js";
import { requestAppSettings, requestEnterNewSmtpPassword, requestDeleteSmtpPassword, requestSmtpPasswordExists } from "./PythonJsBridge.js";
import { FormCardHelper } from "./FormCardHelper.js";

// Wait for DOM content to be fully loaded before executing the fetch
document.addEventListener("DOMContentLoaded", () => {
  // Add the navbar to the page
  const navBar = new NavbarComponent(".navbar-container");
});

window.addEventListener("pywebviewready", function () {
  // Load the settings into the form
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

      initializeFormHelper();
    } catch (error) {
      console.error("Error loading settings into form: ", error);
    }
  });

  // Enable/disable the remove password button based on whether a password is stored
  requestSmtpPasswordExists().then((exists) => {
    document.getElementById("remove-password").disabled = !exists;
  });

  // Add event listeners to change/remove the stored SMTP password
  document.getElementById("change-password").addEventListener("click", () => {
    requestEnterNewSmtpPassword().then((response) => {
      if (response === "true") {
        alert("Password changed successfully!");
        location.reload(); // Reload the page
      } else {
        alert("Error storing password: " + response);
      }
    });
  });

  document.getElementById("remove-password").addEventListener("click", () => {
    // First confirm with user
    const confirmDelete = confirm("Are you sure you want to remove the stored password?");
    if (!confirmDelete) {
      return;
    }
    requestDeleteSmtpPassword().then((response) => {
      if (response === "true") {
        // alert("Password removed successfully!");
        location.reload(); // Reload the page
      } else {
        alert("Error removing password: " + response);
      }
    });
  });
});

function initializeFormHelper() {
  const formHelper = new FormCardHelper(document.querySelector(".form-card"));
  formHelper.saveFormSnapshot();

  // Add validation conditions
  formHelper.addValidationRule("monitoring-interval", "isPositiveInteger");
  formHelper.addCustomValidationRule("theme", (value) => (value.toLowerCase() === "dark" || value.toLowerCase() === "light" ? true : "Invalid theme value"));
  formHelper.addValidationRule("toasts-enabled", "isBoolean");
  formHelper.addValidationRule("email-enabled", "isBoolean");
  formHelper.addValidationRule("sms-enabled", "isBoolean");
  formHelper.addValidationRule("smtp-server", "isNotEmpty");
  formHelper.addValidationRule("smtp-port", "isNonNegativeInteger");
  formHelper.addValidationRule("username", "isNotEmpty");
  formHelper.addValidationRule("to-email", "isEmail");
  formHelper.addValidationRule("to-email-for-sms", "isEmail");
}
