import { MonitorCard } from "./MonitorCard.js";

console.log("HELLO WORLD!");
console.log("main_page.js loaded");

// Message when the page is fully loaded too
window.onload = function () {
  console.log("Page fully loaded");
};

// Holds a ref of all the cards on the page
const cards = [];

/**
 * Function to add a new card to the page
 */
function addCard() {
  console.log("Adding a new card to the page");
  const card = new MonitorCard();
  cards.push(card);
}

document.addEventListener("DOMContentLoaded", () => {
  for (let i = 0; i < 4; i++) {
    addCard();
  }
});

window.addEventListener("test_event", (event) => {
  console.log("Event received from Python:");
  // Print each key-value pair in the event payload
  for (const key in event.detail) {
    console.log(`${key}: ${event.detail[key]}`);
  }

  //extract the "data" key from the event payload
  const data = event.detail.data;
  console.log(`data: ${data}`);
});
