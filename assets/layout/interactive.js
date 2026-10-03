// Stepwise interactive pictures ("explorable explanations") from ```interactive fences.
//
//   ```interactive
//   위젯: overfit
//   ```
//
// A widget starts as an almost empty canvas and adds one idea per step when the student
// presses "다음 단계"; some steps hand over a slider or a button so the student can move
// the picture and watch the numbers change. Everything is plain SVG and runs offline.
(function () {
  'use strict';
  if (globalThis.molipInteractive || typeof document === 'undefined') return;
  const NS = 'http://www.w3.org/2000/svg';
  const el = (name, attrs, parent) => {
    const node = document.createElementNS(NS, name);
    for (const [k, v] of Object.entries(attrs || {})) node.setAttribute(k, v);
    if (parent) parent.append(node);
    return node;
  };
  const text = (parent, x, y, content, attrs) => { const t = el('text', { x, y, ...(attrs || {}) }, parent); t.textContent = content; return t; };
  const show = node => { node.classList.add('on'); };
  const hide = node => { node.classList.remove('on'); };
  // Deterministic pseudo random numbers so every student sees the same picture.
  function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }

  // ---- shared frame: canvas, caption, controls, step button ----
  function frame(container, title, height) {
    const root = document.createElement('div'); root.className = 'interactive';
    const head = document.createElement('div'); head.className = 'interactive-head';
    const h = document.createElement('strong'); h.textContent = title; head.append(h);
    const stepLabel = document.createElement('span'); stepLabel.className = 'interactive-step'; head.append(stepLabel);
    root.append(head);
    const svg = el('svg', { viewBox: `0 0 720 ${height}`, role: 'img', 'aria-label': title });
    root.append(svg);
    const caption = document.createElement('p'); caption.className = 'interactive-caption'; root.append(caption);
    const controls = document.createElement('div'); controls.className = 'interactive-controls'; root.append(controls);
    const next = document.createElement('button'); next.type = 'button'; next.className = 'interactive-next'; next.textContent = '다음 단계 →'; controls.append(next);
    const extra = document.createElement('div'); extra.className = 'interactive-extra'; controls.append(extra);
    container.append(root);
    let index = -1, steps = [];
    function go(i) {
      index = i;
      steps[i].enter();
      caption.textContent = steps[i].text;
      stepLabel.textContent = `${i + 1} / ${steps.length}`;
      next.textContent = i + 1 < steps.length ? '다음 단계 →' : '처음부터';
    }
    next.onclick = () => { if (index + 1 < steps.length) go(index + 1); else { steps.forEach(s => s.reset && s.reset()); go(0); } };
    return { svg, caption, extra, start(list) { steps = list; go(0); } };
  }
  function slider(extra, label, min, max, step, value, onInput) {
    const wrap = document.createElement('label'); wrap.className = 'interactive-slider';
    const name = document.createElement('span'); name.textContent = label; wrap.append(name);
    const input = document.createElement('input'); input.type = 'range'; input.min = min; input.max = max; input.step = step; input.value = value; wrap.append(input);
    const out = document.createElement('output'); out.textContent = value; wrap.append(out);
    input.oninput = () => { out.textContent = input.value; onInput(Number(input.value)); };
    wrap.hidden = true; extra.append(wrap);
    return { wrap, input, out, enable() { wrap.hidden = false; }, set(v) { input.value = v; out.textContent = v; } };
  }

  // ---- widget 1: overfitting — a 1-D regression tree whose depth the student controls ----
  function overfit(container) {
    const H = 360, W = 720, L = 60, R = 700, T = 30, B = 290;
    const f = frame(container, '트리 깊이와 과적합', H);
    const random = rng(7);
    const truth = x => 0.5 + 0.35 * Math.sin(x * 6.2);
    const make = n => Array.from({ length: n }, () => { const x = random(); return { x, y: Math.min(0.98, Math.max(0.02, truth(x) + (random() - 0.5) * 0.25)) }; });
    const train = make(24), test = make(12);
    const sx = x => L + x * (R - L), sy = y => B - y * (B - T);
    // Regression tree on one feature: split where squared error drops most, up to a depth.
    function fit(points, depth) {
      const mean = pts => pts.reduce((a, p) => a + p.y, 0) / pts.length;
      function node(pts, d) {
        if (d === 0 || pts.length <= 2) return { leaf: mean(pts) };
        const sorted = [...pts].sort((a, b) => a.x - b.x);
        let best = null;
        for (let i = 1; i < sorted.length; i++) {
          const left = sorted.slice(0, i), right = sorted.slice(i);
          const err = pts => { const m = mean(pts); return pts.reduce((a, p) => a + (p.y - m) ** 2, 0); };
          const score = err(left) + err(right);
          if (!best || score < best.score) best = { score, cut: (sorted[i - 1].x + sorted[i].x) / 2, left, right };
        }
        return { cut: best.cut, left: node(best.left, d - 1), right: node(best.right, d - 1) };
      }
      const tree = node(points, depth);
      const predict = x => { let n = tree; while (n.leaf === undefined) n = x < n.cut ? n.left : n.right; return n.leaf; };
      return predict;
    }
    const mae = (pts, predict) => pts.reduce((a, p) => a + Math.abs(p.y - predict(p.x)), 0) / pts.length;
    // Static scenery.
    el('line', { x1: L, y1: B, x2: R, y2: B, class: 'axis' }, f.svg);
    el('line', { x1: L, y1: T, x2: L, y2: B, class: 'axis' }, f.svg);
    text(f.svg, (L + R) / 2, B + 28, '입력 (예: 요금)', { class: 'label', 'text-anchor': 'middle' });
    text(f.svg, 18, (T + B) / 2, '정답', { class: 'label', 'text-anchor': 'middle', transform: `rotate(-90 18 ${(T + B) / 2})` });
    const gTrain = el('g', { class: 'fade' }, f.svg), gTest = el('g', { class: 'fade' }, f.svg), gModel = el('g', { class: 'fade' }, f.svg);
    for (const p of train) el('circle', { cx: sx(p.x), cy: sy(p.y), r: 5, class: 'train' }, gTrain);
    for (const p of test) el('path', { d: `M${sx(p.x) - 5},${sy(p.y) - 5} l10,10 m0,-10 l-10,10`, class: 'test' }, gTest);
    const line = el('path', { class: 'model' }, gModel);
    const scoreTrain = text(f.svg, R, T + 4, '', { class: 'score train-score', 'text-anchor': 'end' });
    const scoreTest = text(f.svg, R, T + 24, '', { class: 'score test-score', 'text-anchor': 'end' });
    let depth = 1, showTest = false;
    function draw() {
      const predict = fit(train, depth);
      let d = '';
      for (let i = 0; i <= 200; i++) { const x = i / 200; d += (i ? 'L' : 'M') + sx(x).toFixed(1) + ',' + sy(predict(x)).toFixed(1); }
      line.setAttribute('d', d);
      scoreTrain.textContent = `훈련 오차 ${mae(train, predict).toFixed(3)}`;
      scoreTest.textContent = showTest ? `테스트 오차 ${mae(test, predict).toFixed(3)}` : '';
    }
    const s = slider(f.extra, '트리 깊이 max_depth', 1, 8, 1, 1, v => { depth = v; draw(); });
    f.start([
      { text: '훈련 자료 24개입니다. 가로가 입력, 세로가 맞혀야 할 숫자입니다.', enter() { show(gTrain); hide(gModel); hide(gTest); s.wrap.hidden = true; showTest = false; }, reset() { depth = 1; s.set(1); } },
      { text: '깊이 1인 트리는 질문 한 번으로 두 구간을 나눕니다. 선이 모델의 답입니다.', enter() { depth = 1; s.set(1); draw(); show(gModel); } },
      { text: '슬라이더로 깊이를 올려 보세요. 훈련 오차가 계속 내려갑니다. 점을 전부 외워 가는 중입니다.', enter() { s.enable(); draw(); } },
      { text: '처음 보는 테스트 자료 12개(×)가 들어왔습니다. 깊이를 다시 움직여 보세요. 훈련 오차는 내려가는데 테스트 오차는 어느 깊이부터 다시 올라갑니다. 그 지점이 과적합의 시작입니다.', enter() { showTest = true; show(gTest); draw(); } },
    ]);
  }

  // ---- widget 2: threshold — probabilities become yes/no where the student puts the line ----
  function threshold(container) {
    const H = 330, W = 720, L = 50, R = 690, T = 40, B = 240, N = 40;
    const f = frame(container, '임계값: 확률을 경고로 바꾸는 선', H);
    const random = rng(11);
    // Defaults are more likely at high probabilities but also hide among the low ones, so the
    // threshold trades missed defaults against false alarms instead of just adding alarms.
    const customers = Array.from({ length: N }, (_, i) => { const p = (i + 0.5) / N; return { p, bad: random() < 0.15 + 0.75 * p }; });
    const sx = p => L + p * (R - L), bw = (R - L) / N - 2;
    el('line', { x1: L, y1: B, x2: R, y2: B, class: 'axis' }, f.svg);
    for (const v of [0, 0.5, 1]) text(f.svg, sx(v), B + 20, v.toFixed(1), { class: 'label', 'text-anchor': 'middle' });
    text(f.svg, (L + R) / 2, B + 40, '모델이 말한 부도 확률', { class: 'label', 'text-anchor': 'middle' });
    const bars = customers.map(c => el('rect', { x: sx(c.p) - bw / 2, y: B - 20 - c.p * (B - T - 30), width: bw, height: 20 + c.p * (B - T - 30), class: 'bar fade' }, f.svg));
    const marks = customers.map(c => el('circle', { cx: sx(c.p), cy: B - 10, r: 4, class: 'bad fade', style: c.bad ? '' : 'display:none' }, f.svg));
    const cut = el('line', { x1: sx(0.5), y1: T - 10, x2: sx(0.5), y2: B, class: 'cut fade' }, f.svg);
    const cutLabel = text(f.svg, sx(0.5), T - 16, '임계값 0.50', { class: 'label cut-label fade', 'text-anchor': 'middle' });
    const summary = text(f.svg, L, H - 12, '', { class: 'score' });
    const cost = text(f.svg, R, H - 12, '', { class: 'score', 'text-anchor': 'end' });
    let t = 0.5, showCost = false;
    function draw() {
      let tp = 0, fp = 0, fn = 0, tn = 0;
      customers.forEach((c, i) => {
        const warn = c.p >= t;
        bars[i].classList.toggle('warn', warn);
        if (warn && c.bad) tp++; else if (warn) fp++; else if (c.bad) fn++; else tn++;
      });
      cut.setAttribute('x1', sx(t)); cut.setAttribute('x2', sx(t)); cutLabel.setAttribute('x', sx(t)); cutLabel.textContent = `임계값 ${t.toFixed(2)}`;
      const precision = tp + fp ? tp / (tp + fp) : 0, recall = tp + fn ? tp / (tp + fn) : 0;
      summary.textContent = `경고 ${tp + fp}명 · 맞음 ${tp} 틀림 ${fp} · 놓침 ${fn} · 정밀도 ${precision.toFixed(2)} 재현율 ${recall.toFixed(2)}`;
      cost.textContent = showCost ? `비용 ${(fn * 100 + fp * 5).toLocaleString()}만 원 (놓침 100만, 헛경고 5만)` : '';
    }
    const s = slider(f.extra, '임계값', 0.05, 0.95, 0.05, 0.5, v => { t = v; draw(); });
    f.start([
      { text: '고객 40명을 모델이 말한 부도 확률 순서로 세웠습니다. 막대가 높을수록 부도 확률이 큽니다.', enter() { bars.forEach(show); marks.forEach(hide); hide(cut); hide(cutLabel); s.wrap.hidden = true; showCost = false; t = 0.5; s.set(0.5); draw(); summary.textContent = ''; } },
      { text: '점이 찍힌 사람이 실제로 부도를 낸 고객입니다. 확률이 높은 쪽에 많지만 낮은 쪽에도 있습니다.', enter() { marks.forEach(show); } },
      { text: '임계값 0.5보다 오른쪽이면 경고를 보냅니다. 경고 중 맞은 비율이 정밀도, 실제 부도 중 잡은 비율이 재현율입니다.', enter() { show(cut); show(cutLabel); draw(); } },
      { text: '선을 움직여 보세요. 왼쪽으로 가면 놓치는 부도(FN)는 줄고 헛경고(FP)는 늘어납니다. 어디에 둘지는 비용을 아는 사람이 정합니다.', enter() { s.enable(); showCost = true; draw(); } },
    ]);
  }

  // ---- widget 3: temporal split — a date strip, the test window, and the boundary day ----
  function temporal(container) {
    const H = 300, N = 30, L = 30, R = 690, T = 70, cell = (R - L) / N;
    const f = frame(container, '시간 분리와 경계의 하루', H);
    const cells = [], labels = [];
    for (let i = 0; i < N; i++) {
      cells.push(el('rect', { x: L + i * cell + 1, y: T, width: cell - 2, height: 40, class: 'day fade' }, f.svg));
      if (i % 5 === 0) labels.push(text(f.svg, L + i * cell + cell / 2, T + 60, `${i + 1}일`, { class: 'label fade', 'text-anchor': 'middle' }));
    }
    const testStart = N - 8;
    const bracket = el('rect', { x: L + testStart * cell, y: T - 14, width: 8 * cell, height: 68, class: 'window fade' }, f.svg);
    const windowLabel = text(f.svg, L + (testStart + 4) * cell, T - 20, '테스트 기간 (마지막 8일)', { class: 'label fade', 'text-anchor': 'middle' });
    const arrow = el('path', { d: `M${L + (testStart - 1) * cell + cell / 2},${T + 40} q${cell / 2},40 ${cell},0`, class: 'arrow fade' }, f.svg);
    const arrowLabel = text(f.svg, L + (testStart - 0.5) * cell, T + 100, '이 행의 정답은 테스트 첫날 종가', { class: 'label fade', 'text-anchor': 'middle' });
    const shuffled = el('g', { class: 'fade' }, f.svg);
    const random = rng(3);
    const order = Array.from({ length: N }, (_, i) => i).sort(() => random() - 0.5);
    order.forEach((day, slot) => { el('rect', { x: L + slot * cell + 1, y: T + 150, width: cell - 2, height: 30, class: day >= testStart ? 'day test' : 'day' }, shuffled); });
    text(shuffled, L, T + 200, '무작위로 섞으면: 미래(진한 칸)로 과거를 맞히게 됩니다', { class: 'label' });
    f.start([
      { text: '거래일 30일을 날짜순으로 세웠습니다. 시간 자료는 순서가 있습니다.', enter() { cells.forEach(c => { show(c); c.classList.remove('test', 'boundary'); }); labels.forEach(show); hide(bracket); hide(windowLabel); hide(arrow); hide(arrowLabel); hide(shuffled); } },
      { text: '뒤쪽 8일을 테스트로 떼어 둡니다. 앞 기간으로 훈련하고 뒤 기간으로 채점합니다.', enter() { show(bracket); show(windowLabel); cells.forEach((c, i) => c.classList.toggle('test', i >= testStart)); } },
      { text: '경계 바로 앞 하루를 보세요. 입력 날짜는 훈련이지만 그 행의 정답은 테스트 첫날의 종가입니다. 그래서 훈련에서 뺍니다.', enter() { show(arrow); show(arrowLabel); cells[testStart - 1].classList.add('boundary'); } },
      { text: '비교: 승객처럼 무작위로 섞어 나누면 어떻게 될까요. 6월 가격으로 배워 3월을 맞히는 셈이 됩니다.', enter() { show(shuffled); } },
    ]);
  }

  const WIDGETS = { overfit, threshold, temporal };
  const seen = new WeakSet();
  function render(root) {
    if (!(root instanceof Element) && root !== document) return;
    const codes = [...root.querySelectorAll('pre > code.language-interactive')];
    if (root instanceof Element && root.matches('pre > code.language-interactive')) codes.push(root);
    for (const code of codes) {
      const pre = code.parentElement;
      if (!pre || !pre.isConnected || seen.has(pre)) continue;
      seen.add(pre);
      const name = (code.textContent.match(/위젯:\s*(\w+)/) || [])[1];
      const figure = document.createElement('figure'); figure.className = 'interactive-strip';
      if (WIDGETS[name]) { try { WIDGETS[name](figure); } catch (error) { figure.textContent = '그림을 그리지 못했습니다: ' + error.message; } }
      else figure.textContent = '알 수 없는 위젯: ' + name;
      pre.replaceWith(figure);
    }
  }
  new MutationObserver(records => { for (const r of records) for (const n of r.addedNodes) if (n instanceof Element) render(n); }).observe(document.body, { childList: true, subtree: true });
  render(document);
  globalThis.molipInteractive = { render, WIDGETS };
})();
