/**
 * Load a template from a URL and return the content.
 * E.g. loadTemplate("templates/monitor-details-template.html") -> Promise<DocumentFragment> which you can then append to the DOM.
 * @param {*} url
 * @returns {Promise<DocumentFragment>} A promise that resolves to the content of the template.
 */
export async function loadTemplate(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Failed to load template: ${response.statusText}`);

    const html = await response.text();
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = html.trim();

    const template = tempDiv.querySelector("template");
    if (!template) throw new Error("No <template> element found in the loaded file.");

    return template.content;
  } catch (error) {
    console.error(error);
    return null;
  }
}
