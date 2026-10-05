document.querySelectorAll('.copy').forEach((button) => {
  button.addEventListener('click', async () => {
    const code = button.parentElement.querySelector('code').textContent;
    const status = document.getElementById('copy-status');
    try {
      await navigator.clipboard.writeText(code);
      button.textContent = '복사 완료 ✓';
      status.textContent = '설치 명령을 복사했습니다.';
      setTimeout(() => { button.textContent = '복사'; }, 2000);
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(button.parentElement.querySelector('code'));
      selection.removeAllRanges();
      selection.addRange(range);
      status.textContent = '명령을 선택했습니다. 직접 복사해 주세요.';
      button.textContent = '직접 복사해 주세요';
    }
  });
});
