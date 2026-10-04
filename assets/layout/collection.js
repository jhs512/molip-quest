(() => {
  if (globalThis.molipCollection) return;
  function scan() {
    document.querySelectorAll('.collection-page .collection-card.acquired').forEach(card => {
      const course = card.closest('[data-collection-course]').dataset.collectionCourse;
      const key = `molip.collection.seen:${course}:${card.dataset.cardId}`;
      try { if (localStorage.getItem(key)) card.querySelector('.collection-new').hidden = true; } catch {}
      if (card.dataset.seenBound) return;
      card.dataset.seenBound = 'true';
      card.addEventListener('click', () => {
        try { localStorage.setItem(key, 'true'); } catch {}
        card.querySelector('.collection-new').hidden = true;
      });
    });
  }
  new MutationObserver(scan).observe(document.body, {childList: true, subtree: true});
  globalThis.molipCollection = {scan}; scan();
})();
