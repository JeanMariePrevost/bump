import { loadFragment } from "./utils.js";

export class DashboardColumn {
  constructor(parentSelector) {
    this.parentSelector = parentSelector;
    this.element = null; // Reference to the root element
    this.state = {}; // Internal state for the column

    this.#init();
  }

  // Initializes and attaches the element to the DOM
  #init() {
    const parent = document.querySelector(this.parentSelector);
    if (!parent) {
      console.error(`Parent element "${this.parentSelector}" not found.`);
      return;
    }

    this.element = document.createElement("div");
    this.element.classList.add("dashboard-column");
    parent.appendChild(this.element);

    this.render();
  }

  // Builds the content of the element based on its state
  async render() {
    // Fetch the template
    const monitorDeailsDiv = await loadFragment("fragments/dashboard.html");
    if (!monitorDeailsDiv) {
      console.error("Failed to load template.");
      return;
    }
    console.log("Template loaded:", monitorDeailsDiv);

    // Example: Render based on state
    this.element.appendChild(monitorDeailsDiv);
  }
}
