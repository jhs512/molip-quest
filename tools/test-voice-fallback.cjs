// Exercise the actual browser voice/player scripts with an explicitly blocked TTS endpoint.
// Run: node tools/test-voice-fallback.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

async function verify(systemVoice) {
  let requests = 0, spoken = 0, warnings = 0;
  const events = new EventTarget();
  const context = {
    document: { querySelectorAll: () => [] },
    location: { protocol: 'http:' },
    addEventListener: events.addEventListener.bind(events),
    dispatchEvent: events.dispatchEvent.bind(events),
    CustomEvent, AbortController,
    console: { warn() {} },
    localStorage: { getItem: () => null },
    setTimeout: (fn, ms) => ms >= 10000 ? setTimeout(fn, ms) : setTimeout(fn, 0),
    clearTimeout,
    fetch: async () => {
      requests += 1;
      return { ok: false, status: 403, text: async () => '403 Forbidden' };
    },
    molipToast: () => { warnings += 1; },
  };
  if (systemVoice) {
    context.SpeechSynthesisUtterance = class { constructor(text) { this.text = text; } };
    context.speechSynthesis = {
      getVoices: () => [{ lang: 'ko-KR' }],
      cancel() {}, resume() {},
      speak(utterance) { spoken += 1; queueMicrotask(() => utterance.onend()); },
    };
    context.molipSpeech = { koreanVoice: voices => voices[0] };
  }
  context.window = context;
  vm.createContext(context);
  for (const filename of ['voice.js', 'agent.js']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname, '../assets/layout', filename), 'utf8'), context);
  }
  assert.equal(await context.molipAgent.speakReply('한국어 안내예요.', true), true);
  assert.equal(await context.molipAgent.speakReply('다음 설명도 이어가요.', true), true);
  assert.equal(requests, 1, 'A blocked service must not delay every following sentence');
  assert.equal(warnings, 1, 'The fallback is announced once per session');
  assert.equal(context.molipVoice.enabled(), false);
  assert.equal(spoken, systemVoice ? 2 : 0);
}

(async () => {
  await verify(true);
  await verify(false);
  console.log('403 fallback: Korean system voice and no-voice completion both pass');
})().catch(error => { console.error(error); process.exitCode = 1; });
