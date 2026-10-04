// Keyboard shortcuts for the whole app.
//
// F11 (macOS: control+command+F) toggles the OS window fullscreen by clicking the hidden
// button the Rust side renders (#app-fullscreen-toggle), whose data-fullscreen attribute
// mirrors the window state. Slides use the same button when they enter presentation mode.
(function () {
  'use strict';
  if (globalThis.molipShortcuts || typeof document === 'undefined') return;
  const toggleButton = () => document.getElementById('app-fullscreen-toggle');
  const toggleFullscreen = () => { const b = toggleButton(); if (b) b.click(); return !!b; };
  const isFullscreen = () => toggleButton()?.dataset.fullscreen === 'true';
  document.addEventListener('keydown', event => {
    const mac = navigator.platform.toLowerCase().includes('mac');
    if (event.key === 'F11' || (mac && event.metaKey && event.ctrlKey && event.key.toLowerCase() === 'f')) {
      event.preventDefault();
      toggleFullscreen();
    }
  });
  globalThis.molipShortcuts = { toggleFullscreen, isFullscreen };
})();
