// pywebview_api.js

export function sendDataToPython(eventType, data) {
  //Centralized function to send data to the Python backend
  //Not sure if I,ll need special processing or error handling
  pywebview.api.send_event_to_python(eventType, data);
}

/**
 * Function to request some data from the Python backend based on an input string
 * @param {string} inputString
 * @returns {string} response
 *
 * @example
 * // If inside an async function:
 * const response_data = await testRequestDataFromPython("Hello from JavaScript!");
 *
 * @example
 * // If not inside an async function, you can use .then() to handle the response
 * testRequestDataFromPython("Hello from JavaScript!").then(response_data => {
 *  console.log("Response from Python:", response_data);
 * }
 *
 * //Or an async IIFE (a "immediate lambda")
 *   (async () => {
 *     const response_data = await getDataFromPython("My input");
 *     console.log("Received data:", response_data);
 *   })();
 */
export async function getDataFromPython(inputString) {
  try {
    const response = await pywebview.api.test_request_some_data(inputString);
    return response;
  } catch (error) {
    console.error("Error fetching data from Python backend:", error);
    throw error;
  }
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
