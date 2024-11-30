// File: /f:/OneDrive/MyDocs/Study/TELUQ/Session 5 - Hiver 2024/INF1430 Final Project/TN3 - Actual Software/bump/src/frontend/content/js/MonitorCard.js

import { requestMonitorHistory } from "./PythonJsBridge.js";
import { MonitorDetailsColumn } from "./MonitorDetailsColumn.js";
import { loadTemplate } from "./utils.js";

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
        bar.setAttribute("data-status", "no-data");
        barChart.appendChild(bar);
      }

      newItem.appendChild(barChart);

      // Request the history data for this monitor to update the bars
      requestMonitorHistory(this.monitorData.unique_name, 12)
        .then((response) => {
          console.log(`Received history data for ${this.monitorData.unique_name}:`, response);

          //DEBUG
          const len = response.length;
          const firstElement = response[0];

          for (let i = 0; i < response.length; i++) {
            const bar = barChart.children[barChart.children.length - 1 - i]; // Make the rightmost bar the most recent
            if (response[i].value.test_passed === true) {
              bar.setAttribute("data-status", "up");
            } else if (response[i].value.test_passed === false) {
              bar.setAttribute("data-status", "down");
            } else {
              bar.setAttribute("data-status", "unknown");
            }
          }
        })
        .catch((error) => {
          console.error(`Error while fetching history data for ${this.monitorData.unique_name}:`, error);
        });

      // Add a click event listener to the item
      newItem.addEventListener("click", (event) => {
        console.log(`Clicked on ${this.monitorData.unique_name}`);
        // TODO : Open monitor details page
        //Trying stuff out
        //Completely remove everything INDE "right-column" and add a new element
        const rightColumn = document.querySelector("div.right-column");
        if (rightColumn) {
          const newRightColumn = rightColumn.cloneNode(false); // `false` clones only the element, without its children.
          rightColumn.parentNode.replaceChild(newRightColumn, rightColumn);

          // Add a new element to the right column
          const monitorDetailsColumn = new MonitorDetailsColumn(".right-column");
        }
      });
    } else {
      console.error(".monitors-list element not found");
    }
  }
}
