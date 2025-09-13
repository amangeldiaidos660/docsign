window.openSignModal = function(documentId) {
  const el = document.getElementById('signModal');
  if (!el) return;
  if (documentId) {
    el.dataset.documentId = String(documentId);
  } else {
    delete el.dataset.documentId;
  }
  const btn = el.querySelector('#ecpSignBtn');
  if (btn) {
    btn.onclick = null;
    btn.onclick = async () => {
      btn.disabled = true;
      const logEl = el.querySelector('#signLog');
      try {
        const id = el.dataset.documentId;
        if (id) {
          if (logEl) logEl.innerText = 'Получение документа...';
          const data = await window.signService.getBase64(id);
          const base64 = data && data.file_base64 ? data.file_base64 : '';
          if (!base64) throw new Error('Пустое содержимое файла');
          const { default: ncaWebSocketManager } = await import('./ncaWebSocketManager.js');
          const { signData } = await import('./ncalayer.js');
          if (logEl) logEl.innerText = 'Открытие соединения с NCALayer...';
          await ncaWebSocketManager.connect();
          try {
            if (logEl) logEl.innerText = 'Подписание...';
            const signature = await signData(base64);
            const size = signature ? signature.length : 0;
            console.log('Вторая подпись (CMS):', signature);
            await window.signService.addSign(id, base64, signature);
            if (logEl) logEl.innerText = `Готово. Размер подписи: ${size} символов.`;
          } finally {
            ncaWebSocketManager.disconnect();
          }
        } else {
          if (window.signWithEcp) {
            await window.signWithEcp();
          }
        }
      } catch (e) {
        console.error('Ошибка подписи:', e);
        if (logEl) logEl.innerText = 'Ошибка подписи. Подробности в консоли.';
      } finally {
        btn.disabled = false;
      }
    };
  }
  const modal = new bootstrap.Modal(el);
  modal.show();
};