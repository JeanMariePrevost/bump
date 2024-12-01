import { BaseComponent } from "./BaseComponent.js";
import { requestLogEntries } from "./PythonJsBridge.js";

/**
 * Handles the dashboard right-column panel
 */
export class DashboardPanel extends BaseComponent {
  constructor(parentSelector, upCount, downCount, unknownCount) {
    super(parentSelector, "dashboard-column", "fragments/dashboard-panel.html");
    this.upCount = upCount;
    this.downCount = downCount;
    this.unknownCount = unknownCount;
  }

  _onElementReady() {
    //Update the summary-card element's counts and status based
    const summaryCard = document.querySelector(".summary-card");
    if (this.upCount > 0 && this.downCount === 0 && this.unknownCount === 0) {
      summaryCard.setAttribute("data-status", "up");
      summaryCard.querySelector(".summary-card-title").innerText = "All monitors are up";
    } else if (this.downCount > 0) {
      summaryCard.setAttribute("data-status", "down");
      summaryCard.querySelector(".summary-card-title").innerText = "Some monitors are down";
    } else if (this.unknownCount > 0) {
      // TODO : Need to handle differently here? I don't think so
      summaryCard.querySelector(".summary-card-title").innerText = "Issues were encountered";
      summaryCard.setAttribute("data-status", "down");
    } else if (this.upCount + this.downCount + this.unknownCount === 0) {
      summaryCard.querySelector(".summary-card-title").innerText = "No monitors found";
      summaryCard.setAttribute("data-status", "unknown");
    }
    summaryCard.querySelector(".summary-card-count").innerText = `${this.upCount} / ${this.downCount} / ${this.unknownCount}`;

    console.log(`Monitors status counts: up=${this.upCount}, down=${this.downCount}, unknown=${this.unknownCount}`);

    // Fill the recent events with log entries
    requestLogEntries(30)
      .then((response) => {
        if (!response) {
          console.error("Failed to fetch log entries");
          return;
        }

        console.log("Log entries received:", response);

        // Add each to .recent-events-card .recent-events
        const recentEvents = document.querySelector(".recent-events");
        for (let i = 0; i < response.length; i++) {
          const newElement = document.createElement("div");
          newElement.className = "recent-events-item";
          newElement.innerText = response[i];
          //Set a data-log-level attribute to the element based on whether the entry contains "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
          if (response[i].includes("CRITICAL")) {
            newElement.setAttribute("data-log-level", "critical");
          } else if (response[i].includes("ERROR")) {
            newElement.setAttribute("data-log-level", "error");
          } else if (response[i].includes("WARNING")) {
            newElement.setAttribute("data-log-level", "warning");
          } else if (response[i].includes("INFO")) {
            newElement.setAttribute("data-log-level", "info");
          } else if (response[i].includes("DEBUG")) {
            newElement.setAttribute("data-log-level", "debug");
          } else {
            // Default to "INFO"
            newElement.setAttribute("data-log-level", "info");
          }

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
      })
      .catch((error) => {
        console.error("Error while fetching log entries:", error);
      });
  }
}
