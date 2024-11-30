import { BaseComponent } from "./BaseComponent.js";
import { requestSingleMonitor } from "./PythonJsBridge.js";

/**
 * Handles the monitor details right-column panel
 */
export class MonitorDetailsPanel extends BaseComponent {
  constructor(parentSelector, monitor_unique_name) {
    super(parentSelector, "monitor-details-column", "fragments/monitor-details-panel.html");
    this.monitor_unique_name = monitor_unique_name;
  }

  _onElementReady() {
    // Add your custom logic here
    console.log("MonitorDetailsColumn element is ready");

    // Get the monitor data
    requestSingleMonitor(this.monitor_unique_name).then((monitorData) => {
      this._updateHeaderCard(monitorData);
    });

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

  _updateHeaderCard(monitorData) {
    const monitorNameElement = this.element.querySelector(".monitor-details-title");
    // Return if not found
    if (!monitorNameElement) {
      console.warn("Monitor name element not found.");
      return;
    }

    if (!monitorData) {
      console.warn("Monitor data is not available.");
      return;
    }

    const monitorIsUp = monitorData.value?.last_query_passed ?? null;

    let dataStatus = "unknown";
    if (monitorIsUp === null) {
      // Leave it t its default color
      console.warn("Monitor status is unknown.");
    } else if (monitorIsUp) {
      this.element.setAttribute("data-status", "up");
      dataStatus = "up";
    } else {
      this.element.setAttribute("data-status", "down");
      dataStatus = "down";
    }
    const headerCardDiv = this.element.querySelector(".monitor-details-header-card");
    headerCardDiv?.setAttribute("data-status", dataStatus);

    // Set the monitor name
    monitorNameElement.textContent = monitorData.value.unique_name;
  }
}
