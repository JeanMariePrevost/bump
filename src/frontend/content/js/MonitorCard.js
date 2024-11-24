// File: /f:/OneDrive/MyDocs/Study/TELUQ/Session 5 - Hiver 2024/INF1430 Final Project/TN3 - Actual Software/bump/src/frontend/content/js/MonitorCard.js

document.addEventListener("DOMContentLoaded", (event) => {
  console.log("Hello, world! This coming from MonitorCard.js!");
});

export class MonitorCard {
  constructor() {
    console.log("MonitorCard instance created!");
    this.addSelfToPage();
  }

  sayHello() {
    console.log("Hello from MonitorCard!");
  }

  addSelfToPage() {
    console.log("Adding MonitorCard to page.");
    const cardContainer = document.getElementById("cards-container");
    if (cardContainer) {
      const card = document.createElement("div");
      card.className = "card";
      card.innerText = "This is a dummy card";
      cardContainer.appendChild(card);
    } else {
      console.error("cards-container not found");
    }
  }
}
