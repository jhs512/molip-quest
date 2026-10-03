# Comic strips

Course concepts embed short comics as ```` ```comic-gen ```` fences written in the
Korean YAML syntax of [Comic Gen](https://github.com/jhs512/comic-gen)
(authoring reference: https://jhs512.github.io/comic-gen/llm-guide.md).
The Markdown renderer keeps the fence as `pre > code.language-comic-gen`;
`comics.js` replaces each one with a `<figure class="comic-strip">` holding the
SVG of every panel, so the strip reads inline with the surrounding paragraphs.

`comic-gen.js` is the vendored browser SDK (v0.7.5, an ES module from
`https://cdn.jsdelivr.net/gh/jhs512/comic-gen@v0.7.5/cdn/comic-gen.js`). The app
embeds it as a string and the loader imports it from a Blob URL, so comics work
offline on desktop and Android. Mermaid diagrams inside panels are not used:
they would fetch Mermaid from a CDN at runtime.

Editorial rules for new comics live with the course source in `tools/kpc_course/`:
a comic is one Markdown paragraph (no blank lines inside the fence), every
dialogue line fits in two short rows, and the shared cast (강사, 민지, 준호,
파이썬, 빵 공장장, 콜센터 팀장) keeps the same appearance across units.
