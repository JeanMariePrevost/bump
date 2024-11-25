// pywebview_api.js

export function sendDataToPython(eventType, data) {
  //Centralized function to send data to the Python backend
  //Not sure if I,ll need special processing or error handling
  pywebview.api.send_event_to_python(eventType, data);
}

// NOTE : To receive from Python, you need to add an event listener to the window object
// It is accessible from the global scope, simply do something like:
// window.addEventListener("py_js_test_event", (event) => {
//   console.log("Received payload: ", event.detail);
//   // No parsing needed, the event.detail is already a JS object
//   // You can access the data and any attributes with dot notation like this:
//   console.log("Data received: ", event.detail.data);
// });
