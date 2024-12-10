import { NavbarComponent } from "./NavbarComponent.js";
import { requestAppSettings, requestEnterNewSmtpPassword, requestDeleteSmtpPassword, requestSmtpPasswordExists, submitAppSettings } from "./PythonJsBridge.js";
import { FormCardHelper } from "./FormCardHelper.js";
import { applyTheme } from "./utils.js";

let formHelper;

// Wait for DOM content to be fully loaded before executing the fetch
document.addEventListener("DOMContentLoaded", () => {
  // Add the navbar to the page
  const navBar = new NavbarComponent(".navbar-container");
});

window.addEventListener("pywebviewready", function () {
  applyTheme();

  // Load the settings into the form
  requestAppSettings().then((settings) => {
    try {
      document.getElementById("general_interval").value = settings.general_interval;
      document.getElementById("general_log_level").value = settings.general_log_level;
      document.getElementById("general_theme").value = settings.general_theme;
      document.getElementById("alerts_use_toast").value = settings.alerts_use_toast.toString();
      document.getElementById("alerts_use_email").value = settings.alerts_use_email.toString();
      document.getElementById("alerts_use_sms").value = settings.alerts_use_sms.toString();
      document.getElementById("smtp_server").value = settings.smtp_server;
      document.getElementById("smtp_port").value = settings.smtp_port;
      document.getElementById("smtp_username").value = settings.smtp_username;
      document.getElementById("smtp_target_email").value = settings.smtp_target_email;
      document.getElementById("smtp_target_email_for_sms").value = settings.smtp_target_email_for_sms;

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
  formHelper = new FormCardHelper(document.querySelector(".form-card"), handleFormSubmit);
  formHelper.saveFormSnapshot();

  // Add validation conditions
  formHelper.addValidationRule("general_interval", "isPositiveInteger");
  formHelper.addCustomValidationRule("general_theme", (value) => (value.toLowerCase() === "dark" || value.toLowerCase() === "light" ? true : "Invalid theme value"));
  formHelper.addValidationRule("alerts_use_toast", "isBoolean");
  formHelper.addValidationRule("alerts_use_email", "isBoolean");
  formHelper.addValidationRule("alerts_use_sms", "isBoolean");
  formHelper.addValidationRule("smtp_server", "isNotEmpty");
  formHelper.addValidationRule("smtp_port", "isNonNegativeInteger");
  formHelper.addValidationRule("smtp_username", "isNotEmpty");
  formHelper.addValidationRule("smtp_target_email", "isEmail");
  formHelper.addValidationRule("smtp_target_email_for_sms", "isEmail");
}

function handleFormSubmit(formData) {
  console.log("Form submitted with data: ", formData);

  // if general_interval from formData differs from the one in the FormHelper's snapshot, a restart is required
  let restartRequired = false;
  try {
    restartRequired = formData.general_interval !== formHelper.getSnapshot().general_interval;
  } catch (error) {
    console.error("Error checking interval change: ", error);
  }

  submitAppSettings(formData).then((response) => {
    if (response === "true") {
      console.log("Settings saved successfully!");

      if (restartRequired) {
        // Alter the user
        alert("Some settings require a restart to take effect.");
      }
      // Reload page
      location.reload();
    } else {
      alert("Could not save settings: " + response);
    }
  });
}
