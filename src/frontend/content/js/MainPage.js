import { MonitorListItem } from "./MonitorListItem.js";
import { requestMonitorsList, requestLogEntries } from "./PythonJsBridge.js";

// window.onload = function () {
//   console.log("Page fully loaded");
// };

// Holds a ref of all the MonitorListItem loaded
const monitorsInList = [];

/**
 * Creates a "monitorListItem" element from the given monitor data, which adds itself to the DOM.
 */
function addMonitorToList(monitorData) {
  if (!monitorData) {
    throw new Error("addCard: cannot create a card without monitor data");
  }

  console.log("Adding a new card to the page");
  const newItem = new MonitorListItem(monitorData);
  monitorsInList.push(newItem);

  updateNoMonitorsElementVisibility();
}

/**
 * Updates the visibility of the "no monitors" element in the list based on the number of cards on the page.
 */
function updateNoMonitorsElementVisibility() {
  // TODO: Add a special fake monitor item to the list with a "no monitors" label if monitorsInList.length > 0
}

window.addEventListener("pywebviewready", function () {
  // You can now use the pywebview.api object to interact with the Python backend

  // Testing out the request of log entries
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

  requestMonitorsList()
    .then((response) => {
      if (!response) {
        console.error("Failed to fetch monitors data");
        return;
      } else if (response.length === 0) {
        console.log("Config contains no monitors");
        return;
      }

      // Populate the monitorsList and count the number of monitors by status
      let upCount = 0;
      let downCount = 0;
      let unknownCount = 0;
      for (let i = 0; i < response.length; i++) {
        addMonitorToList(response[i].value);
        if (response[i].value.last_query_passed === true) {
          upCount++;
        } else if (response[i].value.last_query_passed === false) {
          downCount++;
        } else {
          unknownCount++;
        }
      }

      //Update the summary-card element
      const summaryCard = document.querySelector(".summary-card");
      if (upCount > 0 && downCount === 0 && unknownCount === 0) {
        summaryCard.setAttribute("data-status", "up");
        summaryCard.querySelector(".summary-card-title").innerText = "All monitors are up";
      } else if (downCount > 0) {
        summaryCard.setAttribute("data-status", "down");
        summaryCard.querySelector(".summary-card-title").innerText = "Some monitors are down";
      } else if (unknownCount > 0) {
        // TODO : Need to handle differently here? I don't think so
        summaryCard.querySelector(".summary-card-title").innerText = "Issues were encountered";
        summaryCard.setAttribute("data-status", "down");
      } else if (upCount + downCount + unknownCount === 0) {
        summaryCard.querySelector(".summary-card-title").innerText = "No monitors found";
        summaryCard.setAttribute("data-status", "unknown");
      }
      summaryCard.querySelector(".summary-card-count").innerText = `${upCount}/${downCount}/${unknownCount}`;

      console.log(`Monitors status counts: up=${upCount}, down=${downCount}, unknown=${unknownCount}`);
    })
    .catch((error) => {
      console.error("Error while fetching all monitors data:", error);
    });
});

// Testing out events, they should be globally accessible
// window.addEventListener("py_js_test_event", (event) => {
//   console.log("Event received from Python:");
//   // Print each key-value pair in the event payload
//   for (const key in event.detail) {
//     console.log(`${key}: ${event.detail[key]}`);
//   }

//   //extract the "data" key from the event payload
//   const data = event.detail.data;
//   console.log(`data: ${data}`);
// });
