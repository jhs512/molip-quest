// Keyboard shortcuts for the whole app.
//
// F11 (macOS: control+command+F) toggles the OS window fullscreen by clicking the hidden
// button the Rust side renders (#app-fullscreen-toggle), whose data-fullscreen attribute
// mirrors the window state. Slides use the same button when they enter presentation mode.
//
// Coding missions: Ctrl+Enter (macOS: ⌘Enter) runs the code. Enter pressed right after that
// chord (within RESUBMIT_WINDOW_MS, before any other key) submits, so "run, looks right,
// Enter" is one motion. Ctrl+Shift+Enter (⌘⇧Enter) submits straight away. The listener runs in
// the capture phase so CodeMirror's own Mod-Enter binding never sees the chord.
(function () {
  'use strict';
  if (globalThis.molipShortcuts || typeof document === 'undefined') return;
  const mac = navigator.platform.toLowerCase().includes('mac');
  const toggleButton = () => document.getElementById('app-fullscreen-toggle');
  const toggleFullscreen = () => { const b = toggleButton(); if (b) b.click(); return !!b; };
  const isFullscreen = () => toggleButton()?.dataset.fullscreen === 'true';
  const paneButton = text => [...document.querySelectorAll('.pane-actions button')].find(b => b.textContent.trim() === text && !b.disabled) || null;
  const RESUBMIT_WINDOW_MS = 2000;
  let armedUntil = 0;
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      // /auto-all: the learning view renders a hidden stop button while it runs.
      const stop = document.getElementById('autopilot-stop');
      if (stop) { stop.click(); globalThis.molipToast?.('자동 진행을 해제했습니다', 'info'); }
      return;
    }
    if (event.key === 'F11' || (mac && event.metaKey && event.ctrlKey && event.key.toLowerCase() === 'f')) {
      event.preventDefault();
      toggleFullscreen();
      return;
    }
    if (event.key !== 'Enter') { armedUntil = 0; return; }
    const chord = mac ? event.metaKey : event.ctrlKey;
    if (chord && !event.altKey) {
      const button = paneButton(event.shiftKey ? '제출' : '코드 실행');
      if (!button) return;
      event.preventDefault(); event.stopPropagation();
      button.click();
      if (event.shiftKey) { armedUntil = 0; return; }
      armedUntil = performance.now() + RESUBMIT_WINDOW_MS;
      globalThis.molipToast?.('실행 중 · 지금 Enter를 누르면 제출합니다', 'info');
      return;
    }
    if (!event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey && performance.now() < armedUntil) {
      armedUntil = 0;
      const button = paneButton('제출');
      if (!button) return;
      event.preventDefault(); event.stopPropagation();
      button.click();
      globalThis.molipToast?.('제출했습니다', 'info');
      return;
    }
    armedUntil = 0;
  }, { capture: true });
  globalThis.molipShortcuts = { toggleFullscreen, isFullscreen, runKey: mac ? '⌘Enter' : 'Ctrl+Enter', submitKey: mac ? '⌘⇧Enter' : 'Ctrl+Shift+Enter' };
})();
