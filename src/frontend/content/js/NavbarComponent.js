import { BaseComponent } from "./BaseComponent.js";

/**
 * Handles the dashboard right-column panel
 * @param {string} parentSelector - The selector for the parent element to append the panel to
 */
export class NavbarComponent extends BaseComponent {
  constructor(parentSelector) {
    super(parentSelector, "navbar", "fragments/navbar.html");
  }

  _onElementReady() {
    // Listen for and catch the click event on the navbar "id=documentation-link" link to open as an external link
    this.addManagedEventListener(document.getElementById("documentation-link"), "click", (event) => {
      event.preventDefault();
      window.open("https://jeanmarieprevost.github.io/bump/", "_blank");
    });
  }
}
