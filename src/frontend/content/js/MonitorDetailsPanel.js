import { BaseComponent } from "./BaseComponent.js";
import { requestSingleMonitor, requestMonitorHistory } from "./PythonJsBridge.js";
import { MonitorHeaderCard } from "./MonitorHeaderCard.js";

/**
 * Handles the monitor details right-column panel
 */
export class MonitorDetailsPanel extends BaseComponent {
  static MAX_RESULTS_IN_TIMELINE = 100; // TODO: Implement using DAYS instead of number of results? E.g. 7 days

  #headerCardComponent;

  constructor(parentSelector, monitor_unique_name) {
    super(parentSelector, "monitor-details-column", "fragments/monitor-details-panel.html");
    this.monitor_unique_name = monitor_unique_name;
  }

  _onElementReady() {
    // Add your custom logic here
    console.log("MonitorDetailsColumn element is ready");

    // Get the monitor data and create the header card
    requestSingleMonitor(this.monitor_unique_name)
      .then((monitorData) => {
        this.#headerCardComponent = new MonitorHeaderCard(".monitor-header-card-container", monitorData);
        this._udpateStatsCards(monitorData);
      })
      .catch((error) => {
        console.error(`Error while fetching monitor data for ${this.monitor_unique_name}:`, error);
      });

    this.#refreshWithLatestMonitorData();

    document.addEventListener("monitor-results-received", (event) => this.#onMonitorResultsReceived(event));
  }

  #refreshWithLatestMonitorData() {
    requestSingleMonitor(this.monitor_unique_name)
      .then((monitorData) => {
        this._udpateStatsCards(monitorData);
      })
      .catch((error) => {
        console.error(`Error while fetching monitor data for ${this.monitor_unique_name}:`, error);
      });

    requestMonitorHistory(this.monitor_unique_name, MonitorDetailsPanel.MAX_RESULTS_IN_TIMELINE)
      .then((monitorResultsHistory) => {
        this._updateTimelineChart(monitorResultsHistory);
        this._updateMonitorRecentEvents(monitorResultsHistory);
      })
      .catch((error) => {
        console.error(`Error while fetching history data for ${this.monitor_unique_name}:`, error);
      });
  }

  #onMonitorResultsReceived(event) {
    // console.log(`Monitor results received event:`, event);
    if (event.detail.monitorUniqueName === this.monitor_unique_name) {
      //New data for this item, refresh contents
      this.#refreshWithLatestMonitorData();
    }
  }

  _udpateStatsCards(monitorData) {
    console.log("Updating stats cards");
    if (!monitorData || !monitorData.value) {
      console.warn("Monitor data is not available.");
      return;
    }
    console.log("Monitor data:", monitorData);

    // Prepare the data for the stats cards
    let monitorStatus;
    let monitorStatusText;
    if (monitorData.value.paused === true) {
      monitorStatus = "paused";
      monitorStatusText = "Monitoring is currently paused.";
    } else if (monitorData.value.error_preventing_execution !== null) {
      monitorStatus = "error";
      monitorStatusText = monitorData.value.error_preventing_execution;
    } else if (monitorData.value.last_query_passed === true) {
      monitorStatus = "up";
      monitorStatusText = "Monitor query passed.";
    } else if (monitorData.value.last_query_passed === false) {
      monitorStatus = "down";
      monitorStatusText = "Monitor query failed.";
    } else {
      monitorStatus = "unknown";
      monitorStatusText = "Something went wrong, monitor status unknown.";
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
    statusCard.setAttribute("title", monitorStatusText);

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
    const emptyChartElement = this.element.querySelector(".monitor-details-chart-empty");
    if (!monitorResultsHistory || monitorResultsHistory.length === 0) {
      console.log("Monitor has no history.");
      // Remove the ".display-none"  class from the .monitor-details-chart-empty element
      emptyChartElement?.classList.remove("display-none");
      return;
    } else {
      emptyChartElement?.classList.add("display-none");
    }

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

      // Calculate the weight (the flex value) based on the normalized time minus the next one
      if (i < statusChangeResults.length - 1) {
        // Not the last element, calculate flex based on the next normalized time
        bar.style.flex = Math.max(
          statusChangeResults[i + 1].normalizedTime - statusChangeResults[i].normalizedTime,
          0.01 // Minimum width to avoid collapsing
        );
      } else {
        bar.style.flex = 1 - statusChangeResults[i].normalizedTime;
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

    // Add each to .recent-events-card .recent-events
    const recentEvents = document.querySelector(".recent-events");

    // Clear the existing entries
    recentEvents.innerHTML = "";

    for (let i = monitorResultsHistory.length - 1; i >= 0; i--) {
      // Build the string to display as "end time, status, message" AND a special case if "exception_type" exists
      let entryText = `[${new Date(monitorResultsHistory[i].value.end_time.value).toLocaleString()}] `;
      let entryStatus = "error";
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
