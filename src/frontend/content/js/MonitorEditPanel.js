import { BaseComponent } from "./BaseComponent.js";
import { requestSingleMonitor, submitMonitorConfig } from "./PythonJsBridge.js";
import { backendQueryClassToQueryTypeName, queryTypeNameToBackendClass } from "./utils.js";

/**
 * Handles the monitor editing form in the right-column panel
 */
export class MonitorEditPanel extends BaseComponent {
  #formSnapshot; // A snapshot of the form data to compare against to detect changes
  constructor(parentSelector, monitor_unique_name, focusNameField = false) {
    super(parentSelector, "monitor-edit-column", "fragments/monitor-edit-panel.html");
    this.monitor_unique_name = monitor_unique_name;
    this.#formSnapshot = null;
    this.focusNameField = focusNameField;
  }

  /**
   * Takes a "snapshot" of the form data to compare against later to detect changes.
   */
  #saveFormSnapshot() {
    const form = document.querySelector(".settings-form");
    this.#formSnapshot = {};
    for (const element of form.elements) {
      if (element.name) {
        this.#formSnapshot[element.name] = element.value;
      }
    }
  }

  #formContainsChanges() {
    if (!this.#formSnapshot) return false;

    const form = document.querySelector(".settings-form");
    for (const element of form.elements) {
      if (element.name && this.#formSnapshot[element.name] !== undefined) {
        if (element.value !== this.#formSnapshot[element.name]) {
          return true;
        }
      }
    }
    return false;
  }

  _onElementReady() {
    // Add your custom logic here
    console.log("MonitorEditPanel element is ready");

    // Get monitor data from the backend
    this.#resetFormAndFillWithMonitorData();

    // Add event listeners for any form changes (input, change...) NOT for submit
    const form = document.querySelector(".settings-form");
    form.addEventListener("input", this.#onFormChange.bind(this));
    form.addEventListener("change", this.#onFormChange.bind(this));

    // Add event listeners to the action-links
    const actionLinks = this.element.querySelectorAll(".monitor-action-link");
    actionLinks.forEach((link) => {
      link.addEventListener("click", this._onActionLinkClick.bind(this));
    });

    // Fire a global event to inform things like the list that a monitor should be selected
    const event = new CustomEvent("monitor-edit-panel-ready", { detail: { monitor_unique_name: this.monitor_unique_name } });
    document.dispatchEvent(event);
    console.log(`Monitor edit panel fired event for ${this.monitor_unique_name}`);
  }

  _onActionLinkClick(event) {
    const action = event.target.dataset.action;
    // Switch on "data-action" attribute to determine the action
    switch (action) {
      case "apply-edits":
        console.log("Apply edits action clicked");
        // Collect the form data
        const form = document.querySelector(".settings-form");

        const newMonitorConfig = {
          original_name: this.monitor_unique_name,
          unique_name: form.name.value,
          query_url: form.url.value,
          query_type: queryTypeNameToBackendClass(form["query-type"].value),
          query_params_string: form["condition-value"].value,
          period_in_seconds: form.interval.value,
          retries: form.retries.value,
          retries_interval_in_seconds: form["retries-interval"].value,
        };
        submitMonitorConfig(newMonitorConfig)
          .then((response) => {
            if (response === "true") {
              console.log("Backend accepted monitor config");
              // Refresh everything by navigating to home, but give it a parameter to know to jump directly to this window
              window.location.href = "/?monitor_edit=" + encodeURIComponent(newMonitorConfig.unique_name);
            } else {
              console.error("Backend rejected monitor config : ", response);
              alert("Changes could not be applied.\n\nError Message:\n" + response);
            }
          })
          .catch((error) => {
            console.error("Failed to submit monitor config:", error);
            alert("Changes could not be applied.\n\nError Message:\n" + error);
          });
        break;
      case "revert-edits":
        console.log("Revert edits action clicked");
        // Reload the form with the original monitor data, smoother transition
        this.#resetFormAndFillWithMonitorData();
        break;
      default:
        console.warn(`Unknown action: ${action}`);
        alert("Received unknown action: " + action);
    }
  }

  #onFormChange(event) {
    console.log("Form changed");
    const form = event.target.form;
    this.#applyFormValidation(form);

    if (event.target.name === "query-type") {
      // If it's the query-type being changed, update the condition-value element's placeholder and tooltip to show the expected structure
      this.#updateConditionValueFieldFromQueryType(form, event.target.value);
    }
  }

  /**
   * Update the condition-value field based on the query type, e.g. disabling it, setting its tooltip, etc.
   * @param {HTMLFormElement} form The form element containing the condition-value field
   * @param {string} queryType The query type selected by the user
   */
  #updateConditionValueFieldFromQueryType(form, queryType) {
    const conditionValueField = form["condition-value"];

    // Apply the item's tooltip to the dropdown itself
    form["query-type"].title = form["query-type"].selectedOptions[0].title;

    // Reset the condition-value field
    conditionValueField.disabled = false;
    conditionValueField.value = "";

    // Update the condition-value field based on the query type
    switch (queryType) {
      case "http_simple":
        // Special case, empty the condition-value field and disable it
        conditionValueField.disabled = true;
        conditionValueField.placeholder = "No condition needed";
        conditionValueField.title = "Requires no additional parameters";
        break;
      case "http_content":
        conditionValueField.placeholder = 'e.g. "Welcome to"';
        conditionValueField.title = "The text to look for in the response";
        break;
      case "http_headers":
        conditionValueField.placeholder = 'e.g. "Content-Type: text/html"';
        conditionValueField.title = "The key-value pair to look for in the response headers";
        break;
      case "http_status_code":
        conditionValueField.placeholder = 'e.g. "200"';
        conditionValueField.title = "The HTTP status code to look for in the response";
        break;
      case "http_regex":
        conditionValueField.placeholder = 'e.g. "[Ww]elcome to.*"';
        conditionValueField.title = "The regex pattern to look for in the response";
        break;
      case "rendered_content_regex":
        conditionValueField.placeholder = 'e.g. "[Ww]elcome to.*"';
        conditionValueField.title = "The regex pattern to look for in the rendered page content";
        break;
      default:
        console.warn(`Unknown query type: ${queryType}`);
        conditionValueField.placeholder = "ERROR: Unknown query type";
        conditionValueField.title = "Could not resolve query type " + queryType;
        break;
    }
  }

  #applyFormValidation(form) {
    const validator = new FormValidator(form);
    const errors = validator.validate();
    if (Object.keys(errors).length === 0) {
      console.log("Form is valid");
    } else {
      console.log("Form is invalid:", errors);
    }

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

    // Set the data-changes="valid/invalid" attribute on .monitor-edit-card .card-title for added feedback
    const cardTitle = document.querySelector(".monitor-edit-card .card-title");
    const applyButton = document.querySelector('.monitor-action-link[data-action="apply-edits"]');
    const revertButton = document.querySelector('.monitor-action-link[data-action="revert-edits"]');
    revertButton.classList.remove("invisible");
    revertButton.classList.remove("no-events");

    if (!this.#formContainsChanges()) {
      // Nothing changes
      this.#hideApplyButton();
      this.#hideRevertButton();
      cardTitle.setAttribute("data-changes", "no-changes");
    } else {
      if (Object.keys(errors).length === 0) {
        // Valid changes
        cardTitle.setAttribute("data-changes", "valid");
        this.#showRevertButton();
        this.#showApplyButton();
      } else {
        // Invalid changes
        cardTitle.setAttribute("data-changes", "invalid");
        this.#showRevertButton();
        this.#hideApplyButton();
      }
    }
  }

  #showRevertButton() {
    const revertButton = document.querySelector('.monitor-action-link[data-action="revert-edits"]');
    revertButton.classList.remove("invisible");
    revertButton.classList.remove("no-events");
  }

  #hideRevertButton() {
    const revertButton = document.querySelector('.monitor-action-link[data-action="revert-edits"]');
    revertButton.classList.add("invisible");
    revertButton.classList.add("no-events");
  }
  #showApplyButton() {
    const applyButton = document.querySelector('.monitor-action-link[data-action="apply-edits"]');
    applyButton.classList.remove("invisible");
    applyButton.classList.remove("no-events");
  }

  #hideApplyButton() {
    const applyButton = document.querySelector('.monitor-action-link[data-action="apply-edits"]');
    applyButton.classList.add("invisible");
    applyButton.classList.add("no-events");
  }

  #resetFormValidation(form) {
    for (const element of form.elements) {
      element.classList.remove("validation-error");
      element.title = "";
      this.#clearErrorMessagesForField(element);
    }

    // Remove the data-changes attribute from the card title
    const cardTitle = document.querySelector(".monitor-edit-card .card-title");
    cardTitle.removeAttribute("data-changes");

    // Disable the "Apply edits" and "Revert edits" buttons
    const applyButton = document.querySelector('.monitor-action-link[data-action="apply-edits"]');
    const revertButton = document.querySelector('.monitor-action-link[data-action="revert-edits"]');
    applyButton.classList.add("invisible");
    applyButton.classList.add("no-events");
    revertButton.classList.add("invisible");
    revertButton.classList.add("no-events");
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

  #resetFormAndFillWithMonitorData() {
    // Disable the "Apply edits" and "Revert edits" buttons
    const applyButton = document.querySelector('.monitor-action-link[data-action="apply-edits"]');
    const revertButton = document.querySelector('.monitor-action-link[data-action="revert-edits"]');
    applyButton.classList.add("invisible");
    applyButton.classList.add("no-events");
    revertButton.classList.add("invisible");
    revertButton.classList.add("no-events");

    // Remove any "data-changes" attribute from the card title
    const cardTitle = document.querySelector(".monitor-edit-card .card-title");
    cardTitle.removeAttribute("data-changes");

    // Fill the form with the monitor data
    requestSingleMonitor(this.monitor_unique_name)
      .then((monitorData) => {
        if (!monitorData) {
          console.error("Backend returned no data for monitor:", this.monitor_unique_name);
          return;
        }

        // Populate the form with the monitor data
        const form = document.querySelector(".settings-form");
        form.name.value = monitorData?.value?.unique_name ?? "ERROR";
        form.url.value = monitorData?.value?.query?.value?.url ?? "";
        form.interval.value = monitorData?.value?.period_in_seconds ?? "";
        form["query-type"].value = backendQueryClassToQueryTypeName(monitorData?.value?.query?.type);
        this.#updateConditionValueFieldFromQueryType(form, form["query-type"].value); // Update the condition-value field status based on the query type before setting its value
        form["condition-value"].value = monitorData?.value?.query?.value?.query_params_as_string ?? "";
        form.retries.value = monitorData.value.retries;
        form["retries-interval"].value = monitorData.value.retries_interval_in_seconds;
        form.threshold.value = "Not yet implemented"; // TODO: Implement thresholds (e.g. "tolerate 1", or "2 out of 5"...)
        form["threshold-value"].value = "Not yet implemented";
        form["alert-profile"].value = "Not yet implemented"; // TODO: Implement alert profiles defined by the user

        this.#saveFormSnapshot();

        this.#resetFormValidation(form);

        this.#applyFormValidation(form);
        if (this.focusNameField) this.#focusAndSelectNameField();
      })
      .catch((error) => {
        console.error("Failed to fetch monitor data for monitor:", this.monitor_unique_name, ", Error:", error);
      });
  }

  #focusAndSelectNameField() {
    const nameField = document.querySelector(".settings-form input[name='name']");
    console.log("Focusing and selecting name field");
    nameField.focus();
    nameField.select();
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

    switch (this.form["query-type"].value) {
      case "http_simple":
        // No additional validation needed
        break;
      case "http_content":
      case "http_status_code":
      case "http_regex":
      case "rendered_content_regex":
        //"non-empty" is enough for these
        if (!this._nonEmpty(this.form["condition-value"].value)) {
          errors["condition-value"] = "Cannot be empty.";
        }
        break;
      case "http_headers":
        // Has to be non-empty AND match the pattern "key: value" through .+:.+ to avoid confusion
        if (!this._nonEmpty(this.form["condition-value"].value)) {
          errors["condition-value"] = "Cannot be empty.";
        }
        if (!/.+:.+/.test(this.form["condition-value"].value)) {
          errors["condition-value"] = "Must be in the format 'key: value'.";
        }
        break;
    }

    if (!this._isNonNegativeIntegerString(this.form.retries.value)) {
      errors.retries = "Retries must be a non-negative integer.";
    }

    if (!this._isNonNegativeIntegerString(this.form["retries-interval"].value)) {
      errors["retries-interval"] = "Retries interval must be a non-negative integer.";
    }

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
    // TODO: pass this call to the backend to validate // It IS validated on the backend though, maybe validate against the list for the GUI would be enough?
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
