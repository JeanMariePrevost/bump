import { NavbarComponent } from "./NavbarComponent.js";
import { applyTheme } from "./utils.js";

// Wait for DOM content to be fully loaded before executing the fetch
document.addEventListener("DOMContentLoaded", () => {
  // Add the navbar to the page
  const navBar = new NavbarComponent(".navbar-container");

  // Intercept external link clicks and open them in the default browser
  document.addEventListener("click", function (event) {
    // Check if the clicked element is a link with the 'external-link' class
    if (event.target.tagName === "A" && event.target.classList.contains("external-link")) {
      const url = event.target.href;
      event.preventDefault(); // Prevent the default link behavior
      window.open(url); // Open in the default browser
    }
  });

  // Fetch metadata.json file and extract version and releaseDate
  fetch("/metadata.json")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      // Update the DOM elements with the fetched metadata
      document.getElementById("version-text").textContent = `Version ${data.version}`;
      document.getElementById("release-date-text").textContent = `Released on ${data.releaseDate}`;
    })
    .catch((error) => {
      console.error("Error fetching metadata:", error);
    });
});

window.addEventListener("pywebviewready", function () {
  applyTheme();
});
