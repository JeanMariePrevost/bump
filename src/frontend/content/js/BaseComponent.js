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
    this._managedListeners = []; // Array to store event listeners

    this._initElement(className);
    this._renderFragment(fragmentPath).then(() => {
      this._onElementReady();
    });
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

    // Add event listener for the element being remove
    this.addManagedEventListener(this.element, "remove", this.destroy.bind(this));

    // Set up a MutationObserver to detect if the element is removed from the DOM in other ways
    // Couldn't find a beter way to detect if the element is removed from the DOM via innerHTML or replaceChild and such
    const observer = new MutationObserver((mutationsList) => {
      for (const mutation of mutationsList) {
        if (mutation.type === "childList") {
          // Check if the tracked element is in the removedNodes list
          mutation.removedNodes.forEach((node) => {
            if (node === this.element) {
              observer.disconnect(); // Stop observing
              this.destroy(); // Clean up
            }
          });
        }
      }
    });

    // Start observing the parent for child changes
    observer.observe(document, { childList: true, subtree: true });
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
   * Function to add an event listener, but also keep a reference to it to be able to remove it during destruction
   * @param {EventTarget} target The event target, as in "thisIsTheTarget.addEventListener()""
   * @param {string} type The event type, as in "target.addEventListener('theType', listener)"
   * @param {function} listener The event listener, as in "target.addEventListener('theType', thisIsTheListener)"
   * @returns {void}
   */
  addManagedEventListener(target, type, listener) {
    if (!target) {
      console.error("Trying to add event listener to non-existing target.");
      return;
    }
    target.addEventListener(type, listener);
    this._managedListeners.push({ target, type, listener });
  }

  /**
   * Function to remove all managed event listeners
   * @returns {void}
   */
  removeManagedEventListeners() {
    this._managedListeners.forEach(({ target, type, listener }) => {
      target.removeEventListener(type, listener);
    });
    this._managedListeners = [];
  }

  /**
   * Hook for subclasses after the fragment has been loaded and added to the DOM.
   */
  _onElementReady() {}

  /**
   * Clean up the element safely, removing it from the DOM and removing any event listeners
   * Note: Override this method in subclasses if you need special cleanup behavior.
   */
  destroy() {
    console.log("Destroying element" + this.element);
    this.removeManagedEventListeners();
    if (this.element) {
      // Remove the listeners
      this.element.removeEventListener("remove", this.destroy);
      // Remove the element from the DOM if it's still there
      this.element.remove();
    }
  }
}
