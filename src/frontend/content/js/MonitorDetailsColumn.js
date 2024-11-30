import { loadTemplate } from "./utils.js";

export class MonitorDetailsColumn {
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
    this.element.classList.add("monitor-details-column");
    parent.appendChild(this.element);

    this.render();
  }

  // Builds the content of the element based on its state
  async render() {
    if (!this.element) {
      console.error("Element not initialized. Did you forget to call init()?");
      return;
    }

    // Fetch the template
    const monitorDeailsDiv = await loadTemplate("monitor-details-template.html");
    if (!monitorDeailsDiv) {
      console.error("Failed to load template.");
      return;
    }
    console.log("Template loaded:", monitorDeailsDiv);

    // Example: Render based on state
    this.element.appendChild(monitorDeailsDiv);
  }
}
