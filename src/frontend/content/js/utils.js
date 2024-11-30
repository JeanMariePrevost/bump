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
