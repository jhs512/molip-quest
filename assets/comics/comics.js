// Draw comic-gen code fences from course Markdown as inline comic strips.
//
// The Markdown renderer leaves ```comic-gen fences as `pre > code.language-comic-gen`.
// This loader imports the vendored Comic Gen SDK (an ES module, so it is loaded
// from a Blob URL built from `window.__molipComicGenSource`), renders each fence
// to one SVG with every panel, and replaces the fence with a <figure>. Missions
// re-render on navigation, so a MutationObserver draws fences as they appear.
(function () {
  'use strict';
  if (globalThis.molipComics) return;
  const source = globalThis.__molipComicGenSource;
  delete globalThis.__molipComicGenSource;
  if (typeof document === 'undefined' || !source) return;
  const url = URL.createObjectURL(new Blob([source], { type: 'text/javascript' }));
  const sdk = import(url).catch(error => { console.error('comic-gen SDK failed to load', error); return null; });
  const seen = new WeakSet();
  let count = 0;

  async function render(root) {
    if (!(root instanceof Element) && root !== document) return;
    const codes = [...root.querySelectorAll('pre > code.language-comic-gen')];
    if (root instanceof Element && root.matches('pre > code.language-comic-gen')) codes.push(root);
    if (!codes.length) return;
    const api = await sdk;
    for (const code of codes) {
      const pre = code.parentElement;
      if (!pre || !pre.isConnected || seen.has(pre)) continue;
      seen.add(pre);
      const figure = document.createElement('figure');
      figure.className = 'comic-strip';
      figure.setAttribute('aria-label', '설명 만화');
      try {
        if (!api) throw new Error('SDK unavailable');
        const result = api.renderComic(code.textContent, { 너비: 720 });
        if (result.diagnostics.length) throw new Error(result.diagnostics.join(' / '));
        figure.innerHTML = result.svg;
        const svg = figure.querySelector('svg');
        if (svg) { svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', '설명 만화 ' + ((result.panels && result.panels.length) || 1) + '컷'); }
        count += 1;
      } catch (error) {
        figure.classList.add('comic-error');
        figure.textContent = '만화를 그리지 못했습니다: ' + (error && error.message ? error.message : error);
      }
      pre.replaceWith(figure);
    }
  }
  const observer = new MutationObserver(records => {
    for (const record of records) for (const node of record.addedNodes) if (node instanceof Element) render(node);
  });
  const start = () => { observer.observe(document.body, { childList: true, subtree: true }); render(document); };
  if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
  globalThis.molipComics = { render, get count() { return count; }, ready: sdk.then(api => !!api) };
})();
