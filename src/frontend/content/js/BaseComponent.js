import { loadFragment } from "./utils.js";

/**
 * Base class that loads a fragment, builds its element, and adds it to the DOM.
 * @param {string} parentSelector The selector for the target parent element in the DOM.
 * @param {string} className The class name for the element for styling.
 * @param {string} fragmentPath The path to the fragment to load.
 */
export class BaseComponent {
  constructor(parentSelector, className, fragmentPath) {
    this.parentSelector = parentSelector;
    this.element = null; // "this" element in the DOM

    this._initElement(className);
    this._renderFragment(fragmentPath);
  }

  // Initializes and attaches its element to the DOM
  _initElement(className) {
    const parent = document.querySelector(this.parentSelector);
    if (!parent) {
      console.error(`Parent element "${this.parentSelector}" not found.`);
      return;
    }

    this.element = document.createElement("div");
    this.element.className = className;
    parent.appendChild(this.element);
  }

  // Builds the content of the element based on its fragment
  async _renderFragment(fragmentPath) {
    // Fetch the template
    const monitorDeailsDiv = await loadFragment(fragmentPath);
    if (!monitorDeailsDiv) {
      console.error("Failed to load template.");
      return;
    }

    // Add the loaded content to the element
    this.element.appendChild(monitorDeailsDiv);
  }

  /**
   * Clean up the element safely, removing it from the DOM and removing any event listeners
   * Note: Override this method in subclasses if you need special cleanup behavior.
   */
  destroy() {
    if (this.element) {
      this.element.remove();
    }
  }
}
