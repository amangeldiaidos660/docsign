const partnerSearchInput = document.getElementById('partnerSearch');
const partnerResults = document.getElementById('partnerResults');
const selectedPartners = document.getElementById('selectedPartners');
const clearSelectedBtn = document.getElementById('clearSelected');
const pdfInput = document.getElementById('pdfInput');
const pdfPreview = document.getElementById('pdfPreview');
const pdfPlaceholder = document.getElementById('pdfPlaceholder');
const pdfInfo = document.getElementById('pdfInfo');
const sendDocBtn = document.getElementById('sendDoc');
const resetFormBtn = document.getElementById('resetForm');
const createAlert = document.getElementById('createAlert');
const ecpSignBtn = document.getElementById('ecpSignBtn');
const signLog = document.getElementById('signLog');

let selectedIds = [];
let pdfBase64 = '';
let pdfFileName = '';

function renderAlert(type, message) {
    createAlert.innerHTML = `<div class="alert alert-${type} alert-dismissible" role="alert">${message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`;
}

function debounce(fn, ms) {
    let t;
    return function(...args) {
        clearTimeout(t);
        t = setTimeout(() => fn.apply(this, args), ms);
    };
}

function renderSelected() {
    selectedPartners.innerHTML = '';
    selectedIds.forEach((u) => {
        const a = document.createElement('div');
        a.className = 'list-group-item d-flex justify-content-between align-items-start';
        const subtitle = [u.email, u.bin, u.iin].filter(Boolean).join(' · ');
        a.innerHTML = `<div>
            <div class="fw-semibold">${u.full_name || 'Без имени'}${u.organization ? ' — ' + u.organization : ''}</div>
            <div class="small text-muted">${subtitle}</div>
        </div>
        <button type="button" class="btn btn-sm btn-outline-danger">Удалить</button>`;
        a.querySelector('button').addEventListener('click', () => {
            selectedIds = selectedIds.filter(x => x.id !== u.id);
            renderSelected();
        });
        selectedPartners.appendChild(a);
    });
}

async function searchPartners(q) {
    partnerResults.innerHTML = '';
    if (!q || q.trim().length < 2) return;
    try {
        const resp = await fetch(`/documents/partners?query=${encodeURIComponent(q)}&limit=10`, { credentials: 'same-origin' });
        if (!resp.ok) {
            renderAlert('danger', 'Ошибка поиска партнёров');
            return;
        }
        const data = await resp.json();
        const results = (data && data.results) ? data.results : [];
        if (!Array.isArray(results) || results.length === 0) {
            partnerResults.innerHTML = '<div class="list-group-item text-muted">Ничего не найдено</div>';
            return;
        }
        results.forEach(u => {
            const a = document.createElement('a');
            a.href = '#';
            a.className = 'list-group-item list-group-item-action';
            a.dataset.id = u.id;
            const subtitle = [u.email, u.bin, u.iin].filter(Boolean).join(' · ');
            a.innerHTML = `<div class="fw-semibold">${u.full_name || 'Без имени'}${u.organization ? ' — ' + u.organization : ''}</div><div class="small text-muted">${subtitle}</div>`;
            a.addEventListener('click', (e) => {
                e.preventDefault();
                if (selectedIds.find(x => x.id === u.id)) return;
                if (selectedIds.length >= 4) {
                    renderAlert('warning', 'Можно выбрать не более 4 партнёров');
                    return;
                }
                selectedIds.push(u);
                renderSelected();
            });
            partnerResults.appendChild(a);
        });
    } catch (e) {
        renderAlert('danger', 'Сетевая ошибка при поиске');
    }
}

const debouncedSearch = debounce((e) => {
    searchPartners(e.target.value);
}, 350);

if (partnerSearchInput) {
    partnerSearchInput.addEventListener('input', debouncedSearch);
}

if (clearSelectedBtn) {
    clearSelectedBtn.addEventListener('click', () => {
        selectedIds = [];
        renderSelected();
    });
}

if (pdfInput) {
    pdfInput.addEventListener('change', () => {
        const file = pdfInput.files && pdfInput.files[0];
        pdfBase64 = '';
        pdfFileName = '';
        pdfPreview.style.display = 'none';
        pdfPlaceholder.style.display = 'flex';
        pdfInfo.textContent = '';
        if (!file) return;
        if (file.type !== 'application/pdf') {
            renderAlert('warning', 'Можно загрузить только PDF файл');
            pdfInput.value = '';
            return;
        }
        pdfFileName = file.name;
        const reader = new FileReader();
        reader.onload = () => {
            const result = reader.result;
            const base64 = result.split(',')[1];
            pdfBase64 = base64;
            pdfPreview.src = result;
            pdfPreview.style.display = 'block';
            pdfPlaceholder.style.display = 'none';
            pdfInfo.textContent = `${file.name} • ${(file.size/1024/1024).toFixed(2)} MB`;
        };
        reader.readAsDataURL(file);
    });
}

async function sendDocument() {
    if (!selectedIds.length) {
        renderAlert('warning', 'Выберите хотя бы одного партнёра');
        return;
    }
    if (!pdfBase64 || !pdfFileName) {
        renderAlert('warning', 'Загрузите PDF документ');
        return;
    }
    const modal = new bootstrap.Modal(document.getElementById('signModal'));
    modal.show();

    /*
    // Отправка документа на сервер — временно отключено по ТЗ
    try {
        const resp = await fetch('/documents', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({
                title: pdfFileName,
                file_name: pdfFileName,
                file_base64: pdfBase64,
                participant_user_ids: selectedIds.map(u => u.id)
            })
        });
        if (!resp.ok) {
            const text = await resp.text();
            renderAlert('danger', text || 'Ошибка создания документа');
            return;
        }
        const data = await resp.json();
        renderAlert('success', `Документ создан. ID: ${data.document_id}`);
    } catch (e) {
        renderAlert('danger', 'Сетевая ошибка при создании документа');
    }
    */
}

if (sendDocBtn) {
    sendDocBtn.addEventListener('click', sendDocument);
}

if (resetFormBtn) {
    resetFormBtn.addEventListener('click', () => {
        selectedIds = [];
        renderSelected();
        partnerSearchInput.value = '';
        partnerResults.innerHTML = '';
        pdfInput.value = '';
        pdfBase64 = '';
        pdfFileName = '';
        pdfPreview.style.display = 'none';
        pdfPreview.src = '';
        pdfPlaceholder.style.display = 'flex';
        pdfInfo.textContent = '';
        createAlert.innerHTML = '';
    });
}

async function signWithEcp() {
    if (!pdfBase64) {
        renderAlert('warning', 'Сначала загрузите PDF');
        return;
    }
    try {
        const { default: ncaWebSocketManager } = await import('./ncaWebSocketManager.js');
        const { signData } = await import('./ncalayer.js');
        if (signLog) signLog.innerText = 'Открытие соединения с NCALayer...';
        await ncaWebSocketManager.connect();
        if (signLog) signLog.innerText = 'Подписание...';
        const signature = await signData(pdfBase64);
        const size = signature ? signature.length : 0;
        console.log('Размер подписи (символов):', size);
        if (signLog) signLog.innerText = `Готово. Размер подписи: ${size} символов.`;
        
        try {
            const resp = await fetch('/documents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({
                    title: pdfFileName,
                    file_name: pdfFileName,
                    file_base64: pdfBase64,
                    signature: signature,
                    participant_user_ids: selectedIds.map(u => u.id)
                })
            });
            if (!resp.ok) {
                const text = await resp.text();
                renderAlert('danger', text || 'Ошибка создания документа');
                return;
            }
            const data = await resp.json();
            renderAlert('success', `Документ создан. ID: ${data.document_id}`);
            selectedIds = [];
            renderSelected();
            pdfInput.value = '';
            pdfBase64 = '';
            pdfFileName = '';
            pdfPreview.style.display = 'none';
            pdfPreview.src = '';
            pdfPlaceholder.style.display = 'flex';
            pdfInfo.textContent = '';
            const modal = bootstrap.Modal.getInstance(document.getElementById('signModal'));
            modal.hide();
        } catch (e) {
            renderAlert('danger', 'Сетевая ошибка при создании документа');
        }
        
        ncaWebSocketManager.disconnect();
    } catch (e) {
        console.error('Ошибка подписи:', e);
        if (signLog) signLog.innerText = 'Ошибка подписи. Подробности в консоли.';
    }
}


if (ecpSignBtn) {
    ecpSignBtn.addEventListener('click', signWithEcp);
}