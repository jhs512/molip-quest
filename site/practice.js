(() => {
  let unlocked = null;
  let pending = null;
  let lastButton = null;
  const dialog = document.getElementById('instructor-dialog');
  const form = document.getElementById('unlock-form');
  const password = document.getElementById('instructor-password');
  const status = document.getElementById('unlock-status');
  const lock = document.getElementById('lock-instructor');
  const decode = (value) => Uint8Array.from(atob(value), char => char.charCodeAt(0));

  function show(button) {
    const result = button.closest('.exercise').querySelector('.instructor-result');
    const material = unlocked[button.dataset.problem];
    result.replaceChildren();
    const title = document.createElement('h3');
    title.textContent = button.dataset.kind === 'code' ? '정답' : '해설';
    result.append(title);
    if (button.dataset.kind === 'code') {
      const pre = document.createElement('pre');
      const code = document.createElement('code');
      code.textContent = material.code;
      pre.append(code);
      result.append(pre);
    } else {
      const list = document.createElement('ol');
      material.explanation.forEach(text => {
        const item = document.createElement('li');
        item.textContent = text;
        list.append(item);
      });
      result.append(list);
    }
    const close = document.createElement('button');
    close.type = 'button';
    close.textContent = '닫기';
    close.addEventListener('click', () => { result.hidden = true; result.replaceChildren(); button.focus(); });
    result.append(close);
    result.hidden = false;
    result.scrollIntoView({behavior:'smooth',block:'nearest'});
  }

  document.querySelectorAll('[data-problem]').forEach(button => {
    button.addEventListener('click', () => {
      lastButton = button;
      if (unlocked) { show(button); return; }
      pending = button;
      status.textContent = '';
      password.value = '';
      dialog.showModal();
      password.focus();
    });
  });

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const submit = form.querySelector('[type="submit"]');
    const supplied = password.value;
    password.value = '';
    submit.disabled = true;
    status.textContent = '확인 중…';
    try {
      if (!window.isSecureContext || !crypto.subtle) throw new Error('unsupported');
      const response = await fetch('data/instructor.json', {cache:'no-store'});
      if (!response.ok) throw new Error('download');
      const data = await response.json();
      const baseKey = await crypto.subtle.importKey('raw', new TextEncoder().encode(supplied), 'PBKDF2', false, ['deriveKey']);
      const key = await crypto.subtle.deriveKey({name:'PBKDF2',hash:'SHA-256',salt:decode(data.salt),iterations:data.iterations},baseKey,{name:'AES-GCM',length:256},false,['decrypt']);
      const plaintext = await crypto.subtle.decrypt({name:'AES-GCM',iv:decode(data.iv)},key,decode(data.ciphertext));
      unlocked = JSON.parse(new TextDecoder().decode(plaintext));
      lock.hidden = false;
      dialog.close();
      show(pending);
      pending = null;
    } catch (error) {
      status.textContent = error.message === 'unsupported'
        ? 'HTTPS 주소에서 최신 브라우저로 열어 주세요.'
        : error.message === 'download' || error instanceof TypeError
          ? '자료를 불러오지 못했습니다. 연결을 확인하고 다시 시도하세요.'
          : '비밀번호가 맞지 않습니다. 다시 입력하세요.';
      password.focus();
    } finally { submit.disabled = false; }
  });

  form.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => { password.value = ''; lastButton?.focus(); });
  lock.addEventListener('click', () => {
    unlocked = null;
    pending = null;
    document.querySelectorAll('.instructor-result').forEach(result => { result.hidden = true; result.replaceChildren(); });
    lock.hidden = true;
    document.querySelector('[data-problem]').focus();
  });
})();
