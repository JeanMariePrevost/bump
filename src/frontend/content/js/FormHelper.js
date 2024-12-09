/**
 * FormHelper class serves to determine whether the contents of a form have changed,
 * and to facilitate validation.
 */
export class FormHelper {
  #formSnapshot; // Holds a snapshot of the form data to compare against later or to revert to

  constructor(formElement) {
    this.formElement = formElement;
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

  /**
   * Reverts the form to the state it was in when #saveFormSnapshot was called.
   */
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
    this.validate();
  }

  validate() {
    //TODO: run through the conditions set for each field and return the list of errors
  }
}
