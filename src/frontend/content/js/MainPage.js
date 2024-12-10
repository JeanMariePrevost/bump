import { MonitorListItem } from "./MonitorListItem.js";
import { requestMonitorsList, requestLogEntries, requestNewEmptyMonitor } from "./PythonJsBridge.js";
import { DashboardPanel } from "./DashboardPanel.js";
import { MonitorEditPanel } from "./MonitorEditPanel.js";
import { NavbarComponent } from "./NavbarComponent.js";
import { applyTheme } from "./utils.js";

// Holds a ref of all the MonitorListItem loaded
const monitorsInList = [];

/**
 * Creates a "monitorListItem" element from the given monitor data, which adds itself to the DOM.
 */
export function addMonitorToList(monitorData) {
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
  // TODO: Add a special item/div to the list with a "no monitors" label if monitorsInList.length > 0
}

function _onCardTitleButtonClick(event) {
  const action = event.target.getAttribute("data-action");
  console.log(`Clicked on card-title-button with data-action: ${action}`);

  switch (action) {
    case "new-monitor":
      console.log("Create a new monitor");
      // Ask backend to create a new monitor and receive the new monitor's data
      requestNewEmptyMonitor().then((response) => {
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
      });
      break;
    default:
      console.log("Unknown action");
      break;
  }
}

window.addEventListener("pywebviewready", function () {
  // You can now use the pywebview.api object to interact with the Python backend

  //Get url parameters, look for monitor_edit, which tells you to jump to that monitor's edit panel (e.g. because it was just renamed)
  const urlParams = new URLSearchParams(window.location.search);
  const monitorEdit = urlParams.get("monitor_edit");

  applyTheme();
  const navBar = new NavbarComponent(".navbar-container");

  // Build the currently "hard-coded" monitor list of the main page
  requestMonitorsList()
    .then((response) => {
      if (!response) {
        console.error("Failed to fetch monitors data");
        return;
      } else if (response.length === 0) {
        console.log("Config contains no monitors");
        // return;
      }

      // Populate the monitorsList
      for (let i = 0; i < response.length; i++) {
        addMonitorToList(response[i].value); // TODO: Move to a component?
      }

      if (monitorEdit && monitorEdit.length > 0) {
        console.log(`Page loading with monitor_edit parameter: ${monitorEdit}`);
        // Jump to the monitor edit panel
        new MonitorEditPanel(".right-column", monitorEdit);
      } else {
        // Default behavior, load the dashboard panel
        new DashboardPanel(".right-column", response);
      }
    })
    .catch((error) => {
      console.error("Error while fetching all monitors data:", error);
    });

  // Listen for clicks to any "card-title-button" elements
  const cardTitleButtons = document.querySelectorAll(".card-title-button");
  cardTitleButtons.forEach((button) => {
    button.addEventListener("click", _onCardTitleButtonClick);
  });
});
