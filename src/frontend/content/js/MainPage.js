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
 * Function to add a new card to the page
 */
function addCard() {
  console.log("Adding a new card to the page");
  const card = new MonitorCard();
  cards.push(card);
}

import { sendDataToPython, getDataFromPython, requestAllMonitorsData, requestMonitorData } from "./PythonJsBridge.js";

document.addEventListener("DOMContentLoaded", () => {
  for (let i = 0; i < 4; i++) {
    addCard();
  }

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

  // (async () => {
  //   const the_actual_data = await getDataFromPython("My input");
  //   console.log("Received data:", the_actual_data);
  // })();

  getDataFromPython("Hello from JavaScript!").then((response) => {
    console.log("Response from Python:", response);
  });

  // Test, try requesting and printing the list of all monitors, then grab the name of the 1st, and fetch the info of that monitor
  requestAllMonitorsData()
    .then((response) => {
      console.log("All monitors data:");
      console.log(response);
      console.log("Type of response:", typeof response);
      // console.log("GOing to parse the response");
      // const responseAsObject = JSON.parse(response);
      // console.log("Response parsed as object:");
      // console.log(responseAsObject);
      // const firstMonitorName = responseAsObject[0].value.unique_name;
      // console.log("First monitor name:", firstMonitorName);
      // console.log("Requesting data for monitor:", firstMonitorName);
      const firstMonitorName = response[0].value.unique_name;
      console.log("First monitor name:", firstMonitorName);
      console.log("Requesting data for monitor:", firstMonitorName);

      requestMonitorData(firstMonitorName).then((monitorData) => {
        console.log("Data for monitor " + firstMonitorName + ":", monitorData);
      });
    })
    .catch((error) => {
      console.error("Error while fetching all monitors data:", error);
    });

  // const result = fetchDataFromPython("The JS input was this1.");
  // // DEBUG: Print the contents and the type of the result
  // console.log("Result from fetchDataFromPython:", result);
  // console.log("Type of result:", typeof result);

  // (async () => {
  //   try {
  //     const response = await testRequestDataFromPython("The JS input was this.");
  //     console.log("Response from Python:", response.data);
  //   } catch (error) {
  //     console.error("Error while fetching data from Python:", error);
  //   }
  // })();
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
