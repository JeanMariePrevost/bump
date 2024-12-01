import { BaseComponent } from "./BaseComponent.js";
import { requestSingleMonitor } from "./PythonJsBridge.js";

/**
 * Handles the monitor editing form in the right-column panel
 */
export class MonitorEditPanel extends BaseComponent {
  constructor(parentSelector, monitor_unique_name) {
    super(parentSelector, "monitor-edit-column", "fragments/monitor-edit-panel.html");
    this.monitor_unique_name = monitor_unique_name;
  }

  _onElementReady() {
    // Add your custom logic here
    console.log("MonitorEditPanel element is ready");

    // Get monitor data from the backend
    requestSingleMonitor(this.monitor_unique_name).then((response) => {
      if (!response) {
        console.error("Failed to fetch monitor data");
        return;
      }

      console.log("Monitor data received:", response);
      this.#fillForm(response);
    });
  }

  #fillForm(monitorData) {
    // Populate the form with the monitor data
    // form.querySelector(".monitor-name").value = monitorData.name;
    // form.querySelector(".monitor-url").value = monitorData.url;
    // form.querySelector(".monitor-interval").value = monitorData.interval;
    // form.querySelector(".monitor-expected").value = monitorData.expected;
    // form.querySelector(".monitor-notify-email").value = monitorData.notify_email;

    //Populate the form with the monitor data
    const form = document.querySelector(".settings-form");
    form.name.value = monitorData.value.unique_name;
    form.url.value = monitorData.value.query.value.url;
    form.interval.value = monitorData.value.period_in_seconds;
    form.condition.value = monitorData.value.query.type; // TODO Implement a way to comminucate this with the backed? Predefined strings? Use an "adapter"?
    form.retries.value = monitorData.value.query.value._retries;
    form["retries-interval"].value = "Not yet implemented"; // TODO: Implement retries_interval
    form.threshold.value = "Not yet implemented"; // TODO: Implement thresholds (e.g. "tolerate 1", or "2 out of 5"...)
    form["threshold-value"].value = "Not yet implemented";
    form["alert-profile"].value = "Not yet implemented"; // TODO: Implement alert profiles defined by the user

    // Example monitorData for reference:
    //   {
    //     "unique_name": "Google",
    //     "query": {
    //         "type": "queries.http_query.HttpQuery",
    //         "value": {
    //             "_retries": 0,
    //             "url": "http://www.google.com",
    //             "timeout": 10
    //         }
    //     },
    //     "period_in_seconds": 16,
    //     "_next_run_time": {
    //         "type": "datetime.datetime",
    //         "value": "2024-11-27T17:45:01.130393"
    //     },
    //     "last_query_passed": true,
    //     "time_at_last_status_change": {
    //         "type": "datetime.datetime",
    //         "value": "2024-11-24T14:23:47.839640"
    //     },
    //     "stats_avg_uptime": 1,
    //     "stats_avg_latency": 0.1603216944444445
    // }

    //   <div class="card-content">
    //   <form class="settings-form">
    //     <!-- Name -->
    //     <div class="form-group">
    //       <label for="name">Name</label>
    //       <input type="text" id="name" name="name" placeholder="Enter monitor name" />
    //     </div>

    //     <!-- URL -->
    //     <div class="form-group">
    //       <label for="url">URL</label>
    //       <input type="text" id="url" name="url" placeholder="Enter URL" />
    //     </div>

    //     <!-- Interval -->
    //     <div class="form-group">
    //       <label for="interval">Interval (in seconds)</label>
    //       <input type="text" id="interval" name="interval" placeholder="Enter interval" />
    //     </div>

    //     <!-- Condition -->
    //     <div class="form-group">
    //       <label for="condition">Condition</label>
    //       <select id="condition" name="condition">
    //         <option value="status">Status Code</option>
    //         <option value="response_time">Response Time</option>
    //         <option value="content_match">Content Match</option>
    //       </select>
    //     </div>

    //     <!-- Retries -->
    //     <div class="form-group">
    //       <label for="retries">Retries</label>
    //       <input type="text" id="retries" name="retries" placeholder="Number of retries" />
    //     </div>

    //     <!-- Retries Interval -->
    //     <div class="form-group">
    //       <label for="retries-interval">Retries Interval (in seconds)</label>
    //       <input type="text" id="retries-interval" name="retries-interval" placeholder="Interval between retries" />
    //     </div>

    //     <!-- Threshold -->
    //     <div class="form-group threshold-group">
    //       <label for="threshold">Threshold</label>
    //       <div class="threshold-wrapper">
    //         <select id="threshold" name="threshold">
    //           <option value="time">Time</option>
    //           <option value="count">Count</option>
    //         </select>
    //         <input type="text" id="threshold-value" name="threshold-value" placeholder="Enter value" />
    //       </div>
    //     </div>

    //     <!-- Alert Profile -->
    //     <div class="form-group">
    //       <label for="alert-profile">Alert Profile</label>
    //       <select id="alert-profile" name="alert-profile">
    //         <option value="email">Email</option>
    //         <option value="sms">SMS</option>
    //         <option value="webhook">Webhook</option>
    //       </select>
    //     </div>
    //   </form>
    // </div>
  }
}
