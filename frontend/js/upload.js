import { App } from './state.js';
import { uploadFetch, apiFetch } from './api.js';
import { esc, toast } from './utils.js';
import { loadDocuments, startDocPoll } from './workspace.js';

export function onDragOver(e) {
  e.preventDefault();
  document.getElementById('upload-zone').classList.add('dragover');
}

export function onDragLeave() {
  document.getElementById('upload-zone').classList.remove('dragover');
}

export function onDrop(e) {
  e.preventDefault();
  onDragLeave();
  const file = e.dataTransfer.files[0];
  if (file) uploadFile(file);
}

export function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) uploadFile(file);
  e.target.value = '';
}

export async function uploadFile(file) {
  if (!App.activeFolderId) { toast('Select a folder first.'); return; }
  if (!file.name.toLowerCase().endsWith('.pdf')) { toast('Only PDF files are supported.'); return; }

  const zone = document.getElementById('upload-zone');
  const savedHTML = zone.innerHTML;

  zone.classList.add('uploading');
  zone.innerHTML = `
    <span class="upload-spinner"></span>
    <div class="upload-text">
      <strong>Uploading</strong> <span class="upload-filename">${esc(file.name)}</span>
    </div>
  `;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const data = await uploadFetch(`/api/v2/upload/${App.activeFolderId}`, formData);
    toast(`"${file.name}" uploaded. Processing...`);

    await loadDocuments();
    pollDocumentStatus(data.document_id, file.name);
    if (!App.pollTimer) startDocPoll();

  } catch (e) {
    toast(e.message || 'Upload failed.');
  } finally {
    zone.innerHTML = savedHTML;
    zone.classList.remove('uploading');
  }
}

export async function pollDocumentStatus(docId, filename) {
  const maxAttempts = 30;
  let attempts = 0;

  const interval = setInterval(async () => {
    attempts++;
    try {
      const data = await apiFetch(`/api/v2/status/${docId}`);
      if (data.status === 'completed') {
        clearInterval(interval);
        toast(`✅ "${filename}" is ready for search.`);
        await loadDocuments();
      } else if (data.status.startsWith('error')) {
        clearInterval(interval);
        toast(`❌ Error processing "${filename}": ${data.status}`);
        await loadDocuments();
      }
    } catch (e) {
      console.error('Polling error:', e);
    }

    if (attempts >= maxAttempts) {
      clearInterval(interval);
      console.warn(`Stopped polling for ${filename} after max attempts.`);
    }
  }, 4000);
}
