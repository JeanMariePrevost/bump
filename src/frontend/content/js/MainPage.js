import { MonitorListItem } from "./MonitorListItem.js";
import { requestMonitorsList, requestLogEntries } from "./PythonJsBridge.js";
import { DashboardPanel } from "./DashboardPanel.js";

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

  // Build the currently "hard-coded" monitor list of the main page
  requestMonitorsList()
    .then((response) => {
      if (!response) {
        console.error("Failed to fetch monitors data");
        return;
      } else if (response.length === 0) {
        console.log("Config contains no monitors");
        return;
      }

      // Populate the monitorsList and count the number of monitors by status and also use the same request to count the number of monitors up/down/unknown
      let upCount = 0;
      let downCount = 0;
      let unknownCount = 0;
      for (let i = 0; i < response.length; i++) {
        addMonitorToList(response[i].value); // Add a new MonitorListItem in the list
        if (response[i].value.last_query_passed === true) {
          upCount++;
        } else if (response[i].value.last_query_passed === false) {
          downCount++;
        } else {
          unknownCount++;
        }
      }
      // Load the right column's content
      const dashboardColumn = new DashboardPanel(".right-column", upCount, downCount, unknownCount);
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
