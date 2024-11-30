import { BaseComponent } from "./BaseComponent.js";

/**
 * Handles the monitor details right-column panel
 */
export class MonitorDetailsColumn extends BaseComponent {
  constructor(parentSelector) {
    super(parentSelector, "monitor-details-column", "fragments/monitor-details-panel.html");
  }

  _onElementReady() {
    // Add your custom logic here
    console.log("MonitorDetailsColumn element is ready");

    // Add event listeners to the action-links
    //For reference: <span class="monitor-action-link" data-action="pause">❙❙ Pause</span>
    const actionLinks = this.element.querySelectorAll(".monitor-action-link");
    actionLinks.forEach((link) => {
      link.addEventListener("click", this._onActionLinkClick.bind(this));
    });
  }

  _onActionLinkClick(event) {
    const action = event.target.dataset.action;
    // Switch on "data-action" attribute to determine the action
    switch (action) {
      case "pause":
        console.log("Pause action clicked");
        // TODO: Implement pause action
        break;
      case "edit":
        console.log("Edit action clicked");
        // TODO: Implement edit action
        break;
      case "duplicate":
        console.log("Duplicate action clicked");
        // TODO: Implement duplicate action
        break;
      case "delete":
        console.log("Delete action clicked");
        // TODO: Implement delete action
        break;
      default:
        console.warn(`Unknown action: ${action}`);
    }
  }
}
