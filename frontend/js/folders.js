import { App } from './state.js';
import { apiFetch } from './api.js';
import { toast, esc } from './utils.js';
import { selectFolder } from './workspace.js';

export async function loadFolders() {
  try {
    App.folders = await apiFetch('/api/v1/folders');
    renderFolders();
  } catch (e) {
    if (!e.message.startsWith('Session expired')) toast('Could not load folders.');
  }
}

export function renderFolders() {
  const el = document.getElementById('folder-list');
  if (!App.folders.length) {
    el.innerHTML = '<p class="empty-hint">No folders yet. Hit + to create one.</p>';
    return;
  }
  el.innerHTML = App.folders.map(f => `
    <div class="folder-item ${f.id === App.activeFolderId ? 'active' : ''}"
         data-id="${f.id}" data-name="${esc(f.name)}" role="button" tabindex="0">
      <span class="folder-icon">📁</span>
      <div class="folder-meta">
        <div class="folder-name">${esc(f.name)}</div>
        <div class="folder-count">${f.doc_count ?? 0} doc${(f.doc_count ?? 0) !== 1 ? 's' : ''}</div>
      </div>
      <button class="folder-delete" data-action="delete" data-id="${f.id}" data-name="${esc(f.name)}"
              title="Delete folder" aria-label="Delete ${esc(f.name)}">✕</button>
    </div>
  `).join('');
}

export function openNewFolderModal() {
  document.getElementById('new-folder-name').value = '';
  document.getElementById('folder-modal-error').textContent = '';
  document.getElementById('modal-overlay').classList.add('open');
  setTimeout(() => document.getElementById('new-folder-name').focus(), 60);
}

export function closeNewFolderModal() {
  document.getElementById('modal-overlay').classList.remove('open');
}

export async function createFolder() {
  const input = document.getElementById('new-folder-name');
  const errEl = document.getElementById('folder-modal-error');
  const btn = document.getElementById('modal-create-btn');
  const name = input.value.trim();

  if (!name) { errEl.textContent = 'Name is required.'; input.focus(); return; }

  btn.disabled = true;
  btn.textContent = 'Creating…';
  errEl.textContent = '';

  try {
    const f = await apiFetch('/api/v1/folders', { method: 'POST', body: { name } });
    App.folders.push({ id: f.id, name: f.name, doc_count: 0 });
    renderFolders();
    closeNewFolderModal();
    toast(`Folder "${name}" created.`);
  } catch (e) {
    errEl.textContent = e.message || 'Failed to create folder.';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create';
  }
}

export async function deleteFolder(id, name) {
  if (!confirm(`Delete "${name}" and all its documents?\nThis cannot be undone.`)) return;
  try {
    await apiFetch(`/api/v1/folders/${id}`, { method: 'DELETE' });
    App.folders = App.folders.filter(f => f.id !== id);

    if (App.activeFolderId === id) {
      App.activeFolderId = null;
      clearInterval(App.pollTimer);
      App.pollTimer = null;
      document.getElementById('folder-workspace').style.display = 'none';
      document.getElementById('no-folder').style.display = 'flex';
    }

    renderFolders();
    toast('Folder deleted.');
  } catch (e) {
    toast(e.message || 'Failed to delete folder.');
  }
}
