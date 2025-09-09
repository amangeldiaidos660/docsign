const signedDocsList = document.getElementById('signedDocsList');
const signedEmptyState = document.getElementById('signedEmptyState');
const signedDocsPerPage = document.getElementById('signedDocsPerPage');
const signedPagination = document.getElementById('signedPagination');
const signedShowingFrom = document.getElementById('signedShowingFrom');
const signedShowingTo = document.getElementById('signedShowingTo');
const signedTotalDocs = document.getElementById('signedTotalDocs');

let currentPage = 1;
let allDocuments = [];

async function loadSignedDocuments() {
    try {
        const response = await fetch('/documents/signed', {
            credentials: 'same-origin'
        });
        const data = await response.json();
        
        if (!data.documents || data.documents.length === 0) {
            signedDocsList.innerHTML = '';
            signedEmptyState.style.display = 'block';
            signedPagination.innerHTML = '';
            updateShowingInfo(0, 0, 0);
            return;
        }
        
        allDocuments = data.documents;
        signedEmptyState.style.display = 'none';
        renderDocuments();
    } catch (error) {
        console.error('Error loading signed documents:', error);
    }
}

function renderDocuments() {
    const perPage = parseInt(signedDocsPerPage.value);
    const start = (currentPage - 1) * perPage;
    const end = start + perPage;
    const pageDocuments = allDocuments.slice(start, end);
    
    updateShowingInfo(start + 1, Math.min(end, allDocuments.length), allDocuments.length);
    renderPagination(Math.ceil(allDocuments.length / perPage));
    
    signedDocsList.innerHTML = pageDocuments.map((doc, index) => {
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
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function renderPagination(totalPages) {
    if (totalPages <= 1) {
        signedPagination.innerHTML = '';
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
    
    signedPagination.innerHTML = pages;
}

function updateShowingInfo(from, to, total) {
    signedShowingFrom.textContent = from;
    signedShowingTo.textContent = to;
    signedTotalDocs.textContent = total;
}

signedDocsPerPage.addEventListener('change', () => {
    currentPage = 1;
    renderDocuments();
});

signedPagination.addEventListener('click', (e) => {
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

document.addEventListener('DOMContentLoaded', loadSignedDocuments);