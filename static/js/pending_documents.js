const pendingDocsList = document.getElementById('pendingDocsList');
const emptyPendingState = document.getElementById('emptyPendingState');
const docsPerPage = document.getElementById('docsPerPage');
const pagination = document.getElementById('pagination');
const showingFrom = document.getElementById('showingFrom');
const showingTo = document.getElementById('showingTo');
const totalDocs = document.getElementById('totalDocs');

let currentPage = 1;
let allDocuments = [];

async function loadPendingDocuments() {
    try {
        const response = await fetch('/documents/pending', {
            credentials: 'same-origin'
        });
        const data = await response.json();
        
        if (!data.documents || data.documents.length === 0) {
            pendingDocsList.innerHTML = '';
            emptyPendingState.style.display = 'block';
            pagination.innerHTML = '';
            updateShowingInfo(0, 0, 0);
            return;
        }
        
        allDocuments = data.documents;
        emptyPendingState.style.display = 'none';
        renderDocuments();
    } catch (error) {
        console.error('Error loading pending documents:', error);
    }
}

function renderDocuments() {
    const perPage = parseInt(docsPerPage.value);
    const start = (currentPage - 1) * perPage;
    const end = start + perPage;
    const pageDocuments = allDocuments.slice(start, end);
    
    updateShowingInfo(start + 1, Math.min(end, allDocuments.length), allDocuments.length);
    renderPagination(Math.ceil(allDocuments.length / perPage));
    
    pendingDocsList.innerHTML = pageDocuments.map((doc, index) => {
        const partiesInfo = doc.parties.map(p => {
            const info = [];
            if (p.role === 'initiator') info.push('Инициатор');
            if (p.role === 'signer') info.push('Подписант');
            if (p.full_name) info.push(p.full_name);
            if (p.email) info.push(p.email);
            if (p.iin) info.push(`ИИН: ${p.iin}`);
            
            return `
                <div class="party-item py-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="party-info">${info.join(' • ')}</div>
                        <span class="badge ${p.status === 'signed' ? 'bg-success' : 'bg-warning'}">
                            ${p.status === 'signed' ? 'Подписано' : 'Ожидает подписи'}
                        </span>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <tr class="document-row">
                <td class="align-middle">${start + index + 1}</td>
                <td class="align-middle">${new Date(doc.created_at).toLocaleString()}</td>
                <td>
                    <div class="parties-container border-start border-4 border-primary ps-3">
                        ${partiesInfo}
                    </div>
                </td>
                <td class="align-middle">
                    <div class="d-grid gap-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="viewDocument(${doc.id}, '${doc.file_path}')">
                            <i class="bi bi-eye"></i> Открыть
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="signDocument(${doc.id})">
                            <i class="bi bi-pen"></i> Подписать
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function renderPagination(totalPages) {
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }

    let pages = '';
    pages += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage - 1}">
                <i class="bi bi-chevron-left"></i>
            </a>
        </li>
    `;
    
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
            pages += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        } else if (i === currentPage - 2 || i === currentPage + 2) {
            pages += `
                <li class="page-item disabled">
                    <span class="page-link">...</span>
                </li>
            `;
        }
    }
    
    pages += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage + 1}">
                <i class="bi bi-chevron-right"></i>
            </a>
        </li>
    `;
    
    pagination.innerHTML = pages;
}

function updateShowingInfo(from, to, total) {
    showingFrom.textContent = from;
    showingTo.textContent = to;
    totalDocs.textContent = total;
}

function viewDocument(id, filePath) {
    const modal = new bootstrap.Modal(document.getElementById('viewDocModal'));
    document.getElementById('pdfViewer').src = `/static/${filePath}`;
    modal.show();
}

docsPerPage.addEventListener('change', () => {
    currentPage = 1;
    renderDocuments();
});

pagination.addEventListener('click', (e) => {
    e.preventDefault();
    const pageLink = e.target.closest('[data-page]');
    if (pageLink) {
        const newPage = parseInt(pageLink.dataset.page);
        if (newPage !== currentPage && newPage > 0) {
            currentPage = newPage;
            renderDocuments();
        }
    }
});

document.addEventListener('DOMContentLoaded', loadPendingDocuments);