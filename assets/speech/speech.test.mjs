// Pure-function tests for the double-click reader. Run: node --test assets/speech/
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const context = { Intl, console };
context.globalThis = context;
vm.runInNewContext(readFileSync(new URL('./speech.js', import.meta.url), 'utf8'), context);
const speech = context.molipSpeech;

test('sentences are split with offsets that index the original text', () => {
  const text = '첫 코드는 한 줄입니다. print는 괄호 안의 것을 보여 주는 명령이고, 따옴표는 글자 표시입니다.';
  const sentences = speech.speechSentences(text);
  assert.equal(sentences.length, 2);
  assert.equal(text.slice(sentences[1].start, sentences[1].end), sentences[1].text);
  assert.ok(sentences[1].text.startsWith('print는'));
});

test('long sentences become bounded chunks that keep their sentence index', () => {
  const text = '가 '.repeat(200).trim() + '. 끝.';
  const chunks = speech.splitSpeechRanges(text, 100);
  assert.ok(chunks.length >= 3);
  assert.ok(chunks.every(c => c.text.length <= 100));
  assert.equal(chunks.at(-1).text, '끝.');
  assert.equal(chunks.at(-1).sentenceIndex, 1);
});

test('technical terms are pronounced in Korean while code spans stay verbatim', () => {
  assert.equal(speech.pronunciationText('Python의 `print(x)` 함수와 pandas DataFrame'), '파이썬의 print(x) 함수와 판다스 데이터프레임');
  assert.equal(speech.pronunciationText('MAE와 RMSE, 그리고 R²'), '엠에이이와 알엠에스이, 그리고 알 제곱');
  assert.equal(speech.pronunciationText('printer'), 'printer'); // not a whole-word match
});

test('numbers and operators read naturally', () => {
  assert.equal(speech.mathSpeechText('test_size=0.2'), 'test_size 이퀄 0 점 이');
  assert.equal(speech.mathSpeechText('생존율 38%'), '생존율 38 퍼센트');
  assert.equal(speech.mathSpeechText('price >= 10000'), 'price 크거나 같다 10000');
});

test('the controller reads chunks in order and resumes from the paused sentence', () => {
  const spoken = [];
  let current;
  class Utterance { constructor(text) { this.text = text; } }
  const synth = { getVoices: () => [{ lang: 'ko-KR', localService: true, default: true }], cancel() {}, resume() {}, speak(u) { spoken.push(u.text); current = u; } };
  const timers = { setTimeout: () => 0, clearTimeout() {} };
  const states = [];
  const controller = new speech.StorySpeech(synth, Utterance, ({ state }) => states.push(state), timers);
  controller.chunks = ['첫 문장.', '둘째 문장.', '셋째 문장.'];
  controller.start();
  assert.deepEqual(spoken, ['첫 문장.']);
  current.onstart(); current.onend();
  assert.deepEqual(spoken, ['첫 문장.', '둘째 문장.']);
  controller.pause();
  assert.equal(controller.state, 'paused');
  controller.start();
  assert.equal(spoken.at(-1), '둘째 문장.');
  current.onstart(); current.onend(); current.onstart(); current.onend();
  assert.equal(controller.state, 'ended');
  assert.ok(states.includes('speaking'));
});

test('without a Korean voice the controller reports an error instead of speaking', () => {
  const synth = { getVoices: () => [{ lang: 'en-US' }], cancel() {}, resume() {}, speak() { throw new Error('must not speak'); } };
  let message;
  const controller = new speech.StorySpeech(synth, class {}, update => { message = update.message; });
  controller.chunks = ['문장'];
  controller.start();
  assert.equal(controller.state, 'error');
  assert.match(message, /한국어 음성/);
});
