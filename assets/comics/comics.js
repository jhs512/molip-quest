// Draw comic-gen code fences from course Markdown as inline comic strips.
//
// The Markdown renderer leaves ```comic-gen fences as `pre > code.language-comic-gen`.
// This loader imports the vendored Comic Gen SDK (an ES module, so it is loaded
// from a Blob URL built from `window.__molipComicGenSource`), renders each fence
// to an SVG, and replaces the fence with a <figure>. Slides select one resolved
// panel via a molip-panel marker, sharing the rendered script across slides. Missions
// re-render on navigation, so a MutationObserver draws fences as they appear.
(function () {
  'use strict';
  if (globalThis.molipComics) return;
  const source = globalThis.__molipComicGenSource;
  delete globalThis.__molipComicGenSource;
  if (typeof document === 'undefined' || !source) return;
  // Mermaid diagrams inside panels: the SDK would fetch its loader and Mermaid from a CDN,
  // so the vendored Mermaid build is served from a Blob URL through a tiny loader of our own
  // that fulfils the same ready/error events. Comics then render fully offline.
  const mermaidSource = globalThis.__molipMermaidSource;
  delete globalThis.__molipMermaidSource;
  let sdkSource = source;
  if (mermaidSource) {
    const mermaidUrl = URL.createObjectURL(new Blob([mermaidSource], { type: 'text/javascript' }));
    const loader = "const s=document.createElement('script');s.src=" + JSON.stringify(mermaidUrl)
      + ";s.onload=()=>{const e=globalThis.mermaid;if(e&&typeof e.initialize==='function'&&typeof e.render==='function'){Object.defineProperty(window,'__comicGenMermaid',{value:e});window.dispatchEvent(new Event('comic-gen-mermaid-ready'));}else{window.dispatchEvent(new Event('comic-gen-mermaid-error'));}};"
      + "s.onerror=()=>window.dispatchEvent(new Event('comic-gen-mermaid-error'));document.head.append(s);";
    const loaderUrl = URL.createObjectURL(new Blob([loader], { type: 'text/javascript' }));
    sdkSource = sdkSource.replace('"https://cdn.jsdelivr.net/gh/jhs512/comic-gen@v0.6.0/cdn/comic-gen.mermaid.js"', JSON.stringify(loaderUrl));
  }
  const url = URL.createObjectURL(new Blob([sdkSource], { type: 'text/javascript' }));
  const sdk = import(url).catch(error => { console.error('comic-gen SDK failed to load', error); return null; });
  const seen = new WeakSet();
  let count = 0;
  const slideRenders = new Map();

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
        const panelMarker = code.textContent.match(/^# molip-panel:(\d+)\n/);
        const script = code.textContent.replace(/^# molip-panel:\d+\n/, '');
        let pending = panelMarker && slideRenders.get(script);
        if (!pending) {
          pending = api.renderComicAsync(script, { 너비: 720 });
          if (panelMarker) slideRenders.set(script, pending);
        }
        const result = await pending;
        if (result.diagnostics.length) throw new Error(result.diagnostics.join(' / '));
        const panel = panelMarker && result.panels[Number(panelMarker[1])];
        figure.innerHTML = panel ? panel.svg : result.svg;
        const svg = figure.querySelector('svg');
        if (svg) { svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', panel ? `설명 만화 ${Number(panelMarker[1]) + 1} / ${result.panels.length}컷` : '설명 만화 ' + ((result.panels && result.panels.length) || 1) + '컷'); }
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
