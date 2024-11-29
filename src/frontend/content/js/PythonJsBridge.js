// pywebview_api.js

export function sendDataToPython(eventType, data) {
  //Centralized function to send data to the Python backend
  //Not sure if I,ll need special processing or error handling
  pywebview.api.send_event_to_python(eventType, data);
}

// NOTE on requesting data from Python:
// These functions will return a promise that resolves with the data returned from the Python backend
// This means you can use async/await or .then() to handle the response, like so:
// requestWhateverFromBackend()
//   .then((response) => {
//     console.log("Received data from Python:", response);
//   })
//   .catch((error) => {
//     console.error("Error while fetching all monitors data:", error);
//   });

/**
 * Get an object containing the list of all monitors and their data
 * @returns {Promise<Array<Object>>} Promise that resolves to an array of objects, each containing the state of a monitor under its 'value' property
 */
export async function requestMonitorsList() {
  const response = await pywebview.api.request_all_monitors_data();
  return response;
}

/**
 * Pass a name to retrieve the state of a monitor
 * @param {string} monitorName
 * @returns {Promise<Object>} The monitor, with its state under the 'value' property
 */
export async function requestSingleMonitor(monitorName) {
  const response = await pywebview.api.request_monitor_data(monitorName);
  return response;
}

/**
 * Request a number of recent results for a monitor
 * @param {string} monitorName
 * @param {number} numberOfResults
 * @returns {Promise<Array<Object>>} Array of objects, each containing the state of a monitor under its 'value' property
 */
export async function requestMonitorHistory(monitorName, numberOfResults) {
  const response = await pywebview.api.request_monitor_history(monitorName, numberOfResults);
  return response;
}

//
//
//
// NOTE : To receive from Python without requesting it, you need to add an event listener to the window object
// It is accessible from the global scope, simply do something like this from anywhere in a js file:
// window.addEventListener("py_js_test_event", (event) => {
//   console.log("Received payload: ", event.detail);
//   // No parsing needed, the event.detail is already a JS object
//   // You can access the data and any attributes with dot notation like this:
//   console.log("Data received: ", event.detail.data);
// });
