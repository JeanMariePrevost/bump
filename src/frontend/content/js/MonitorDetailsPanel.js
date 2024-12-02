import { BaseComponent } from "./BaseComponent.js";
import { requestSingleMonitor, requestMonitorHistory } from "./PythonJsBridge.js";
import { MonitorEditPanel } from "./MonitorEditPanel.js";

/**
 * Handles the monitor details right-column panel
 */
export class MonitorDetailsPanel extends BaseComponent {
  static MAX_RESULTS_IN_TIMELINE = 100; // TODO: Implement using DAYS instead of number of results? E.g. 7 days

  constructor(parentSelector, monitor_unique_name) {
    super(parentSelector, "monitor-details-column", "fragments/monitor-details-panel.html");
    this.monitor_unique_name = monitor_unique_name;
  }

  _onElementReady() {
    // Add your custom logic here
    console.log("MonitorDetailsColumn element is ready");

    // Get the monitor data
    requestSingleMonitor(this.monitor_unique_name)
      .then((monitorData) => {
        this._updateHeaderCard(monitorData);
        this._udpateStatsCards(monitorData);
      })
      .catch((error) => {
        console.error(`Error while fetching monitor data for ${this.monitor_unique_name}:`, error);
      });

    requestMonitorHistory(this.monitor_unique_name, MonitorDetailsPanel.MAX_RESULTS_IN_TIMELINE)
      .then((monitorResultsHistory) => {
        console.log("History data received:", monitorResultsHistory);
        this._updateTimelineChart(monitorResultsHistory);
        this._updateMonitorRecentEvents(monitorResultsHistory);
      })
      .catch((error) => {
        console.error(`Error while fetching history data for ${this.monitor_unique_name}:`, error);
      });

    // Add event listeners to the action-links
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
        // Remove self and instantiate a MonitorEditPanel
        this.destroy();
        new MonitorEditPanel(".right-column", this.monitor_unique_name);
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
    //TODO : Color-code against static values?
    const uptimeValue = uptimeCard.querySelector(".stat-card-value-text");
    uptimeValue.textContent = `${uptimePercentage.toFixed(2)}%`;

    // Update the latency card
    //TODO : Color-code against static values?
    const latencyValue = latencyCard.querySelector(".stat-card-value-text");
    latencyValue.textContent = `${avgLatency.toFixed(2)}ms`;
  }

  _updateTimelineChart(monitorResultsHistory) {
    // Step 1: Create a new array with only results that differ from the previous one
    const statusChangeResults = [];
    let lastStatus = null;
    for (let i = 0; i < monitorResultsHistory.length; i++) {
      if (monitorResultsHistory[i].value.test_passed !== lastStatus) {
        statusChangeResults.push(monitorResultsHistory[i]);
        lastStatus = monitorResultsHistory[i].value.test_passed;
      }
    }

    console.log("Simplified results array:", statusChangeResults);

    // Step 2: Calcualte a normalized "time" value for each result from the earliest to the latest timestamps
    // Also set the values for monitor-details-chart-left-time / monitor-details-chart-right-time
    const firstTimestamp = Date.parse(statusChangeResults[0].value.end_time.value);
    const lastTimestamp = Date.parse(statusChangeResults[statusChangeResults.length - 1].value.end_time.value);
    const timeRange = lastTimestamp - firstTimestamp;

    // get the monitor-details-chart-left-time and monitor-details-chart-right-time elements
    const leftTimeElement = this.element.querySelector(".monitor-details-chart-left-time");
    const rightTimeElement = this.element.querySelector(".monitor-details-chart-right-time");
    // Set the text content of the elements as just the date portion of the timestamps
    leftTimeElement.textContent = new Date(firstTimestamp).toLocaleDateString();
    rightTimeElement.textContent = new Date(lastTimestamp).toLocaleDateString();

    for (let i = 0; i < statusChangeResults.length; i++) {
      const currentTimestamp = Date.parse(statusChangeResults[i].value.end_time.value);
      if (Math.abs(timeRange) < Number.EPSILON) {
        statusChangeResults[i].normalizedTime = 0;
      }
      statusChangeResults[i].normalizedTime = (currentTimestamp - firstTimestamp) / timeRange;
    }

    console.log("Simplified results array with normalized time:", statusChangeResults);

    // Step 3:  Fully clean the chart before updating it
    const chartRootDiv = this.element.querySelector(".monitor-details-chart");
    chartRootDiv.innerHTML = "";

    // Step 4: Create the chart
    for (let i = 0; i < statusChangeResults.length; i++) {
      const bar = document.createElement("div");
      bar.className = "monitor-details-chart-bar color-by-status";
      bar.setAttribute("data-index", i);
      bar.setAttribute("data-status", statusChangeResults[i].value.test_passed ? "up" : "down");
      bar.setAttribute("data-begin-time", statusChangeResults[i].value.end_time.value);
      bar.setAttribute("data-message", statusChangeResults[i].value.reason);
      // Set data-end-time to the next status change or the end of the timeline, i.e. "now"
      if (i < statusChangeResults.length - 1) {
        bar.setAttribute("data-end-time", statusChangeResults[i + 1].value.end_time.value);
      } else {
        bar.setAttribute("data-end-time", new Date().toISOString());
      }
      // Calculate the weight (the flex value) based on the normalized time minus the previous one
      if (i > 0) {
        bar.style.flex = `${statusChangeResults[i].normalizedTime - statusChangeResults[i - 1].normalizedTime}`;
      } else {
        bar.style.flex = `${statusChangeResults[i].normalizedTime}`;
      }

      //Set listeners for tooltips
      bar.addEventListener("mousemove", (event) => {
        const tooltip = document.querySelector(".monitor-details-chart-tooltip");
        if (tooltip) {
          tooltip.setAttribute("data-target-index", event.target.getAttribute("data-index"));
          // Calculate the time right under the cursor using data-begin-time and data-end-time
          const cursorPositionNorm = event.offsetX / event.target.clientWidth;
          const cursorPositionTime = new Date(
            Date.parse(event.target.getAttribute("data-begin-time")) +
              (Date.parse(event.target.getAttribute("data-end-time")) - Date.parse(event.target.getAttribute("data-begin-time"))) * cursorPositionNorm
          ).toISOString();

          // Update the tooltip content
          const timeDiv = tooltip.querySelector(".monitor-details-chart-tooltip-time");
          const statusDiv = tooltip.querySelector(".monitor-details-chart-tooltip-status");
          const startedDiv = tooltip.querySelector(".monitor-details-chart-tooltip-started");
          const messageDiv = tooltip.querySelector(".monitor-details-chart-tooltip-message");

          timeDiv.textContent = `Time: ${cursorPositionTime}`;
          statusDiv.textContent = `Status: ${event.target.getAttribute("data-status")}`;
          startedDiv.textContent = `Since: ${event.target.getAttribute("data-end-time")}`;
          messageDiv.textContent = `Message: ${event.target.getAttribute("data-message")}`;
          tooltip.style.top = `${event.clientY + 10}px`;
          tooltip.style.left = `${event.clientX + 10}px`;

          // Calculate constrained tooltip position
          const tooltipWidth = tooltip.offsetWidth;
          const tooltipHeight = tooltip.offsetHeight;
          const windowWidth = window.innerWidth;
          const windowHeight = window.innerHeight;

          let top = event.clientY + 10; // Offset from cursor
          let left = event.clientX + 10;

          // Adjust position to stay within the window bounds
          if (left + tooltipWidth > windowWidth) {
            left = windowWidth - tooltipWidth - 10; // Move tooltip left
          }
          if (top + tooltipHeight > windowHeight) {
            top = windowHeight - tooltipHeight - 10; // Move tooltip up
          }

          tooltip.style.top = `${top}px`;
          tooltip.style.left = `${left}px`;

          // Show the tooltip
          tooltip.classList.remove("opacity-0");
          tooltip.classList.add("opacity-100");
        }
      });

      bar.addEventListener("mouseleave", (event) => {
        const tooltip = document.querySelector(".monitor-details-chart-tooltip");
        console.log("Mouse left bar" + event.target);
        if (tooltip && tooltip.getAttribute("data-target-index") === event.target.getAttribute("data-index")) {
          tooltip.classList.remove("opacity-100");
          tooltip.classList.add("opacity-0");
        }
      });

      chartRootDiv.appendChild(bar);
    }
  }

  _updateMonitorRecentEvents(monitorResultsHistory) {
    if (!monitorResultsHistory) {
      console.error("No log entries received.");
      return;
    }

    console.log("Log entries received:", monitorResultsHistory);

    // Add each to .recent-events-card .recent-events
    const recentEvents = document.querySelector(".recent-events");
    for (let i = 0; i < monitorResultsHistory.length; i++) {
      // Build the string to display as "end time, status, message" AND a special case if "exception_type" exists
      let entryText = `[${new Date(monitorResultsHistory[i].value.end_time.value).toLocaleString()}] `;
      let entryStatus = "unknown";
      if (monitorResultsHistory[i].value.test_passed) {
        entryText += "Monitor query passed";
        entryStatus = "up";
      } else if (monitorResultsHistory[i].value.exception_type) {
        entryText += `Issues encountered: ${monitorResultsHistory[i].value.exception_type}`;
        entryStatus = "error";
      } else {
        entryText += `Monitor query failed: ${monitorResultsHistory[i].value.reason}`;
        entryStatus = "down";
      }

      const newElement = document.createElement("div");
      newElement.className = "recent-events-item text-color-by-status";
      newElement.innerText = entryText;
      //Set a data-status attribute to the element to color-code it
      newElement.setAttribute("data-status", entryStatus);

      recentEvents.appendChild(newElement);

      //If the text inside newElement overflows, add a data-text-overflows attribute to it
      if (newElement.scrollHeight > newElement.clientHeight) {
        newElement.setAttribute("data-text-overflows", "true");
      }

      //Folding/unfolding behavior for long log entries
      newElement.addEventListener("click", () => {
        if (newElement.getAttribute("data-text-overflows") === "true") {
          //If it has the class ".expanded", remove it, otherwise, add it
          newElement.classList.toggle("expanded");

          //If it has the class now has ".expanded", apply a new max-height calculated from its scrollHeight, to fix the animation
          if (newElement.classList.contains("expanded")) {
            newElement.style.maxHeight = `${newElement.scrollHeight}px`;
          } else {
            newElement.style.maxHeight = "1.4rem";
          }
        }
      });
    }
  }
}
