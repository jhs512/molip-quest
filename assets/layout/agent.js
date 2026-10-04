// Lets the tutor chat act on the screen.
//
// The assistant may end an answer with a ```molip-actions fence holding a JSON array such as
// [{"action":"set_code","code":"..."},{"action":"submit"}]. The Rust side hands that array to
// window.molipAgent.run, which drives the same buttons and inputs the student uses, waits for
// each run or submission to finish, and returns a text report that goes back to the assistant.
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
  function dismissClearPopup() {
    const ok = [...document.querySelectorAll('.doctor-panel button')].find(b => b.textContent.trim() === '확인');
    if (!ok) return false;
    ok.click();
    return true;
  }
  const handlers = {
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
      const passed = dismissClearPopup();
      return (passed ? '제출 결과: 통과. 미션 클리어로 기록됐습니다.\n' : '제출 결과:\n') + (workspaceReport() || '(출력 없음)');
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
          pick.click();
        } else {
          const input = section.querySelector('input:not([type=radio]):not([type=checkbox])');
          if (!input) { notes.push(`${key}번: 입력칸이 없습니다`); continue; }
          input.value = want;
          input.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }
      await sleep(300);
      const button = document.querySelector('.quiz-actions .primary');
      if (button && !button.disabled) { button.click(); await waitIdle(button); }
      await sleep(300);
      dismissClearPopup();
      const status = text('.quiz-actions ~ .execution-status, .concept-flow .execution-status, .execution-status', 600);
      const banner = text('.clear-banner', 200);
      return ['채점 결과: ' + (status || '(상태 없음)'), banner, ...notes].filter(Boolean).join('\n');
    },
    async next() { const b = byText('.header-navigation button', '다음 →'); if (!b || b.disabled) throw new Error('다음 미션으로 갈 수 없습니다'); b.click(); await sleep(600); return '다음 미션으로 이동했습니다: ' + text('.reading-mission h2, .problem-pane h2, .slides-mission h2', 120); },
    async prev() { const b = byText('.header-navigation button', '← 이전'); if (!b || b.disabled) throw new Error('이전 미션으로 갈 수 없습니다'); b.click(); await sleep(600); return '이전 미션으로 이동했습니다: ' + text('.reading-mission h2, .problem-pane h2, .slides-mission h2', 120); },
    async goto(a) { const cells = document.querySelectorAll('.mission-cell'); const cell = cells[Number(a.mission) - 1]; if (!cell) throw new Error(`이 단원에는 ${a.mission}번 미션이 없습니다 (미션 ${cells.length}개)`); cell.click(); await sleep(600); return `${a.mission}번 미션으로 이동했습니다: ` + text('.reading-mission h2, .problem-pane h2, .slides-mission h2', 120); },
    async next_slide() { const b = byText('.slides-bar button', '다음 장 →'); if (!b || b.disabled) throw new Error('넘길 장이 없습니다'); b.click(); await sleep(300); return '다음 장으로 넘겼습니다: ' + text('.slides-counter', 20); },
    async finish_slides() { const b = byText('button', '다 봤어요 · 미션 완료'); if (!b) throw new Error('슬라이드 미션이 아닙니다'); if (!b.disabled) b.click(); await sleep(400); return '슬라이드 미션을 완료로 표시했습니다.'; },
  };
  async function run(actions) {
    if (!Array.isArray(actions)) return '동작 목록이 배열이 아닙니다.';
    const lines = [];
    for (const [i, action] of actions.entries()) {
      const name = action && action.action;
      const handler = handlers[name];
      if (!handler) { lines.push(`${i + 1}. ${name}: 모르는 동작입니다 (가능: ${Object.keys(handlers).join(', ')})`); continue; }
      try {
        lines.push(`${i + 1}. ${name}: ${await handler(action)}`);
      } catch (error) {
        lines.push(`${i + 1}. ${name}: 오류 - ${error && error.message ? error.message : error}`);
        break;
      }
    }
    return lines.join('\n');
  }
  globalThis.molipAgent = { run, actions: Object.keys(handlers) };
})();
