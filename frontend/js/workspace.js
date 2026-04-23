import { App } from './state.js';
import { apiFetch } from './api.js';
import { esc } from './utils.js';
import { renderFolders } from './folders.js';

export async function selectFolder(id, name) {
  App.activeFolderId = id;
  document.getElementById('workspace-folder-name').textContent = name;
  document.getElementById('no-folder').style.display = 'none';
  document.getElementById('folder-workspace').style.display = 'flex';
  document.getElementById('chat-messages').innerHTML = '';
  document.getElementById('chat-input').value = '';

  renderFolders();
  clearInterval(App.pollTimer);
  App.pollTimer = null;

  await loadDocuments();
  startDocPoll();
}

export async function loadDocuments() {
  if (!App.activeFolderId) return;
  try {
    const docs = await apiFetch(`/api/v1/folders/${App.activeFolderId}/documents`);
    renderDocs(docs);

    const folder = App.folders.find(f => f.id === App.activeFolderId);
    if (folder && folder.doc_count !== docs.length) {
      folder.doc_count = docs.length;
      renderFolders();
    }

    const anyProcessing = docs.some(d => d.status === 'processing');
    if (!anyProcessing && App.pollTimer) {
      clearInterval(App.pollTimer);
      App.pollTimer = null;
    }
  } catch { /* ignore transient errors */ }
}

export function renderDocs(docs) {
  const el = document.getElementById('doc-list');
  if (!docs.length) {
    el.innerHTML = '<span class="doc-empty">No documents yet.</span>';
    return;
  }
  el.innerHTML = docs.map(d => `
    <div class="doc-chip" title="${esc(d.filename)} — ${d.status || 'processing'}">
      <div class="doc-status status-${d.status || 'processing'}"></div>
      <span class="doc-name">${esc(d.filename)}</span>
    </div>
  `).join('');
}

export function startDocPoll() {
  App.pollTimer = setInterval(loadDocuments, 4000);
}
