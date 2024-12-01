import { BaseComponent } from "./BaseComponent.js";
import { requestSingleMonitor } from "./PythonJsBridge.js";

/**
 * Handles the monitor editing form in the right-column panel
 */
export class MonitorEditPanel extends BaseComponent {
  constructor(parentSelector, monitor_unique_name) {
    super(parentSelector, "monitor-edit-column", "fragments/monitor-edit-panel.html");
    this.monitor_unique_name = monitor_unique_name;
  }

  _onElementReady() {
    // Add your custom logic here
    console.log("MonitorEditPanel element is ready");

    // Get monitor data from the backend
    requestSingleMonitor(this.monitor_unique_name).then((response) => {
      if (!response) {
        console.error("Failed to fetch monitor data");
        return;
      }

      console.log("Monitor data received:", response);
      this.#fillForm(response);
    });

    // Add event listeners for any form changes (input, change...) NOT for submit
    const form = document.querySelector(".settings-form");
    form.addEventListener("input", this.#onFormChange.bind(this));
    form.addEventListener("change", this.#onFormChange.bind(this));

    // form.addEventListener("submit", (event) => {
    //   console.log("Form submitted");
    //   event.preventDefault();
    //   const validator = new FormValidator(form);
    //   const errors = validator.validate();
    //   if (Object.keys(errors).length === 0) {
    //     console.log("Form is valid, submitting...");
    //   }
    // });
  }

  #onFormChange(event) {
    console.log("Form changed");
    const form = event.target.form;
    const validator = new FormValidator(form);
    const errors = validator.validate();
    console.log("Errors:", errors);

    // Update the form with the validation errors styles and messages
    for (const element of form.elements) {
      if (!errors[element.name]) {
        element.classList.remove("validation-error");
        element.title = "";
        this.#clearErrorMessagesForField(element);
      } else {
        element.classList.add("validation-error");
        element.title = errors[element.name];
        this.#addErrorMessageForField(element, errors[element.name]);
      }
    }
  }

  #addErrorMessageForField(formElement, message) {
    // Skip if the element already has an error message
    if (formElement.parentElement.querySelector(".validation-error-message")) {
      return;
    }

    const errorElement = document.createElement("div");
    errorElement.className = "validation-error-message";
    errorElement.innerText = message;
    // Add after itself to the same parent
    formElement.insertAdjacentElement("afterend", errorElement);
  }

  #clearErrorMessagesForField(formElement) {
    const errorMessages = formElement.parentElement.querySelectorAll(".validation-error-message");
    for (const message of errorMessages) {
      message.remove();
    }
  }

  #fillForm(monitorData) {
    // Populate the form with the monitor data
    const form = document.querySelector(".settings-form");
    form.name.value = monitorData.value.unique_name;
    form.url.value = monitorData.value.query.value.url;
    form.interval.value = monitorData.value.period_in_seconds;
    form.condition.value = monitorData.value.query.type; // TODO Implement a way to comminucate this with the backed? Predefined strings? Use an "adapter"?
    form.retries.value = monitorData.value.query.value._retries;
    form["retries-interval"].value = "Not yet implemented"; // TODO: Implement retries_interval
    form.threshold.value = "Not yet implemented"; // TODO: Implement thresholds (e.g. "tolerate 1", or "2 out of 5"...)
    form["threshold-value"].value = "Not yet implemented";
    form["alert-profile"].value = "Not yet implemented"; // TODO: Implement alert profiles defined by the user
  }
}

class FormValidator {
  constructor(form) {
    this.form = form;
  }

  validate() {
    const errors = {};

    // Validate each field
    if (!this._nonEmpty(this.form.name.value)) {
      errors.name = "Name cannot be empty.";
    } else if (!this._isValidFilename(this.form.name.value)) {
      errors.name = "Name is not a valid filename.";
    } else if (!this._isUniqueName(this.form.name.value)) {
      errors.name = "Name must be unique.";
    }

    if (!this._nonEmpty(this.form.url.value) || !this._isUrl(this.form.url.value)) {
      errors.url = "URL must be a valid URL (including protocol).";
    }

    if (!this._isPositiveIntegerString(this.form.interval.value)) {
      errors.interval = "Interval must be a positive integer.";
    }

    // if (!this._nonEmpty(this.form.condition.value)) {
    //   errors.condition = "Condition must be selected.";
    // }

    if (!this._isNonNegativeIntegerString(this.form.retries.value)) {
      errors.retries = "Retries must be a non-negative integer.";
    }

    // Placeholder checks for not-yet-implemented fields
    // if (!this._nonEmpty(this.form["retries-interval"].value)) {
    //   errors["retries-interval"] = "Retries interval is not implemented yet.";
    // }

    // if (!this._nonEmpty(this.form.threshold.value)) {
    //   errors.threshold = "Threshold is not implemented yet.";
    // }

    // if (!this._nonEmpty(this.form["threshold-value"].value)) {
    //   errors["threshold-value"] = "Threshold value is not implemented yet.";
    // }

    // if (!this._nonEmpty(this.form["alert-profile"].value)) {
    //   errors["alert-profile"] = "Alert profile is not implemented yet.";
    // }

    // Return errors object
    return errors;
  }

  _nonEmpty(value) {
    return value.trim() !== "";
  }

  _isUrl(value) {
    try {
      new URL(value);
      return true;
    } catch (_) {
      return false;
    }
  }

  _isNumber(value) {
    return !isNaN(value);
  }

  _isNonNegativeIntegerString(value) {
    return /^\d+$/.test(value);
  }

  _isPositiveIntegerString(value) {
    return /^[1-9]\d*$/.test(value);
  }

  _isUniqueName(value) {
    // TODO: pass this call to the backend to validate
    // WARNING - Currently always returns true
    return true;
  }

  _isValidFilename(filename) {
    const forbiddenCharacters = /[<>:"/\\|?*\x00-\x1F]/; // Forbidden characters and control chars
    const reservedNames = /^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$/i; // Windows reserved names
    const maxLength = 240; // Accounting for extensions and such

    if (typeof filename !== "string" || filename.length === 0 || filename.length > maxLength) {
      return false;
    }

    return !forbiddenCharacters.test(filename) && !reservedNames.test(filename);
  }
}
