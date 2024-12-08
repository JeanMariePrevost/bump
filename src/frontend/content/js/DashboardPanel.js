import { BaseComponent } from "./BaseComponent.js";
import { requestLogEntries, requestMonitorsList } from "./PythonJsBridge.js";

/**
 * Handles the dashboard right-column panel
 * @param {string} parentSelector - The selector for the parent element to append the panel to
 * @param {Object[]} monitorListthis.monitorListResponseDataData - The this.monitorListResponseData object from the monitor list request
 */
export class DashboardPanel extends BaseComponent {
  static LOG_ENTRIES_LIMIT = 100; // The maximum number of log entries to fetch and display on the dashboard

  constructor(parentSelector, monitorListResponseDataData) {
    super(parentSelector, "dashboard-column", "fragments/dashboard-panel.html");
    this.monitorListResponseData = monitorListResponseDataData;
  }

  _onElementReady() {
    if (!this.monitorListResponseData) {
      console.error("No monitor list data provided to the DashboardPanel");
      return;
    } else if (this.monitorListResponseData.length === 0) {
      console.log("Config contains no monitors");
    }

    this.#updateSummaryCard(this.monitorListResponseData);
    this.#updateRecentEvents();

    this.addManagedEventListener(window, "new_monitor_results_in_backend", () => {
      // Refresh monitorListResponseData and update the summary card and recent events
      requestMonitorsList().then((response) => {
        if (!response) {
          console.error("Failed to fetch monitor list");
          return;
        }

        this.monitorListResponseData = response;
        this.#updateSummaryCard(this.monitorListResponseData);
        this.#updateRecentEvents();
      });
    });
  }

  #updateRecentEvents() {
    requestLogEntries(DashboardPanel.LOG_ENTRIES_LIMIT)
      .then((response) => {
        if (!response) {
          console.error("Failed to fetch log entries");
          return;
        }

        //TODO - Add entires until we reach one that is already displayed, then stop?

        // Clear the existing log entries
        const recentEvents = document.querySelector(".recent-events");
        const scrollTop = recentEvents.parentElement.scrollTop; // Save the current scroll position
        recentEvents.innerHTML = "";

        function formatLogEntryElement(logEntryElement, rawText) {
          // Kinda jank/fragile method of applying color and formatting to log entries
          // TODO - Come up with a more robust system than regex... tight coupling between string formats... at least it's visual-only
          let processedText = rawText;

          // Trim the timestamp to make it slightly easier to read (e.g. from "2024-12-07 15:27:14,060 " to "2024-12-07 15:27:14 ")
          const timestampRegex = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}/;
          const timestampMatch = processedText.match(timestampRegex);
          if (timestampMatch) {
            const trimmedTimestamp = timestampMatch[0].replace(/,\d{3}$/, ""); // Remove milliseconds
            processedText = processedText.replace(timestampRegex, trimmedTimestamp);
          }

          // Remove the module:line part of the log entry for anything that isn't a ERROR/CRITICAL
          // E.g. " (monitor.log_monitor_event:ln96) "
          if (!processedText.includes("[ERROR]") && !processedText.includes("[CRITICAL]")) {
            const moduleLineRegex = /\s\(.+:.*?\d+\)\s/;
            const moduleLineMatch = processedText.match(moduleLineRegex);
            if (moduleLineMatch) {
              processedText = processedText.replace(moduleLineRegex, " ");
            }
          }

          // Apply color to the log level and remove it from the text
          const logLevelRegex = /(\[DEBUG\]|\[INFO\]|\[WARNING\]|\[ERROR\]|\[CRITICAL\])/;
          const logLevelMatch = processedText.match(logLevelRegex);
          if (logLevelMatch) {
            const logLevel = logLevelMatch[0].replace(/\[|\]/g, "");
            logEntryElement.setAttribute("data-log-level", logLevel.toLowerCase());
            processedText = processedText.replace(logLevelRegex, "");
          } else {
            logEntryElement.setAttribute("data-log-level", "info");
          }

          // HACK - Apply special case coloring for good/bad monitoring events
          if (processedText.includes("onitor is back online")) {
            logEntryElement.setAttribute("data-extra-event-type", "good");
          }
          if (processedText.includes("onitor is down")) {
            logEntryElement.setAttribute("data-extra-event-type", "bad");
          }

          // Apply the text to the element
          logEntryElement.innerText = processedText;
        }

        // Add the new log entries
        for (let i = 0; i < response.length; i++) {
          const newElement = document.createElement("div");
          newElement.className = "recent-events-item";
          formatLogEntryElement(newElement, response[i]);

          recentEvents.appendChild(newElement);

          //If the text inside newElement overflows, add a data-text-overflows attribute to it
          if (newElement.scrollHeight > newElement.clientHeight) {
            newElement.setAttribute("data-text-overflows", "true");
          }

          //Folding/unfolding behavior for long log entries
          this.addManagedEventListener(newElement, "click", () => {
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

        // Restore the scroll position
        recentEvents.parentElement.scrollTop = scrollTop;
      })
      .catch((error) => {
        console.error("Error while fetching log entries:", error);
      });
  }

  #updateSummaryCard(monitorListResponseData) {
    let upCount = 0;
    let downCount = 0;
    let pausedCount = 0;
    let errorCount = 0;
    for (let i = 0; i < monitorListResponseData.length; i++) {
      if (monitorListResponseData[i].value.paused === true) {
        pausedCount++;
      } else if (monitorListResponseData[i].value.error_preventing_execution !== null) {
        errorCount++;
      } else if (monitorListResponseData[i].value.last_query_passed === true) {
        upCount++;
      } else if (monitorListResponseData[i].value.last_query_passed === false) {
        downCount++;
      } else {
        errorCount++;
      }
    }

    //Update the summary-card element's counts and status based
    // Paused monitors are not used here, regardless of their status
    const summaryCard = document.querySelector(".summary-card");
    if (upCount > 0 && downCount === 0 && errorCount === 0) {
      summaryCard.setAttribute("data-status", "up");
      summaryCard.querySelector(".summary-card-title").innerText = "All monitors are up";
    } else if (downCount > 0) {
      summaryCard.setAttribute("data-status", "down");
      summaryCard.querySelector(".summary-card-title").innerText = "Some monitors are down";
      summaryCard.classList.add("shake-animation");
    } else if (errorCount > 0) {
      summaryCard.querySelector(".summary-card-title").innerText = "Issues were encountered";
      summaryCard.setAttribute("data-status", "error");
      summaryCard.classList.add("shake-animation");
    } else if (upCount + downCount + errorCount === 0) {
      summaryCard.querySelector(".summary-card-title").innerText = "No monitors found";
      summaryCard.setAttribute("data-status", "no-data");
    }

    // const summaryCard = document.querySelector(".summary-card-count");
    const countUpSpan = summaryCard.querySelector(".count-up");
    const countDownSpan = summaryCard.querySelector(".count-down");
    const countPausedSpan = summaryCard.querySelector(".count-paused");
    const countErrorSpan = summaryCard.querySelector(".count-error");

    countUpSpan.innerText = upCount;
    countDownSpan.innerText = downCount;
    countPausedSpan.innerText = pausedCount;
    countErrorSpan.innerText = errorCount;

    // Set the tooltips
    summaryCard.querySelector(".count-up").setAttribute("title", upCount === 1 ? `1 monitor is up` : `${upCount} monitors are up`);
    summaryCard.querySelector(".count-down").setAttribute("title", downCount === 1 ? `1 monitor is down` : `${downCount} monitors are down`);
    summaryCard.querySelector(".count-paused").setAttribute("title", pausedCount === 1 ? `1 monitor is paused` : `${pausedCount} monitors are paused`);
    summaryCard.querySelector(".count-error").setAttribute("title", errorCount === 1 ? `1 monitor has issues` : `${errorCount} monitors have issues`);

    // Color the individual counts using data-color-type="good", "bad", "neutral"
    if (upCount > 0) {
      summaryCard.querySelector(".count-up").setAttribute("data-color-type", "good");
    } else {
      summaryCard.querySelector(".count-up").setAttribute("data-color-type", "neutral");
    }

    if (downCount > 0) {
      summaryCard.querySelector(".count-down").setAttribute("data-color-type", "bad");
    } else {
      summaryCard.querySelector(".count-down").setAttribute("data-color-type", "neutral");
    }

    // Paused count is always neutral
    summaryCard.querySelector(".count-paused").setAttribute("data-color-type", "neutral");

    if (errorCount > 0) {
      summaryCard.querySelector(".count-error").setAttribute("data-color-type", "bad");
    } else {
      summaryCard.querySelector(".count-error").setAttribute("data-color-type", "neutral");
    }

    console.log(`Monitors status counts: up=${upCount}, down=${downCount}, unknown=${errorCount}`);
  }
}
