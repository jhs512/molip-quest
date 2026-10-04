// Celebration is driven by persisted mission counts, never by animation state.
(() => {
  if (globalThis.molipVictory) return;
  const seen = new WeakSet();
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  function celebrate(card) {
    if (seen.has(card)) return;
    seen.add(card);
    const before = Number(card.dataset.xpBefore), after = Number(card.dataset.xpAfter);
    const fill = card.querySelector('.victory-fill');
    const total = card.querySelector('.victory-total');
    const level = card.querySelector('.victory-level');
    const start = performance.now();
    let frame, canvas, ctx;
    const particles = [];
    if (!reduced.matches) {
      canvas = document.createElement('canvas');
      canvas.className = 'victory-fireworks';
      canvas.setAttribute('aria-hidden', 'true');
      (document.fullscreenElement || document.body).append(canvas);
      const dpr = Math.min(devicePixelRatio || 1, 2);
      canvas.width = innerWidth * dpr; canvas.height = innerHeight * dpr;
      ctx = canvas.getContext('2d'); ctx.scale(dpr, dpr);
      const colors = ['#ffdc84', '#67e8e0', '#c7a5ff', '#ffffff', '#ffa8ba'];
      for (let burst = 0; burst < 5; burst++) {
        const x = innerWidth * [.2, .8, .5, .12, .88][burst];
        const y = innerHeight * [.35, .35, .18, .65, .65][burst];
        for (let i = 0; i < 48; i++) {
          const angle = Math.PI * 2 * i / 48;
          const speed = 70 + Math.random() * 170;
          particles.push({ x, y, vx: Math.cos(angle)*speed, vy: Math.sin(angle)*speed,
            delay: burst * 170, color: colors[i % colors.length], size: 1.5 + Math.random()*2 });
        }
      }
    }
    function update(now) {
      if (!card.isConnected) { canvas?.remove(); cancelAnimationFrame(frame); return; }
      const elapsed = now - start;
      const t = reduced.matches ? 1 : Math.min(1, elapsed / 1500);
      const ease = 1 - Math.pow(1-t, 3);
      const xp = Math.round(before + (after-before)*ease);
      total.textContent = `${xp.toLocaleString()} XP`;
      level.textContent = `Lv. ${Math.floor(xp/500)+1}`;
      fill.style.width = `${(xp%500)/5}%`;
      if (after > before && Math.floor(xp/500) > Math.floor(before/500)) {
        card.classList.add('leveled-up');
        card.querySelector('.victory-level-note').textContent = 'LEVEL UP! 새로운 레벨에 도달했어요.';
      }
      if (ctx) {
        ctx.clearRect(0, 0, innerWidth, innerHeight);
        for (const p of particles) {
          const age = (elapsed-p.delay)/1000;
          if (age < 0 || age > 1.65) continue;
          ctx.globalAlpha = Math.pow(1-age/1.65, 1.4);
          ctx.strokeStyle = p.color; ctx.fillStyle = p.color;
          ctx.shadowBlur = 12; ctx.shadowColor = p.color;
          const x = p.x+p.vx*age, y = p.y+p.vy*age+80*age*age;
          ctx.lineWidth = p.size;
          ctx.beginPath(); ctx.moveTo(x-p.vx*.025, y-p.vy*.025); ctx.lineTo(x,y); ctx.stroke();
        }
        ctx.globalAlpha = 1;
      }
      if (elapsed < 2600 && !reduced.matches) frame = requestAnimationFrame(update);
      else { canvas?.remove(); card.dataset.celebrated = 'true'; }
    }
    frame = requestAnimationFrame(update);
  }
  function scan() { document.querySelectorAll('.victory-panel').forEach(celebrate); }
  new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
  globalThis.molipVictory = { scan }; scan();
})();
