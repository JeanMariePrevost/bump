import { NavbarComponent } from "./NavbarComponent.js";

// Wait for DOM content to be fully loaded before executing the fetch
document.addEventListener("DOMContentLoaded", () => {
  // Add the navbar to the page
  const navBar = new NavbarComponent(".navbar-container");
});
