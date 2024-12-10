import { requestAppSettings } from "./PythonJsBridge.js";

/**
 * Load a fragment from a URL and return the content.
 * E.g. loadfragment("fragments/monitor-details.html") -> Promise<DocumentFragment> which you can then append to the DOM.
 * @param {*} url
 * @returns {Promise<DocumentFragment>} A promise that resolves to the content of the fragment.
 */
export async function loadFragment(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Failed to load fragment: ${response.statusText}`);

    const html = await response.text();

    const template = document.createElement("template");
    template.innerHTML = html.trim(); // Parse HTML without adding unnecessary nodes.

    return template.content; // Directly return the parsed content as a DocumentFragment.
  } catch (error) {
    console.error(error);
    return null;
  }
}

/**
 * Lookup table for query option names to backend classes equivalence.
 */
export const queryTypeMapping = {
  http_simple: "queries.http_query.HttpQuery",
  http_content: "queries.http_content_query.HttpContentQuery",
  http_headers: "queries.http_headers_query.HttpHeadersQuery",
  http_status_code: "queries.http_status_code_query.HttpStatusCodeQuery",
  http_regex: "queries.http_regex_query.HttpRegexQuery",
  rendered_content_regex: "queries.rendered_content_regex_query.RenderedContentRegexQuery",
};

/**
 * Converts a frontend query option key to its backend class name.
 * @param {string} queryType - The frontend key.
 * @returns {string|null} - The backend class name, or null if the key doesn't exist.
 */
export function queryTypeNameToBackendClass(queryType) {
  const className = queryTypeMapping[queryType];
  if (!className) console.warn(`No backend query class found for frontend key: ${queryType}`);
  return className || null;
}

/**
 * Converts a backend class name to its frontend query option key.
 * @param {string} backendValue - The backend class name.
 * @returns {string|null} - The frontend key, or null if the class name doesn't exist.
 */
export function backendQueryClassToQueryTypeName(backendValue) {
  const entry = Object.entries(queryTypeMapping).find(([, value]) => value === backendValue);
  if (!entry) {
    console.warn(`No frontend query type found for backend class: ${backendValue}`);
  }
  return entry ? entry[0] : null;
}

export function applyTheme() {
  requestAppSettings().then((settings) => {
    const theme = settings.general_theme;
    if (theme === "dark") {
      // Add the "[general-theme="dark"]" attribute to the body tag
      console.log("Applying dark theme");
      document.body.setAttribute("general-theme", "dark");
    } else {
      console.log("general_theme = " + theme + ", applying default theme");
      // Nothing atm, only dark and default
    }
  });
}
