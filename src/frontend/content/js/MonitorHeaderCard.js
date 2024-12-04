/**
 *  MonitorHeaderCard.js
 * A component that displays the name of the monitor and lists its basic actions
 */

import { BaseComponent } from "./BaseComponent.js";
import { MonitorEditPanel } from "./MonitorEditPanel.js";
import { requestMonitorDeletion, requestNewDuplicateMonitor, requestMonitorExecution } from "./PythonJsBridge.js";
import { addMonitorToList } from "./MainPage.js";

export class MonitorHeaderCard extends BaseComponent {
  constructor(parentSelector, monitorData) {
    super(parentSelector, "monitor-header-card", "fragments/monitor-header-card.html");
    this.monitorUniqueName = monitorData.value.unique_name;
    this.monitorData = monitorData;
  }

  _onElementReady() {
    this._updateHeaderCard(this.monitorData);

    // Add event listeners to the action-links
    const actionLinks = this.element.querySelectorAll(".monitor-action-link");
    actionLinks.forEach((link) => {
      link.addEventListener("click", (event) => {
        this.handleMonitorActionBarLinksClick(event, this.monitor_unique_name);
      });
    });
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

  handleMonitorActionBarLinksClick(event) {
    const action = event.target.dataset.action;
    // Switch on "data-action" attribute to determine the action
    switch (action) {
      case "execute":
        console.log("Execute action clicked");
        // Ask backend to execute the monitor
        requestMonitorExecution(this.monitorUniqueName);
        break;
      case "pause":
        console.log("Pause action clicked");
        // TODO: Implement pause action
        break;
      case "edit":
        console.log("Edit action clicked");
        // Empty whaterver is in the right column
        document.querySelector(".right-column").innerHTML = "";
        // Open the edit panel for the monitor
        new MonitorEditPanel(".right-column", this.monitorUniqueName);
        break;
      case "duplicate":
        console.log("Duplicate action clicked");
        // Ask backend to create a new monitor and receive the new monitor's data
        requestNewDuplicateMonitor(this.monitorUniqueName)
          .then((response) => {
            if (!response) {
              console.error("Failed to fetch new monitor data");
              return;
            }
            // Add the new monitor to the list
            addMonitorToList(response.value);
            // Empty whaterver is in the right column
            document.querySelector(".right-column").innerHTML = "";
            // Open the edit panel for the new monitor
            new MonitorEditPanel(".right-column", response.value.unique_name, true); // true will make it focus on the name input directly since the user will want to rename it
          })
          .catch((error) => {
            console.error("Error while duplicating monitor:", error);
          });
        break;
      case "delete":
        console.log("Delete action clicked");
        // Prompt user for confirmation
        if (confirm("Are you sure you want to delete this monitor?")) {
          // Ask backend to delete the monitor
          console.log("Deleting monitor");
          requestMonitorDeletion(this.monitorUniqueName)
            .then((response) => {
              if (response === "true") {
                console.log("Monitor deleted successfully");
                // Refresh back to the home page "/"
                window.location.href = "/";
              } else {
                console.error("Error while deleting monitor:", response);
              }
            })
            .catch((error) => {
              console.error("Error while deleting monitor:", error);
            });
        }
        // TODO: Implement delete action
        break;
      default:
        console.warn(`Unknown action: ${action}`);
    }
  }
}
