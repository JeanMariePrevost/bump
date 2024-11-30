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
      this._udpateStatsCards(monitorData);
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

  _udpateStatsCards(monitorData) {
    console.log("Updating stats cards");
    if (!monitorData) {
      console.warn("Monitor data is not available.");
      return;
    }
    console.log("Monitor data:", monitorData);

    // Prepare the data for the stats cards
    let monitorStatus = "unknown";
    if (monitorData.value?.last_query_passed === true) {
      monitorStatus = "up";
    } else if (monitorData.value?.last_query_passed === false) {
      monitorStatus = "down";
    }

    let timeAtLastStatusChange = monitorData.value?.time_at_last_status_change?.value ?? null;
    if (timeAtLastStatusChange) {
      // Convert to human-readable format
      const date = new Date(timeAtLastStatusChange);
      timeAtLastStatusChange = `${date.toLocaleDateString()}<br>${date.toLocaleTimeString()}`;
    }

    const uptimePercentage = monitorData.value?.stats_avg_uptime * 100 ?? 0;
    const avgLatency = monitorData.value?.stats_avg_latency * 1000 ?? null; // Convert to ms

    // Update the stats cards
    const statusCard = this.element.querySelector(".monitor-details-status");
    const durationCard = this.element.querySelector(".monitor-details-duration");
    const uptimeCard = this.element.querySelector(".monitor-details-uptime");
    const latencyCard = this.element.querySelector(".monitor-details-latency");

    // Update the status card
    statusCard.setAttribute("data-status", monitorStatus);
    const statusValue = statusCard.querySelector(".stat-card-value-text");
    statusValue.textContent = monitorStatus.toUpperCase();

    // Update the duration card
    durationCard.setAttribute("data-status", monitorStatus);
    const durationValue = durationCard.querySelector(".stat-card-value-text");
    durationValue.innerHTML = timeAtLastStatusChange; // Use innerHTML to render the <br> tag

    // Update the uptime card
    //TODO : Color-code?
    const uptimeValue = uptimeCard.querySelector(".stat-card-value-text");
    uptimeValue.textContent = `${uptimePercentage.toFixed(2)}%`;

    // Update the latency card
    //TODO : Color-code?
    const latencyValue = latencyCard.querySelector(".stat-card-value-text");
    latencyValue.textContent = `${avgLatency.toFixed(2)}ms`;

    // For reference:
    //   <div class="monitor-details-stats-container">
    //   <div class="card monitor-details-status">
    //     <div class="card-content">
    //       <div class="stat-card-value-text">UP</div>
    //       <div class="stat-card-label">Status</div>
    //     </div>
    //   </div>
    //   <div class="card monitor-details-duration">
    //     <div class="card-content">
    //       <div class="stat-card-value-text">0s</div>
    //       <div class="stat-card-label">Since</div>
    //     </div>
    //   </div>
    //   <div class="card monitor-details-status">
    //     <div class="card-content">
    //       <div class="stat-card-value-text">0%</div>
    //       <div class="stat-card-label">7-days uptime</div>
    //     </div>
    //   </div>
    //   <div class="card monitor-details-status">
    //     <div class="card-content">
    //       <div class="stat-card-value-text">0ms</div>
    //       <div class="stat-card-label">Avg latency</div>
    //     </div>
    //   </div>
    // </div>
  }
}
