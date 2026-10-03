// Marp slide decks inside the app.
//
// A slides mission renders its Markdown through Marp Core (bundled here, offline) into
// scaled SVG slides and shows one at a time with ←/→, a counter and a fullscreen
// button, so the instructor can project a deck from the same screen students use.
// comic-gen, mapping and interactive fences inside slides are picked up by the other
// loaders because the rendered DOM contains ordinary <pre><code> blocks.
import { Marp } from '@marp-team/marp-core';

const marp = new Marp({ html: false, inlineSVG: true, minifyCSS: false });
// A friendly default theme: Pretendard, dark text on a warm paper, accent for headings.
marp.themeSet.add(`/* @theme molip */
section { width: 1280px; height: 720px; padding: 64px 80px; font-family: 'Pretendard', 'Malgun Gothic', sans-serif; font-size: 30px; line-height: 1.6; color: #1d2b3a; background: #fbf8f1; }
section h1 { font-size: 60px; line-height: 1.25; margin: 0 0 24px; color: #0f3d5e; letter-spacing: -1px; }
section h2 { font-size: 44px; margin: 0 0 20px; color: #0f3d5e; letter-spacing: -0.5px; }
section h3 { font-size: 34px; margin: 0 0 12px; color: #236b55; }
section p, section li { margin: 0 0 10px; }
section ul, section ol { padding-left: 1.2em; }
section strong { color: #b2461d; }
section code { font-family: 'JetBrains Mono', 'Pretendard', monospace; font-size: 0.85em; background: #eee8da; padding: 2px 8px; border-radius: 6px; }
section pre { background: #16283a; color: #e4eef7; padding: 20px 24px; border-radius: 12px; font-size: 24px; line-height: 1.5; }
section pre code { background: none; color: inherit; padding: 0; font-size: inherit; }
section blockquote { border-left: 6px solid #e0a63a; margin: 12px 0; padding: 6px 24px; color: #4a5a6a; font-size: 28px; }
section table { font-size: 24px; border-collapse: collapse; } section th, section td { border: 1px solid #cfc7b5; padding: 8px 14px; } section th { background: #eee8da; }
section footer, section header { color: #8a93a0; font-size: 18px; }
section.lead { display: flex; flex-direction: column; justify-content: center; text-align: center; background: #0f3d5e; color: #f4f8fb; }
section.lead h1, section.lead h2 { color: #ffffff; } section.lead strong { color: #ffd37a; }
section.lead p { font-size: 34px; color: #d6e4f0; }
section .comic-strip svg { max-height: 520px; width: auto; margin: 0 auto; }
section figure { margin: 8px 0; }
section .columns { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
`);

export function renderDeck(markdown) {
  const { html, css } = marp.render(markdown);
  return { html, css };
}

const seen = new WeakSet();
function mount(host) {
  if (seen.has(host)) return;
  seen.add(host);
  const source = host.dataset.marpSource || '';
  let rendered;
  try { rendered = renderDeck(source); } catch (error) { host.textContent = '슬라이드를 그리지 못했습니다: ' + error.message; return; }
  const style = document.createElement('style'); style.textContent = rendered.css;
  const stage = document.createElement('div'); stage.className = 'slides-stage'; stage.innerHTML = rendered.html;
  const slides = [...stage.querySelectorAll(':scope > .marpit > svg, :scope > .marpit > section')];
  if ('marpAll' in host.dataset) {
    // Overview mode (PPT 모아보기): every slide visible in a grid, a click shows one fullscreen.
    slides.forEach(s => { s.onclick = () => s.requestFullscreen?.(); });
    host.replaceChildren(style, stage);
    globalThis.molipSlides.count += 1;
    return;
  }
  const bar = document.createElement('div'); bar.className = 'slides-bar';
  const prev = document.createElement('button'); prev.type = 'button'; prev.textContent = '← 이전 장';
  const counter = document.createElement('span'); counter.className = 'slides-counter';
  const next = document.createElement('button'); next.type = 'button'; next.textContent = '다음 장 →';
  const full = document.createElement('button'); full.type = 'button'; full.textContent = '전체 화면'; full.className = 'slides-full';
  bar.append(prev, counter, next, full);
  host.replaceChildren(style, stage, bar);
  let index = 0;
  const update = () => {
    slides.forEach((s, i) => { s.style.display = i === index ? '' : 'none'; });
    counter.textContent = `${index + 1} / ${slides.length}`;
    prev.disabled = index === 0; next.disabled = index === slides.length - 1;
    host.dataset.slideIndex = String(index);
    // Reaching the last slide completes the mission: the Rust side listens on a hidden button.
    if (index === slides.length - 1) host.closest('.slides-mission')?.querySelector('.slides-finish')?.click();
  };
  prev.onclick = () => { if (index > 0) { index--; update(); } };
  next.onclick = () => { if (index < slides.length - 1) { index++; update(); } };
  full.onclick = () => { if (document.fullscreenElement) document.exitFullscreen(); else host.requestFullscreen?.(); };
  host.tabIndex = 0;
  host.addEventListener('keydown', event => {
    if (event.key === 'ArrowRight' || event.key === 'PageDown' || event.key === ' ') { event.preventDefault(); next.click(); }
    if (event.key === 'ArrowLeft' || event.key === 'PageUp') { event.preventDefault(); prev.click(); }
  });
  update();
  globalThis.molipSlides.count += 1;
}
function render(root) {
  if (!(root instanceof Element) && root !== document) return;
  const hosts = [...root.querySelectorAll('[data-marp-source]')];
  if (root instanceof Element && root.matches('[data-marp-source]')) hosts.push(root);
  hosts.forEach(mount);
}
globalThis.molipSlides = { render, renderDeck, count: 0 };
new MutationObserver(records => { for (const r of records) for (const n of r.addedNodes) if (n instanceof Element) render(n); }).observe(document.body, { childList: true, subtree: true });
render(document);
