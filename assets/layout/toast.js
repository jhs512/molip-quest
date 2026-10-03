// A single floating notice near the bottom of the window, replaced on each call.
(function () {
  'use strict';
  if (globalThis.molipToast || typeof document === 'undefined') return;
  let host, timer;
  globalThis.molipToast = function (text, kind) {
    if (!host) {
      host = document.createElement('div');
      host.className = 'molip-toast';
      host.setAttribute('role', 'status');
      host.setAttribute('aria-live', 'polite');
      document.body.append(host);
    }
    host.textContent = text;
    host.dataset.kind = kind || 'info';
    host.classList.add('show');
    clearTimeout(timer);
    timer = setTimeout(() => host.classList.remove('show'), 2600);
  };
})();
