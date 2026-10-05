// Draw ```mapping fences from course Markdown as "one input → one output" pictures.
//
//   ```mapping
//   제목: map(int, ['10000', '3'])
//   함수: int
//   '10000' → 10000
//   '3' → 3
//   ```
//
// Each line with an arrow becomes a row: the left box is the value going in, the arrow
// carries the function name, the right box is the value coming out. The footer states
// that N inputs give N outputs, which is the point of map.
//
// `종류: 비교` draws the same rows side by side with no arrow and no footer: two things
// compared line by line (리스트 vs 딕셔너리), not one turning into the other.
(function () {
  'use strict';
  if (globalThis.molipDiagrams || typeof document === 'undefined') return;
  const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function parse(text) {
    const spec = { title: '', fn: '', left: '들어가는 값', right: '나오는 값', rows: [], compare: false };
    for (const raw of text.split('\n')) {
      const line = raw.trim();
      if (!line) continue;
      if (line.startsWith('제목:')) spec.title = line.slice(3).trim();
      else if (line.startsWith('종류:')) spec.compare = line.slice(3).trim() === '비교';
      else if (line.startsWith('함수:')) spec.fn = line.slice(3).trim();
      else if (line.startsWith('왼쪽:')) spec.left = line.slice(3).trim();
      else if (line.startsWith('오른쪽:')) spec.right = line.slice(4).trim();
      else {
        const parts = line.split(/\s*(?:→|->)\s*/);
        if (parts.length === 2) spec.rows.push(parts);
      }
    }
    return spec;
  }

  function svg(spec) {
    const compare = spec.compare;
    const W = 720, rowH = 48, boxH = 34;
    const lx = compare ? 40 : 60, lw = compare ? 300 : 210, rx = compare ? 380 : 450, rw = compare ? 300 : 210;
    const top = (spec.title ? 46 : 12) + 28;
    const H = top + spec.rows.length * rowH + (compare ? 8 : 44);
    const mono = 'Consolas, "Malgun Gothic", monospace';
    let s = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(spec.title || '대응 그림')}">`;
    s += '<defs><marker id="mapping-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#9fe3c6"/></marker></defs>';
    if (spec.title) s += `<text x="${W / 2}" y="28" text-anchor="middle" font-family="${mono}" font-size="17" font-weight="700" fill="#a9d9ff">${esc(spec.title)}</text>`;
    const headY = top - 10;
    s += `<text x="${lx + lw / 2}" y="${headY}" text-anchor="middle" font-size="13" fill="#9ab0c2">${esc(spec.left)}</text>`;
    s += `<text x="${rx + rw / 2}" y="${headY}" text-anchor="middle" font-size="13" fill="#9ab0c2">${esc(spec.right)}</text>`;
    spec.rows.forEach(([a, b], i) => {
      const y = top + i * rowH, mid = y + boxH / 2;
      s += `<rect x="${lx}" y="${y}" width="${lw}" height="${boxH}" rx="8" fill="#12212f" stroke="#405970"/>`;
      s += `<text x="${lx + lw / 2}" y="${mid + 6}" text-anchor="middle" font-family="${mono}" font-size="16" fill="${compare ? '#a9d9ff' : '#f7cc91'}">${esc(a)}</text>`;
      if (compare) {
        s += `<text x="${(lx + lw + rx) / 2}" y="${mid + 5}" text-anchor="middle" font-size="13" fill="#6f8799">vs</text>`;
      } else {
        s += `<line x1="${lx + lw + 14}" y1="${mid}" x2="${rx - 14}" y2="${mid}" stroke="#9fe3c6" stroke-width="2" marker-end="url(#mapping-arrow)"/>`;
        if (spec.fn) s += `<text x="${(lx + lw + rx) / 2}" y="${mid - 7}" text-anchor="middle" font-family="${mono}" font-size="13" fill="#9fe3c6">${esc(spec.fn)}</text>`;
      }
      s += `<rect x="${rx}" y="${y}" width="${rw}" height="${boxH}" rx="8" fill="#12212f" stroke="#405970"/>`;
      s += `<text x="${rx + rw / 2}" y="${mid + 6}" text-anchor="middle" font-family="${mono}" font-size="16" fill="${compare ? '#f7cc91' : '#a6efd1'}">${esc(b)}</text>`;
    });
    const n = spec.rows.length;
    if (!compare) s += `<text x="${W / 2}" y="${H - 14}" text-anchor="middle" font-size="14" fill="#dce7f1">값 ${n}개가 들어가면 결과도 ${n}개 · 한 줄씩 짝지어 바뀝니다</text>`;
    return s + '</svg>';
  }

  const seen = new WeakSet();
  function render(root) {
    if (!(root instanceof Element) && root !== document) return;
    const codes = [...root.querySelectorAll('pre > code.language-mapping')];
    if (root instanceof Element && root.matches('pre > code.language-mapping')) codes.push(root);
    for (const code of codes) {
      const pre = code.parentElement;
      if (!pre || !pre.isConnected || seen.has(pre)) continue;
      seen.add(pre);
      const spec = parse(code.textContent);
      if (!spec.rows.length) continue;
      const figure = document.createElement('figure');
      figure.className = 'diagram-strip';
      figure.innerHTML = svg(spec);
      pre.replaceWith(figure);
    }
  }
  new MutationObserver(records => {
    for (const record of records) for (const node of record.addedNodes) if (node instanceof Element) render(node);
  }).observe(document.body, { childList: true, subtree: true });
  render(document);
  globalThis.molipDiagrams = { render, parse, svg };
})();
