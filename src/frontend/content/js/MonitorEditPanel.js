import { BaseComponent } from "./BaseComponent.js";

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
  }
}
