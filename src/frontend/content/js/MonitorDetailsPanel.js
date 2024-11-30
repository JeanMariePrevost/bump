import { BaseComponent } from "./BaseComponent.js";

/**
 * Handles the monitor details right-column panel
 */
export class MonitorDetailsColumn extends BaseComponent {
  constructor(parentSelector) {
    super(parentSelector, "monitor-details-column", "fragments/monitor-details-panel.html");
  }
}
