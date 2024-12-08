import { BaseComponent } from "./BaseComponent.js";

/**
 * Handles the dashboard right-column panel
 * @param {string} parentSelector - The selector for the parent element to append the panel to
 */
export class NavbarComponent extends BaseComponent {
  constructor(parentSelector) {
    super(parentSelector, "navbar", "fragments/navbar.html");
  }
}
