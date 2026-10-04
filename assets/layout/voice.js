// The app's neural voice, shared by 읽어주기 (speech.js) and 해설 모드 (agent.js).
//
// A sentence becomes an MP3 through the app's own `molip` protocol (POST /tts, see src/tts.rs:
// the Edge Read Aloud voices 선히/인준/현수, fetched by the app itself and cached on disk). This
// module keeps an in-page cache of object URLs per (voice, sentence) so the same line is never
// fetched twice, and lets callers prefetch the next sentence while one plays. `name` is the
// voice id from the assistant settings; "system" means the device's own Web Speech voice.
(function () {
  'use strict';
  if (globalThis.molipVoice || typeof document === 'undefined') return;
  let name = 'ko-KR-SunHiNeural';
  const clips = new Map();
  const stats = { fetched: 0, cached: 0, failed: 0, lastEngine: '' };
  function url() {
    // wry serves custom protocols as http://<name>.localhost on Windows (the page itself is on
    // http://dioxus.index.html there), and as <name>://localhost on macOS and Linux.
    return location.protocol === 'http:' || location.protocol === 'https:'
      ? `${location.protocol}//molip.localhost/tts` : 'molip://localhost/tts';
  }
  const enabled = () => name !== 'system' && typeof fetch === 'function';
  // Resolves to an object URL for the clip, or null when the voice is off or unreachable.
  function synthesize(sentence) {
    const text = String(sentence || '').trim();
    if (!enabled() || !text) return Promise.resolve(null);
    const key = name + '\n' + text;
    let pending = clips.get(key);
    if (pending) { stats.cached += 1; return pending; }
    pending = fetch(url(), { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: JSON.stringify({ text, voice: name }) })
      .then(async response => {
        if (!response.ok) { stats.failed += 1; console.warn('tts', response.status, await response.text().catch(() => '')); clips.delete(key); return null; }
        stats.fetched += 1; stats.lastEngine = response.headers.get('X-Molip-Engine') || '';
        return URL.createObjectURL(await response.blob());
      })
      .catch(error => { stats.failed += 1; clips.delete(key); console.warn('tts', error); return null; });
    clips.set(key, pending);
    return pending;
  }
  function setName(value) { name = String(value || 'system'); return name; }
  globalThis.molipVoice = { synthesize, setName, enabled, get name() { return name; }, stats };
})();
