import { BaseComponent } from "./BaseComponent.js";

/**
 * Handles the dashboard right-column panel
 */
export class DashboardPanel extends BaseComponent {
  constructor(parentSelector) {
    super(parentSelector, "dashboard-column", "fragments/dashboard-panel.html");
  }
}
