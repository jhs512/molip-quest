// Lets the tutor chat act on the screen, and explain while it does.
//
// The assistant may end an answer with a ```molip-actions fence holding a JSON array such as
// [{"action":"set_code","code":"..."},{"action":"submit"}]. The Rust side hands that array to
// window.molipAgent.run, which drives the same buttons and inputs the student uses, waits for
// each run or submission to finish, and returns a text report that goes back to the assistant.
//
// 해설 모드: any action may carry "say". The agent then puts a purple spotlight on the part of the
// screen it is about to touch, shows the sentence in a caption there and reads it aloud (Web
// Speech, Korean voice, the reading speed the 읽어주기 panel saved), and only then acts.
// `say` {target, text} is narration alone; `type_code` {code, say, replace} types code into the
// editor a few characters at a time while the explanation is spoken. The voice comes from
// assets/layout/voice.js (neural clips) with Web Speech as the fallback. molipAgent.stop() ends a
// narration (the sidebar's 멈춤 button), molipAgent.setVoice(false) keeps the captions but mutes.
(function () {
  'use strict';
  if (globalThis.molipAgent || typeof document === 'undefined') return;
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const byText = (selector, text) => [...document.querySelectorAll(selector)].find(b => b.textContent.trim() === text);
  async function waitIdle(button, limit = 180000) {
    const started = Date.now();
    await sleep(200);
    while (button.isConnected && button.disabled && Date.now() - started < limit) await sleep(150);
    await sleep(250);
  }
  const text = (selector, max = 3000) => [...document.querySelectorAll(selector)].map(e => e.textContent.trim()).filter(Boolean).join('\n').slice(0, max);
  function workspaceReport() {
    return [text('.result-pane .execution-status'), text('.result-pane .output')].filter(Boolean).join('\n');
  }
  // The reward card (다음 미션 / 여기 머물기) is left to the student or to /auto-all; its presence
  // is how a pass is recognised. A `next` action takes its 다음 미션 button.
  const popupButton = text => [...document.querySelectorAll('.doctor-panel button')].find(b => b.textContent.trim() === text) || null;
  const cleared = () => !!document.querySelector('.victory-panel');

  // ---- Spotlight: a purple frame over the element being talked about, with the sentence. ----
  const TARGETS = {
    problem: ['.problem-pane h3', '.problem-pane', '.reading-mission'],
    examples: ['.problem-pane details', '.problem-pane .examples', '.problem-pane table', '.problem-pane'],
    editor: ['.cm-editor', '.editor-pane', 'textarea.code-editor'],
    blanks: ['.code-blanks', 'input.code-blank', '.editor-pane'],
    input: ['.result-pane textarea', '.result-pane details', '.result-pane'],
    output: ['.result-pane .output', '.result-pane'],
    run: [() => byText('.pane-actions button', '코드 실행'), '.pane-actions'],
    submit: [() => byText('.pane-actions button', '제출'), '.pane-actions'],
    hint: ['.problem-pane details', '.hint', '.problem-pane'],
    prompt: ['.prompt-buttons', '.problem-pane'],
    quiz: ['.quiz-question', '.reading-mission'],
    quiz_submit: ['.quiz-actions .primary', '.quiz-actions'],
    nav: ['.header-navigation'],
    missions: ['.mission-cell.current', '.mission-cell'],
    slides: ['.slides-host'],
    xp: ['.learning-xp'],
  };
  function resolveTarget(target) {
    if (!target) return null;
    const key = String(target).trim();
    // "quiz:2" is the second question; "option:2:3" its third choice.
    let m = key.match(/^quiz[:\s]+(\d+)$/);
    if (m) return document.querySelectorAll('.quiz-question')[Number(m[1]) - 1] || document.querySelector('.quiz-question');
    m = key.match(/^option[:\s]+(\d+)[:\s]+(\d+)$/);
    if (m) {
      const section = document.querySelectorAll('.quiz-question')[Number(m[1]) - 1];
      return (section && section.querySelectorAll('.quiz-option')[Number(m[2]) - 1]) || section || null;
    }
    const candidates = TARGETS[key];
    if (candidates) {
      for (const candidate of candidates) {
        const element = typeof candidate === 'function' ? candidate() : document.querySelector(candidate);
        if (element) return element;
      }
      return null;
    }
    try { return document.querySelector(key); } catch { return null; }
  }
  let spot, caption, spotTarget = null, raf = 0;
  function ensureSpot() {
    if (spot) return;
    spot = document.createElement('div'); spot.className = 'agent-spotlight'; spot.hidden = true; spot.setAttribute('aria-hidden', 'true');
    caption = document.createElement('div'); caption.className = 'agent-caption'; caption.hidden = true; caption.setAttribute('role', 'status'); caption.setAttribute('aria-live', 'polite');
    document.body.append(spot, caption);
  }
  function place() {
    const margin = 8;
    if (spotTarget && spotTarget.isConnected) {
      const r = spotTarget.getBoundingClientRect();
      const pad = 6;
      spot.style.left = `${r.left - pad}px`; spot.style.top = `${r.top - pad}px`;
      spot.style.width = `${r.width + pad * 2}px`; spot.style.height = `${r.height + pad * 2}px`;
      spot.hidden = false;
      if (!caption.hidden) {
        const w = caption.offsetWidth, h = caption.offsetHeight;
        let left = r.left + r.width / 2 - w / 2;
        left = Math.max(margin, Math.min(left, innerWidth - margin - w));
        let top = r.bottom + pad + 12;
        if (top + h > innerHeight - margin) top = r.top - pad - 12 - h;
        if (top < margin) top = Math.min(innerHeight - margin - h, r.top + 12);
        caption.style.left = `${left}px`; caption.style.top = `${top}px`;
      }
    } else {
      spot.hidden = true;
      if (!caption.hidden) {
        caption.style.left = `${Math.max(margin, innerWidth / 2 - caption.offsetWidth / 2)}px`;
        caption.style.top = `${innerHeight - margin - caption.offsetHeight - 24}px`;
      }
    }
    raf = requestAnimationFrame(place);
  }
  function spotlight(target, sentence) {
    ensureSpot();
    const element = resolveTarget(target);
    spotTarget = element || null;
    if (element) {
      try { element.scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: 'smooth' }); } catch {}
    }
    caption.textContent = sentence || '';
    caption.hidden = !sentence;
    cancelAnimationFrame(raf);
    place();
  }
  function clearSpot() {
    cancelAnimationFrame(raf); raf = 0;
    spotTarget = null;
    if (spot) { spot.hidden = true; caption.hidden = true; }
  }

  // ---- Voice: one sentence at a time, resolved when it has been read (or would have been). ----
  let voice = true, cancelled = false;
  // ---- Neural voice: clips come from assets/layout/voice.js (the app's /tts endpoint). ----
  let currentAudio = null;
  const neural = () => (globalThis.molipVoice && globalThis.molipVoice.enabled()) ? globalThis.molipVoice : null;
  function synthesize(sentence) { const v = neural(); return v ? v.synthesize(sentence) : Promise.resolve(null); }
  function playClip(url) {
    return new Promise(resolve => {
      const audio = new Audio(url);
      audio.playbackRate = globalThis.molipVoice ? globalThis.molipVoice.rate : 1;
      let done = false;
      const finish = ok => { if (done) return; done = true; if (currentAudio === audio) currentAudio = null; resolve(ok); };
      audio.onended = () => finish(true);
      audio.onerror = () => finish(false);
      currentAudio = audio;
      audio.play().then(() => { if (cancelled) { audio.pause(); finish(true); } }).catch(() => finish(false));
    });
  }
  function stopClip() { if (currentAudio) { try { currentAudio.pause(); } catch {} currentAudio = null; } }
  window.addEventListener('molip:tts-rate', event => { if (currentAudio) currentAudio.playbackRate = event.detail; });
  function prefetch(actions) {
    if (!voice || !neural()) return;
    for (const action of actions) {
      const sentence = action && (action.action === 'say' ? action.text : action.say);
      if (sentence) synthesize(String(sentence));
    }
  }
  // Chromium drops onend for an utterance that gets garbage-collected, and ignores speak() in the
  // same tick as cancel(): keep the utterance referenced, and only cancel when something plays.
  let current = null;
  async function speak(sentence) {
    if (!sentence) return;
    if (voice && neural() && !cancelled) {
      const url = await synthesize(String(sentence));
      if (cancelled) return;
      if (url && await playClip(url)) { lastSpeech = 'neural'; return; }
    }
    lastSpeech = 'system';
    return speakWithSystemVoice(sentence);
  }
  let lastSpeech = '';
  function speakWithSystemVoice(sentence) {
    const length = String(sentence).length;
    if (!voice || !('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) {
      return sleep(Math.min(5000, 700 + length * 55)); // reading time, so the caption can be read
    }
    return new Promise(resolve => {
      const helpers = globalThis.molipSpeech;
      const synth = window.speechSynthesis;
      let done = false, timer = 0;
      const finish = () => { if (done) return; done = true; clearTimeout(timer); current = null; resolve(); };
      const start = () => {
        if (cancelled || !voice) { finish(); return; }
        const utterance = new SpeechSynthesisUtterance(helpers && helpers.pronunciationText ? helpers.pronunciationText(sentence) : sentence);
        utterance.lang = 'ko-KR';
        const korean = helpers && helpers.koreanVoice ? helpers.koreanVoice(synth.getVoices()) : null;
        if (korean) utterance.voice = korean;
        let rate = 1;
        try { const saved = Number(localStorage.getItem('molip:tts-rate')); if (saved >= 0.5 && saved <= 2) rate = saved; } catch {}
        utterance.rate = rate;
        timer = setTimeout(finish, 3000 + length * 170 / rate);
        utterance.onend = finish; utterance.onerror = finish;
        current = utterance;
        try { synth.resume(); synth.speak(utterance); } catch { finish(); }
      };
      if (synth.speaking || synth.pending) { synth.cancel(); setTimeout(start, 150); } else start();
    });
  }
  function stopSpeech() { current = null; stopClip(); if ('speechSynthesis' in window) try { window.speechSynthesis.cancel(); } catch {} }

  async function typeCode(code, replace) {
    const api = window.molipCodeEditors;
    if (!api || !api.appendValue || !api.getValue) throw new Error('코드 편집기를 찾지 못했습니다');
    if (replace && !api.setValue('')) throw new Error('이 미션에는 코드 편집기가 없습니다 (코딩 미션에서만 됩니다)');
    const current = api.getValue();
    if (current === null) throw new Error('이 미션에는 코드 편집기가 없습니다 (코딩 미션에서만 됩니다)');
    let body = String(code ?? '');
    if (!body.endsWith('\n')) body += '\n';
    if (current && !current.endsWith('\n')) body = '\n' + body;
    for (let i = 0; i < body.length && !cancelled; i += 2) {
      api.appendValue(body.slice(i, i + 2));
      await sleep(18);
    }
    return body.split('\n').filter(line => line.trim()).length;
  }

  const handlers = {
    async say(a) {
      // The spotlight and speech were started by run(); nothing else to do.
      return '설명: ' + String(a.text || '').slice(0, 80);
    },
    async type_code(a) {
      spotlight('editor', a.say);
      const spoken = speak(a.say);
      const lines = await typeCode(a.code, !!a.replace);
      await spoken;
      await sleep(250);
      return `코드 ${lines}줄을 입력했습니다.`;
    },
    async set_code(a) {
      const api = window.molipCodeEditors;
      if (!api || !api.setValue) throw new Error('코드 편집기를 찾지 못했습니다');
      if (!api.setValue(String(a.code ?? ''))) throw new Error('이 미션에는 코드 편집기가 없습니다 (코딩 미션에서만 됩니다)');
      await sleep(300);
      return '코드를 편집기에 넣었습니다.';
    },
    async fill_blanks(a) {
      const inputs = [...document.querySelectorAll('input.code-blank')];
      if (!inputs.length) throw new Error('채울 빈칸이 없습니다');
      const values = Array.isArray(a.values) ? a.values : [];
      values.forEach((value, i) => {
        if (!inputs[i]) return;
        inputs[i].value = String(value);
        inputs[i].dispatchEvent(new Event('input', { bubbles: true }));
      });
      await sleep(300);
      return `빈칸 ${Math.min(inputs.length, values.length)}개를 채웠습니다.`;
    },
    async run() {
      const button = byText('.pane-actions button', '코드 실행');
      if (!button) throw new Error('코드 실행 버튼이 없습니다 (코딩 미션에서만 됩니다)');
      button.click();
      await waitIdle(button);
      return '실행 결과:\n' + (workspaceReport() || '(출력 없음)');
    },
    async submit() {
      const button = byText('.pane-actions button', '제출');
      if (!button) throw new Error('제출 버튼이 없습니다 (코딩 미션에서만 됩니다)');
      button.click();
      await waitIdle(button);
      await sleep(400);
      const passed = cleared();
      return (passed ? '제출 결과: 통과. 미션 클리어로 기록됐습니다 (정답 카드가 떠 있습니다).\n' : '제출 결과:\n') + (workspaceReport() || '(출력 없음)');
    },
    async answer_quiz(a) {
      const sections = [...document.querySelectorAll('.quiz-question')];
      if (!sections.length) throw new Error('이 미션에는 퀴즈나 확인 문항이 없습니다');
      const answers = a.answers && typeof a.answers === 'object' ? a.answers : {};
      const notes = [];
      for (const [key, value] of Object.entries(answers)) {
        const section = sections[Number(key) - 1];
        if (!section) { notes.push(`${key}번 문항이 없습니다`); continue; }
        const want = String(value).trim();
        const radios = [...section.querySelectorAll('input[type=radio]')];
        if (radios.length) {
          let pick = radios.find(r => r.value.trim() === want)
            || radios.find(r => r.value.trim().includes(want) || want.includes(r.value.trim()));
          if (!pick && /^\d+$/.test(want)) pick = radios[Number(want) - 1];
          if (!pick) { notes.push(`${key}번: 보기 "${want}"를 찾지 못했습니다. 보기: ${radios.map(r => r.value).join(' | ')}`); continue; }
          if (a.say) { spotlight(pick.closest('.quiz-option') ? `option:${key}:${radios.indexOf(pick) + 1}` : `quiz:${key}`, a.say); }
          pick.click();
        } else {
          const input = section.querySelector('input:not([type=radio]):not([type=checkbox])');
          if (!input) { notes.push(`${key}번: 입력칸이 없습니다`); continue; }
          input.value = want;
          input.dispatchEvent(new Event('input', { bubbles: true }));
        }
        if (a.say) await sleep(500);
      }
      await sleep(300);
      const button = document.querySelector('.quiz-actions .primary');
      if (button && !button.disabled) { if (a.say) spotlight('quiz_submit', a.say); button.click(); await waitIdle(button); }
      await sleep(300);
      const status = text('.quiz-actions ~ .execution-status, .concept-flow .execution-status, .execution-status', 600) + (cleared() ? ' · 미션 클리어 (정답 카드가 떠 있습니다)' : '');
      const banner = text('.clear-banner', 200);
      return ['채점 결과: ' + (status || '(상태 없음)'), banner, ...notes].filter(Boolean).join('\n');
    },
    async next() { const popup = popupButton('다음 미션 ›'); const b = popup || byText('.header-navigation button', '다음 →'); if (!b || b.disabled) throw new Error('다음 미션으로 갈 수 없습니다'); b.click(); await sleep(600); return '다음 미션으로 이동했습니다: ' + text('.reading-mission h2, .problem-pane h2, .slides-mission h2', 120); },
    async prev() { const b = byText('.header-navigation button', '← 이전'); if (!b || b.disabled) throw new Error('이전 미션으로 갈 수 없습니다'); b.click(); await sleep(600); return '이전 미션으로 이동했습니다: ' + text('.reading-mission h2, .problem-pane h2, .slides-mission h2', 120); },
    async goto(a) { const cells = document.querySelectorAll('.mission-cell'); const cell = cells[Number(a.mission) - 1]; if (!cell) throw new Error(`이 단원에는 ${a.mission}번 미션이 없습니다 (미션 ${cells.length}개)`); cell.click(); await sleep(600); return `${a.mission}번 미션으로 이동했습니다: ` + text('.reading-mission h2, .problem-pane h2, .slides-mission h2', 120); },
    async next_slide() { const b = byText('.slides-bar button', '다음 장 →'); if (!b || b.disabled) throw new Error('넘길 장이 없습니다'); b.click(); await sleep(300); return '다음 장으로 넘겼습니다: ' + text('.slides-counter', 20); },
    async finish_slides() { const b = byText('button', '다 봤어요 · 미션 완료'); if (!b) throw new Error('슬라이드 미션이 아닙니다'); if (!b.disabled) b.click(); await sleep(400); return '슬라이드 미션을 완료로 표시했습니다.'; },
  };
  // Where each action's spotlight goes when it carries "say" (type_code places its own).
  const DEFAULT_TARGET = {
    say: a => a.target || null, set_code: () => 'editor', fill_blanks: () => 'blanks', run: () => 'run', submit: () => 'submit',
    answer_quiz: () => 'quiz', next: () => 'nav', prev: () => 'nav', goto: () => 'missions', next_slide: () => 'slides', finish_slides: () => 'slides',
  };
  async function run(actions) {
    if (!Array.isArray(actions)) return '동작 목록이 배열이 아닙니다.';
    cancelled = false;
    prefetch(actions);
    const lines = [];
    try {
      for (const [i, action] of actions.entries()) {
        if (cancelled) { lines.push(`${i + 1}. 학생이 멈춤을 눌러 여기서 중단했습니다.`); break; }
        const name = action && action.action;
        const handler = handlers[name];
        if (!handler) { lines.push(`${i + 1}. ${name}: 모르는 동작입니다 (가능: ${Object.keys(handlers).join(', ')})`); continue; }
        try {
          const sentence = name === 'say' ? action.text : action.say;
          if (sentence && name !== 'type_code' && name !== 'answer_quiz') {
            spotlight(DEFAULT_TARGET[name] ? DEFAULT_TARGET[name](action) : null, sentence);
            await speak(sentence);
            if (cancelled) { lines.push(`${i + 1}. 학생이 멈춤을 눌러 여기서 중단했습니다.`); break; }
          } else if (sentence && name === 'answer_quiz') {
            spotlight('quiz', sentence);
            await speak(sentence);
          }
          lines.push(`${i + 1}. ${name}: ${await handler(action)}`);
          if (sentence) await sleep(350);
        } catch (error) {
          lines.push(`${i + 1}. ${name}: 오류 - ${error && error.message ? error.message : error}`);
          break;
        }
      }
    } finally {
      stopSpeech();
      clearSpot();
    }
    return lines.join('\n');
  }
  function stop() { cancelled = true; stopSpeech(); clearSpot(); }
  function setVoice(on) { voice = !!on; if (!voice) stopSpeech(); return voice; }
  function setVoiceName(name) { return globalThis.molipVoice ? globalThis.molipVoice.setName(name) : String(name || 'system'); }
  globalThis.molipAgent = { run, stop, setVoice, setVoiceName, get voice() { return voice; }, get voiceName() { return globalThis.molipVoice ? globalThis.molipVoice.name : 'system'; }, get lastSpeech() { return lastSpeech; }, get playbackRate() { return currentAudio ? currentAudio.playbackRate : null; }, actions: Object.keys(handlers) };
})();
