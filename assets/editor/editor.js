import { EditorView, basicSetup } from 'codemirror';
import { python } from '@codemirror/lang-python';
import { keymap } from '@codemirror/view';
import { indentWithTab } from '@codemirror/commands';
import { syntaxHighlighting, HighlightStyle } from '@codemirror/language';
import { tags, highlightCode, classHighlighter } from '@lezer/highlight';

// The textarea stays as the Dioxus event bridge and accessible fallback.
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
          extensions: [basicSetup, python(), keymap.of([indentWithTab]), theme, colors,
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
  window.molipCodeEditors = { sync };
  new MutationObserver(sync).observe(document.body, {
    subtree: true, childList: true, attributes: true,
    attributeFilter: ['data-editor-value', 'data-editor-reset'],
  });
  sync();
}
