/**
 * FormHelper class serves to determine whether the contents of a form have changed, and to facilitate validation.
 * Expects the following structure:
 *   - a ".card" element containing a form
 *   - fields with a "name" attribute
 *   - an apply and revert button with ids "apply-edits" and "revert-edits".
 *
 * Example:
 * <div class="card monitor-edit-card">
 *   <div class="card-title">
 *     <div class="flex-row-baseline">
 *       <div class="monitor-action-link invisible no-events" id="revert-edits" data-action="revert-edits">↶ Revert</div>
 *       <div class="monitor-action-link invisible no-events" id="apply-edits" data-action="apply-edits">✔ Apply</div>
 *     </div>
 *   </div>
 *   <div class="card-content">
 *     <form class="settings-form">
 *       ...
 */
export class FormCardHelper {
  #formSnapshot; // Holds a snapshot of the form data to compare against later or to revert to
  #validationRules = new Set(); // Holds the validation rules for each field as (fieldName, predicate) pairs

  /**
   * @param {HTMLElement} cardElementContainingTheForm - The card element containing the form
   * @param {string} errorMessageParentSelector - The selector of the closest element to add to error messages, defaults to direct parent of the field if not provided
   */
  constructor(cardElementContainingTheForm, errorMessageParentSelector = undefined) {
    this.element = cardElementContainingTheForm;
    this.formElement = cardElementContainingTheForm.querySelector("form");
    this.errorMessageParentSelector = errorMessageParentSelector;
    this.#formSnapshot = null;
    this.revertButton = document.getElementById("revert-edits");
    this.applyButton = document.getElementById("apply-edits");

    // Error checks
    if (!this.formElement) {
      console.error("Form not found in the card element.");
      return;
    }
    if (!this.revertButton) {
      console.error("Revert button not found.");
    }
    if (!this.applyButton) {
      console.error("Apply button not found.");
    }

    // Add event listeners
    this.formElement.addEventListener("change", this.#onFormChange.bind(this));
    this.formElement.addEventListener("input", this.#onFormChange.bind(this));
    this.revertButton = document.getElementById("revert-edits");
    if (this.revertButton) {
      this.revertButton.addEventListener("click", this.revertForm.bind(this));
    }
  }

  /**
   * Takes a "snapshot" of the form data to compare against later to detect changes.
   * Fields are identified as those with a name attribute.
   */
  saveFormSnapshot() {
    const form = document.querySelector(".settings-form");
    this.#formSnapshot = {};
    for (const element of form.elements) {
      if (element.name) {
        this.#formSnapshot[element.name] = element.value;
      }
    }
    console.log("DEBUG - Form snapshot saved:", this.#formSnapshot);
  }

  /** True if the form contains changes compared to the last snapshot */
  formContainsChanges() {
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

  /** Reverts the form to the state it was in when #saveFormSnapshot was called. */
  revertForm() {
    if (!this.#formSnapshot) return;

    const form = document.querySelector(".settings-form");
    for (const element of form.elements) {
      if (element.name && this.#formSnapshot[element.name] !== undefined) {
        element.value = this.#formSnapshot[element.name];
      }
    }
  }

  #onFormChange(event) {
    console.log("DEBUG - Form changed");

    // DEBUG - run and display the various functions
    console.log("DEBUG - Form contains changes:", this.formContainsChanges());
    console.log("DEBUG - Form is valid:", this.isFormInputValid());
    console.log("DEBUG - Validation errors:", this.getValidationErrors());
    this.applyValidationStylesAndMessages();
  }

  /**
   * Validates the form based on the validation rules set by addValidationRule().
   * @returns {boolean} - True if all fields pass validation, false if any fail or error.
   */
  isFormInputValid() {
    this.warnIfValidatingWithNoRules();

    // Go through each element of this.#validationRules and check if the field passes the predicate
    for (const { fieldName, predicate } of this.#validationRules) {
      const field = this.formElement.querySelector(`[name="${fieldName}"]`);
      if (!field) {
        console.error(`Field "${fieldName}" not found in the form.`);
        continue;
      }

      const value = field.value;
      const result = predicate(value);
      if (result !== true) {
        return false;
      }
    }
    return true;
  }

  /**
   * Returns a list of validation errors for the form based on the validation rules set by addValidationRule
   * @returns {Array} - List of (fieldName, errorString) pairs for each failed validation
   */
  getValidationErrors() {
    const errors = []; // List of fieldName, errorString pairs

    this.warnIfValidatingWithNoRules();

    for (const { fieldName, predicate } of this.#validationRules) {
      const field = this.formElement.querySelector(`[name="${fieldName}"]`);
      if (!field) {
        console.error(`Field "${fieldName}" not found in the form.`);
        errors.push([fieldName, "Field not found."]);
        continue;
      }

      const value = field.value;
      const result = predicate(value);
      if (result !== true) {
        errors.push([fieldName, result]);
      }
    }
    return errors;
  }

  /**
   * Applies formating to the form fields to indicate validation errors to the user.
   * Also inserts/removes elements after the field with the error message.
   * @param {string} invalidClassName - The class name to add to fields that fail validation
   * @param {string} invalidMessageClassName - The class name to add to the error message element
   */
  applyValidationStylesAndMessages(invalidClassName = "validation-error", invalidMessageClassName = "validation-error-message") {
    const errors = this.getValidationErrors();
    // Clear current error styles
    const fields = this.formElement.querySelectorAll(`.${invalidClassName}`);
    for (const field of fields) {
      field.classList.remove(invalidClassName);
    }

    // Clear current error messages
    const errorMessages = this.element.querySelectorAll(`.${invalidMessageClassName}`);
    for (const message of errorMessages) {
      message.remove();
    }

    // Add new error styles and messages
    for (const [fieldName, error] of errors) {
      const field = this.formElement.querySelector(`[name="${fieldName}"]`);
      if (!field) {
        console.error(`Field "${fieldName}" not found in the form.`);
        continue;
      }

      field.classList.add(invalidClassName);
      this.#addErrorMessageForField(field, error, invalidMessageClassName);
    }

    const cardTitle = this.element.querySelector(".card-title");
    if (this.formContainsChanges()) {
      if (this.isFormInputValid()) {
        cardTitle.setAttribute("data-changes", "valid");
        this.applyButton.classList.remove("invisible");
        this.revertButton.classList.remove("invisible");
      } else {
        cardTitle.setAttribute("data-changes", "invalid");
        this.applyButton.classList.add("invisible");
        this.revertButton.classList.remove("invisible");
      }
    } else {
      cardTitle.setAttribute("data-changes", "no-changes");
      this.applyButton.classList.add("invisible");
      this.revertButton.classList.add("invisible");
    }
  }

  #addErrorMessageForField(fieldElement, message, invalidMessageClassName) {
    const targetElement = this.errorMessageParentSelector ? fieldElement.closest(this.errorMessageParentSelector) : fieldElement.parentElement;

    // Skip if the element already has an error message
    if (targetElement.querySelector(`.${invalidMessageClassName}`)) {
      return;
    }

    const errorElement = document.createElement("div");
    errorElement.className = invalidMessageClassName;
    errorElement.innerText = message;
    // Add to the target element
    targetElement.insertAdjacentElement("afterend", errorElement);
  }

  warnIfValidatingWithNoRules() {
    if (this.#validationRules.size === 0) {
      console.warn("Form has no rules and will always pass validation.");
    }
  }

  /**
   * Add a validation condition for a field when using the validate() method.
   * Can be used multiple times for the same field to add multiple conditions.
   * E.g. addValidationRule("email", "isEmail")
   * @param {string} fieldName - The name of the field to validate
   * @param {string} ruleName - The name of the rule to apply
   * @returns {void}
   */
  addValidationRule(fieldName, ruleName) {
    const predicate = this.predicates[ruleName];
    if (predicate === undefined) {
      console.error(`No rule named "${ruleName}".`);
      return;
    }

    this.#validationRules.add({ fieldName, predicate });
  }

  /**
   * Add a validation rule that uses a custom predicate function.
   * E.g. addCustomValidationRule("email", (value) => value.includes("@"))
   * @param {string} fieldName - The name of the field to validate
   * @param {function} predicate - The predicate function to apply
   */
  addCustomValidationRule(fieldName, predicate) {
    this.#validationRules.add({ fieldName, predicate });
  }

  ///////////////////////////////////////
  // Validation methods for validating STRING inputs
  // NOTE: Each returns the boolean true if valid, but an error message string if invalid
  ///////////////////////////////////////
  predicates = {
    isNotEmpty: function (valueString) {
      return valueString.trim() !== "" ? true : "Must be non-empty.";
    },

    isEmail: function (valueString) {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valueString) ? true : "Must be a valid address.";
    },

    isUrl: function (valueString) {
      try {
        new URL(valueString);
        return true;
      } catch (_) {
        return "Must be a valid URL.";
      }
    },

    isBoolean: function (valueString) {
      return /^([Tt]rue|[Ff]alse|1|0)$/.test(valueString) ? true : "Must be true or false.";
    },

    isNonNegativeNumber: function (valueString) {
      return !isNaN(valueString) && parseFloat(valueString) >= 0 ? true : "Must be a non-negative number.";
    },

    isNonNegativeInteger: function (valueString) {
      return /^\d+$/.test(valueString) ? true : "Must be a non-negative integer.";
    },

    isPositiveInteger: function (valueString) {
      return /^[1-9]\d*$/.test(valueString) ? true : "Must be a positive integer.";
    },

    isValidFilename: function (valueString) {
      if (typeof value !== "string" || value.trim().length === 0) {
        return "Must be a non-empty string.";
      }
      if (filename.length > 255) {
        return "Filename is too long.";
      }

      const invalidChars = /[<>:"/\\|?*\x00-\x1F]/g;
      if (invalidChars.test(filename)) {
        return false;
      }

      const reservedNames = /^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\..*)?$/i;
      if (reservedNames.test(filename)) {
        return "Filename is OS-reserved.";
      }

      // Check for only dots or spaces
      if (/^[. ]+$/.test(filename)) {
        return "Filename cannot be only dots or spaces.";
      }

      return true;
    },
  };
}
