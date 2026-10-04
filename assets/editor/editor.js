import { EditorView, lineNumbers, highlightActiveLineGutter, highlightSpecialChars, drawSelection,
  dropCursor, rectangularSelection, crosshairCursor, highlightActiveLine, keymap } from '@codemirror/view';
import { EditorState } from '@codemirror/state';
import { python } from '@codemirror/lang-python';
import { history, defaultKeymap, historyKeymap, indentWithTab } from '@codemirror/commands';
import { syntaxHighlighting, HighlightStyle, indentUnit, defaultHighlightStyle, indentOnInput, bracketMatching, foldGutter, foldKeymap } from '@codemirror/language';
import { searchKeymap, highlightSelectionMatches } from '@codemirror/search';
import { tags, highlightCode, classHighlighter } from '@lezer/highlight';

// The textarea stays as the Dioxus event bridge and accessible fallback.
// Indentation is four spaces, as the course text and every example teach.
if (!window.molipCodeEditors) {
  const editors = new Map();
  const resetVersions = new Map();
  const colors = syntaxHighlighting(HighlightStyle.define([
    { tag: tags.keyword, color: '#c792ea' },
    { tag: tags.string, color: '#a8d99c' },
    { tag: tags.comment, color: '#92abc0' },
    { tag: tags.number, color: '#f6c177' },
    { tag: tags.function(tags.variableName), color: '#82cfff' },
    { tag: tags.operator, color: '#89dceb' },
  ]));
  // codemirror's basicSetup minus autocompletion and auto-closing brackets: learners type
  // every character themselves, and a popup over "pr" only distracts beginners.
  const setup = [
    lineNumbers(), highlightActiveLineGutter(), highlightSpecialChars(), history(), foldGutter(),
    drawSelection(), dropCursor(), EditorState.allowMultipleSelections.of(true), indentOnInput(),
    syntaxHighlighting(defaultHighlightStyle, { fallback: true }), bracketMatching(),
    rectangularSelection(), crosshairCursor(), highlightActiveLine(), highlightSelectionMatches(),
    keymap.of([...defaultKeymap, ...searchKeymap, ...historyKeymap, ...foldKeymap]),
  ];
  const theme = EditorView.theme({
    '&': { height: '100%', backgroundColor: '#202d3e', color: '#e3edf6' },
    '.cm-scroller': { overflow: 'auto', fontFamily: 'Consolas, monospace', fontSize: '15px' },
    '.cm-content': { padding: '16px 0', caretColor: '#fff' },
    '.cm-gutters': { backgroundColor: '#202d3e', color: '#8299ae', border: 'none' },
    // Selection is drawn behind the text; keep the active line translucent.
    '.cm-activeLine': { backgroundColor: '#2b405555' },
    '.cm-activeLineGutter': { backgroundColor: '#2b4055' },
    '.cm-cursor': { borderLeftColor: '#fff' },
    '.cm-selectionBackground': { backgroundColor: '#426385 !important' },
    '.cm-panels, .cm-tooltip': { backgroundColor: '#192b3c', color: '#e3edf6' },
  }, { dark: true });

  function sync() {
    document.querySelectorAll('.markdown pre code.language-python').forEach(code => {
      const source = code.textContent;
      if (code.dataset.highlighted === source) return;
      code.dataset.highlighted = source;
      const fragment = document.createDocumentFragment();
      highlightCode(source, python().language.parser.parse(source), classHighlighter, (text, classes) => {
        const span = document.createElement('span');
        span.textContent = text;
        span.className = classes;
        fragment.append(span);
      }, () => fragment.append(document.createTextNode('\n')));
      code.replaceChildren(fragment);
    });
    for (const [element, view] of editors) {
      if (!element.isConnected) { view.destroy(); editors.delete(element); resetVersions.delete(element); }
    }
    document.querySelectorAll('textarea[data-code-editor]').forEach(element => {
      const source = element.getAttribute('data-editor-value') ?? element.value;
      const resetVersion = element.getAttribute('data-editor-reset');
      let view = editors.get(element);
      if (!view) {
        const host = document.createElement('div');
        host.className = 'python-editor-host';
        element.after(host);
        view = new EditorView({
          doc: source,
          parent: host,
          extensions: [setup, python(), indentUnit.of('    '), keymap.of([indentWithTab]), theme, colors,
            EditorView.contentAttributes.of({ 'aria-label': 'Python 코드 편집기' }),
            EditorView.updateListener.of(update => {
              if (!update.docChanged || element.value === update.state.doc.toString()) return;
              element.value = update.state.doc.toString();
              element.dispatchEvent(new Event('input', { bubbles: true }));
            })],
        });
        editors.set(element, view);
        resetVersions.set(element, resetVersion);
        element.hidden = true;
      } else if (resetVersions.get(element) !== resetVersion) {
        // Only explicit resets may replace the editor document. Typing is owned
        // by CodeMirror: delayed backend echoes must not interrupt IME input.
        resetVersions.set(element, resetVersion);
        element.value = source;
        if (view.state.doc.toString() !== source) {
          view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: source } });
        }
      }
    });
  }
  // Replace the document of the editor on screen (used by the tutor agent). The update
  // listener above then syncs the hidden textarea and tells the Rust side.
  function setValue(source) {
    let done = false;
    for (const [element, view] of editors) {
      if (!element.isConnected) continue;
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: source } });
      done = true;
    }
    return done;
  }
  window.molipCodeEditors = { sync, setValue };
  new MutationObserver(sync).observe(document.body, {
    subtree: true, childList: true, attributes: true,
    attributeFilter: ['data-editor-value', 'data-editor-reset'],
  });
  sync();
}
