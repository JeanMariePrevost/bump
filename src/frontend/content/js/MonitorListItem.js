// File: /f:/OneDrive/MyDocs/Study/TELUQ/Session 5 - Hiver 2024/INF1430 Final Project/TN3 - Actual Software/bump/src/frontend/content/js/MonitorCard.js

document.addEventListener("DOMContentLoaded", (event) => {
  console.log("Hello, world! This coming from MonitorCard.js!");
});

export class MonitorListItem {
  constructor(monitorData) {
    this.monitorData = monitorData;
    console.log(`${this.constructor.name} instance created with config:`, monitorData);
    this.addSelfToDOM();
  }

  addSelfToDOM() {
    console.log(`Adding ${this.constructor.name} to the DOM`);
    const monitorsListElement = document.querySelector(".monitors-list");
    if (monitorsListElement) {
      // Create a new div element
      const newItem = document.createElement("div");
      newItem.setAttribute("data-unique-name", this.monitorData.unique_name);
      newItem.className = "monitor-list-item";
      // newItem.innerText = this.monitorData.unique_name;
      monitorsListElement.appendChild(newItem);

      // Add the ".status-indicator" element
      const statusIndicator = document.createElement("div");
      statusIndicator.className = "monitor-list-item-status-indicator";
      if (this.monitorData.last_query_passed === true) {
        statusIndicator.setAttribute("data-status", "up");
      } else if (this.monitorData.last_query_passed === false) {
        statusIndicator.setAttribute("data-status", "down");
      } else {
        statusIndicator.setAttribute("data-status", "unknown");
      }
      newItem.appendChild(statusIndicator);

      //Add the label
      const label = document.createElement("div");
      label.className = "monitor-list-item-label";
      label.innerText = this.monitorData.unique_name;
      newItem.appendChild(label);

      //Add the "bar chart" element
      const barChart = document.createElement("div");
      barChart.className = "monitor-list-item-history";

      // Add the "bar" elements
      for (let i = 0; i < 12; i++) {
        const bar = document.createElement("div");
        bar.className = "monitor-list-item-history-bar";
        if (i < this.monitorData.last_query_duration) {
          bar.setAttribute("data-status", "up");
        } else {
          bar.setAttribute("data-status", "down");
        }
        barChart.appendChild(bar);
      }

      newItem.appendChild(barChart);
    } else {
      console.error("cards-container not found");
    }
  }
}
