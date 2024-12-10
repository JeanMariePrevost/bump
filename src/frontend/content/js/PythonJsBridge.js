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
 * Requests the backend to create and return a new empty monitor
 * @returns {Promise<Object>} The new monitor, with its state under the 'value' property
 */
export async function requestNewEmptyMonitor() {
  const response = await pywebview.api.create_new_empty_monitor();
  return response;
}

/**
 * Requests the backend to create and return a new monitor duplicating an existing one
 * @param {string} baseMonitorName - The name of the monitor to duplicate
 * @returns {Promise<Object>} The new monitor, with its state under the 'value' property
 */
export async function requestNewDuplicateMonitor(baseMonitorName) {
  const response = await pywebview.api.create_new_duplicate_monitor(baseMonitorName);
  return response;
}

/**
 * Requests that a monitor be executed immediately
 * @param {string} monitorName
 * @returns {Promise<string>} Promise that resolves to "true" if the monitor was executed, or an error message if it was not
 */
export async function requestMonitorExecution(monitorName) {
  const response = await pywebview.api.request_monitor_execution(monitorName);
  return response;
}

/**
 * Requests the backend to delete a monitor
 * @param {*} monitorName
 * @returns {Promise<string>} Promise that resolves to "true" if the monitor was deleted, or an error message if it was not
 */
export async function requestMonitorDeletion(monitorName) {
  const response = await pywebview.api.request_delete_monitor(monitorName);
  return response;
}

/**
 * Requests the backend to pause/unpause a monitor
 * @param {string} monitorName
 * @param {boolean} pause - True to pause, false to unpause
 * @returns {Promise<string>} Promise that resolves to "true" if the monitor was paused/unpaused, or an error message if it was not
 */
export async function setMonitorPauseState(monitorName, pause) {
  const response = await pywebview.api.set_monitor_pause_state(monitorName, pause);
  return response;
}

/**
 * Submits a new monitor configuration to the backend, the backend validates and replies
 * @param {Object} monitorConfig - The monitor configuration object
 * @returns {Promise<string>} Promise that resolves to "true" if the configuration was accepted, or an error message if it was rejected
 */
export async function submitMonitorConfig(monitorConfig) {
  const response = await pywebview.api.submit_monitor_config(monitorConfig);
  return response;
}

/**
 * Request a number of recent results for a monitor
 * @param {string} monitorName
 * @param {number} numberOfResults
 * @returns {Promise<Array<Object>>} Array of objects, each containing the state of a monitor under its 'value' property
 */
export async function requestMonitorHistory(monitorName, numberOfResults) {
  try {
    const response = await pywebview.api.request_monitor_history(monitorName, numberOfResults);
    return response || [];
  } catch (error) {
    console.error("Error while fetching monitor history data:", error);
    return [];
  }
}

/**
 * Request a number of application log entries
 * @param {number} numberOfEntries
 * @returns {Promise<Array<Object>>} Array of objects, each containing the log entry under its 'value' property
 */
export async function requestLogEntries(numberOfEntries) {
  // Signature for reference:
  // request_log_entries(self, max_number_of_entries: int, min_level: str = "INFO", include_general: bool = True, include_monitoring: bool = True)
  const response = await pywebview.api.request_log_entries(numberOfEntries, "INFO", true, true);
  return response;
}

/**
 * Requests the app settings object
 * @returns {Promise<Object>} The settings object
 */
export async function requestAppSettings() {
  const response = await pywebview.api.request_app_settings();
  return response;
}

/**
 * Submits new settings to the backend
 * @param {Object} newSettings - The new settings object
 * @returns {Promise<string>} Promise that resolves to "true" if the settings were accepted, or an error message if they were rejected
 */
export async function submitAppSettings(newSettings) {
  const response = await pywebview.api.submit_app_settings(newSettings);
  return response;
}

/**
 * Request the backend to prompt for a new SMTP password
 * @returns {Promise<string>} Promise that resolves to "true" if the prompt was shown, or an error message if it was not
 */
export async function requestEnterNewSmtpPassword() {
  const response = await pywebview.api.request_enter_new_smtp_password();
  return response;
}

/**
 * Request the backend to delete the stored SMTP password
 * @returns {Promise<string>} Promise that resolves to "true" if the password was deleted, or an error message if it was not
 */
export async function requestDeleteSmtpPassword() {
  const response = await pywebview.api.request_delete_smtp_password();
  return response;
}

/**
 * Request the backend to confirm whether the stored SMTP password is set
 * @returns {Promise<boolean>} Promise that resolves to true if the password is set, false if it is not
 */
export async function requestSmtpPasswordExists() {
  const response = await pywebview.api.request_smtp_password_exists();
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
