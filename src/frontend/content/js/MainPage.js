import { MonitorCard } from "./MonitorCard.js";

console.log("HELLO WORLD!");
console.log("main_page.js loaded");

// Message when the page is fully loaded too
window.onload = function () {
  console.log("Page fully loaded");
};

// Holds a ref of all the cards on the page
const cards = [];

/**
 * Creates a "card" element from the given monitor data and adds it to the DOM.
 */
function addCard(monitorData) {
  if (!monitorData) {
    throw new Error("addCard: cannot create a card without monitor data");
  }

  console.log("Adding a new card to the page");
  const card = new MonitorCard(monitorData);
  cards.push(card);

  updateNoMonitorsCardVisibility();
}

/**
 * Updates the visibility of the "no monitors" card based on the number of cards on the page.
 */
function updateNoMonitorsCardVisibility() {
  const noMonitorsCard = document.getElementById("no-monitors-card");
  if (noMonitorsCard) {
    if (cards.length > 0) {
      noMonitorsCard.style.display = "none";
    } else {
      noMonitorsCard.style.display = "block";
    }
  }
}

import { sendDataToPython, getDataFromPython, requestAllMonitorsData, requestMonitorData } from "./PythonJsBridge.js";

document.addEventListener("DOMContentLoaded", () => {
  // for (let i = 0; i < 4; i++) {
  //   addCard();
  // }
  //
  // Wait for 5 seconds then send an event back to the backend
  // setTimeout(() => {
  //   sendDataToPython("js_py_test_event", { data: "Hello from JavaScript!" });
  // }, 5000);
  // Test requesting data from the backend after a delay
  // setTimeout(async () => {
  //   const response = await testRequestDataFromPython("Hello from JavaScript!");
  //   console.log("Response from Python:", response);
  // }, 3000);
  // Instant request test
  // (async () => {
  //   const response = await testRequestDataFromPython("Hello from JavaScript!");
  //   console.log("Response from Python:", response);
  // })();
});

window.addEventListener("pywebviewready", function () {
  console.log("PyWebView is ready!");
  // Test, try requesting and printing the list of all monitors, then grab the name of the 1st, and fetch the info of that monitor
  requestAllMonitorsData()
    .then((response) => {
      if (!response) {
        console.error("Failed to fetch monitors data");
        return;
      } else if (response.length === 0) {
        console.log("Config contains no monitors");
        return;
      }

      // use addCard for each monitor in response
      for (let i = 0; i < response.length; i++) {
        addCard(response[i].value);
      }
    })
    .catch((error) => {
      console.error("Error while fetching all monitors data:", error);
    });
});

window.addEventListener("py_js_test_event", (event) => {
  console.log("Event received from Python:");
  // Print each key-value pair in the event payload
  for (const key in event.detail) {
    console.log(`${key}: ${event.detail[key]}`);
  }

  //extract the "data" key from the event payload
  const data = event.detail.data;
  console.log(`data: ${data}`);
});
