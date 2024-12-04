// File: /f:/OneDrive/MyDocs/Study/TELUQ/Session 5 - Hiver 2024/INF1430 Final Project/TN3 - Actual Software/bump/src/frontend/content/js/MonitorCard.js

import { requestMonitorHistory, requestSingleMonitor } from "./PythonJsBridge.js";
import { MonitorDetailsPanel } from "./MonitorDetailsPanel.js";

document.addEventListener("DOMContentLoaded", (event) => {
  console.log("Hello, world! This coming from MonitorCard.js!");
});

export class MonitorListItem {
  constructor(monitorData) {
    this.monitorData = monitorData;
    console.log(`${this.constructor.name} instance created with config:`, monitorData);
    this.element = this.addSelfToDOM();

    if (this.element) {
      this.#refreshStatusIndicator();
      this.#refreshHistoryBars();

      // Add various global event listeners like when an item should appear as selected or when it should refresh itself
      document.addEventListener("monitor-edit-panel-ready", (event) => this.#onMonitorEditPanelReady(event));
      document.addEventListener("monitor-results-received", (event) => this.#onMonitorResultsReceived(event));
    } else {
      console.error("Could not add self to DOM");
    }
  }

  #onMonitorEditPanelReady(event) {
    // console.log(`MonitorEditPanel ready event received:`, event);
    if (event.detail.monitorUniqueName === this.monitorData.unique_name) {
      // Something else triggered the editing of THIS item's monitor, so select it
      const items = document.querySelectorAll(".monitor-list-item");
      items.forEach((item) => {
        item.classList.remove("selected-monitor");
      });
      const item = document.querySelector(`.monitor-list-item[data-unique-name="${this.monitorData.unique_name}"]`);
      if (item) {
        item.classList.add("selected-monitor");
      }
    }
  }

  #onMonitorResultsReceived(event) {
    // console.log(`Monitor results received event:`, event);
    if (event.detail.monitorUniqueName === this.monitorData.unique_name) {
      //New data for this item, refresh
      this.#refreshWithLatestMonitorData();
    }
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
        bar.setAttribute("data-status", "no-data");
        barChart.appendChild(bar);
      }

      newItem.appendChild(barChart);

      // Add a click event listener to the item
      newItem.addEventListener("click", (event) => this.#onClicked(event));
      return newItem;
    } else {
      console.error(".monitors-list element not found");
    }
  }

  #onClicked(event) {
    console.log(`Clicked on ${this.monitorData.unique_name}`);
    // Remove the "selected-monitor" class from all items, place on self
    const items = document.querySelectorAll(".monitor-list-item");
    items.forEach((item) => {
      item.classList.remove("selected-monitor");
    });
    event.currentTarget.classList.add("selected-monitor");

    //Completely remove everything in "right-column" and add a new element
    const rightColumn = document.querySelector("div.right-column");
    if (rightColumn) {
      const newRightColumn = rightColumn.cloneNode(false); // `false` clones only the element, without its children.
      rightColumn.parentNode.replaceChild(newRightColumn, rightColumn);

      // Add a new element to the right column
      const monitorDetailsColumn = new MonitorDetailsPanel(".right-column", this.monitorData.unique_name);
    }
  }

  #refreshWithLatestMonitorData() {
    // Request the latest data for this monitor
    requestSingleMonitor(this.monitorData.unique_name)
      .then((response) => {
        console.log(`Received data for ${this.monitorData.unique_name}:`, response);
        this.monitorData = response.value;
        this.#refreshStatusIndicator();
        this.#refreshHistoryBars();
      })
      .catch((error) => {
        console.error(`Error while fetching data for ${this.monitorData.unique_name}:`, error);
      });
  }

  #refreshStatusIndicator() {
    // statusIndicator.className = "monitor-list-item-status-indicator";
    const statusIndicator = this.element.querySelector(".monitor-list-item-status-indicator");
    if (this.monitorData.last_query_passed === true) {
      statusIndicator.setAttribute("data-status", "up");
    } else if (this.monitorData.last_query_passed === false) {
      statusIndicator.setAttribute("data-status", "down");
    } else {
      statusIndicator.setAttribute("data-status", "unknown");
    }
  }

  #refreshHistoryBars() {
    const barChart = this.element.querySelector(".monitor-list-item-history");
    if (!barChart) {
      console.error("Could not find the bar chart element");
      return;
    }

    // Request the history data for this monitor to update the bars
    requestMonitorHistory(this.monitorData.unique_name, 12)
      .then((response) => {
        console.log(`Received history data for ${this.monitorData.unique_name}:`, response);

        for (let i = 0; i < response.length; i++) {
          const bar = barChart.children[barChart.children.length - 1 - i]; // Start from the end
          const status = response[response.length - 1 - i].value.test_passed;
          if (status === true) {
            bar.setAttribute("data-status", "up");
          } else if (status === false) {
            bar.setAttribute("data-status", "down");
          } else {
            bar.setAttribute("data-status", "unknown");
          }
        }
      })
      .catch((error) => {
        console.error(`Error while fetching history data for ${this.monitorData.unique_name}:`, error);
      });
  }
}
