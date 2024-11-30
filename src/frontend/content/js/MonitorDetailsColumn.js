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
    const template = await loadTemplate("monitor-details-template.html");
    if (!template) {
      console.error("Failed to load template.");
      return;
    }
    console.log("Template loaded:", template);

    // Example: Render based on state
    this.element.innerHTML = `
        <h2>Monitor Details</h2>
        <p>Status: ${this.state.status || "Unknown"}</p>
        <p>Last Updated: ${this.state.lastUpdated || "Never"}</p>
      `;

    // Example: Add dynamic buttons or interactive elements
    const refreshButton = document.createElement("button");
    refreshButton.textContent = "Refresh";
    refreshButton.addEventListener("click", () => {
      this.setState({ lastUpdated: new Date().toLocaleString() });
    });
    this.element.appendChild(refreshButton);
  }
}
