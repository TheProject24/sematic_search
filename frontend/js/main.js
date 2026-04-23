import { App } from './state.js';
import { switchTab, handleAuth, logout, showApp } from './auth.js';
import { openNewFolderModal, closeNewFolderModal, createFolder, deleteFolder } from './folders.js';
import { selectFolder } from './workspace.js';
import { onDragOver, onDragLeave, onDrop, handleFileSelect } from './upload.js';
import { onChatKey, sendChat, autoResize } from './chat.js';

document.addEventListener('DOMContentLoaded', () => {

  // ── Auth ──────────────────────────────────────────────────
  document.getElementById('tab-login')
    .addEventListener('click', () => switchTab('login'));
  document.getElementById('tab-register')
    .addEventListener('click', () => switchTab('register'));
  document.getElementById('auth-btn')
    .addEventListener('click', handleAuth);
  document.getElementById('auth-email')
    .addEventListener('keydown', e => { if (e.key === 'Enter') handleAuth(); });
  document.getElementById('auth-password')
    .addEventListener('keydown', e => { if (e.key === 'Enter') handleAuth(); });

  // ── Topbar ────────────────────────────────────────────────
  document.getElementById('logout-btn')
    .addEventListener('click', logout);

  // ── Sidebar: new folder button ────────────────────────────
  document.getElementById('new-folder-btn')
    .addEventListener('click', openNewFolderModal);

  // ── Sidebar: event delegation for folder items + delete ───
  document.getElementById('folder-list').addEventListener('click', e => {
    const deleteBtn = e.target.closest('[data-action="delete"]');
    const folderItem = e.target.closest('.folder-item');

    if (deleteBtn) {
      e.stopPropagation();
      deleteFolder(deleteBtn.dataset.id, deleteBtn.dataset.name);
      return;
    }

    if (folderItem) {
      selectFolder(folderItem.dataset.id, folderItem.dataset.name);
    }
  });

  document.getElementById('folder-list').addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') {
      const folderItem = e.target.closest('.folder-item');
      if (folderItem) {
        e.preventDefault();
        selectFolder(folderItem.dataset.id, folderItem.dataset.name);
      }
    }
  });

  // ── New folder modal ──────────────────────────────────────
  document.getElementById('modal-cancel-btn')
    .addEventListener('click', closeNewFolderModal);
  document.getElementById('modal-create-btn')
    .addEventListener('click', createFolder);
  document.getElementById('new-folder-name')
    .addEventListener('keydown', e => {
      if (e.key === 'Enter') createFolder();
      if (e.key === 'Escape') closeNewFolderModal();
    });
  document.getElementById('modal-overlay')
    .addEventListener('click', e => {
      if (e.target === e.currentTarget) closeNewFolderModal();
    });

  // ── Upload zone ───────────────────────────────────────────
  document.getElementById('upload-zone')
    .addEventListener('click', () => document.getElementById('file-input').click());
  document.getElementById('upload-zone')
    .addEventListener('dragover', onDragOver);
  document.getElementById('upload-zone')
    .addEventListener('dragleave', onDragLeave);
  document.getElementById('upload-zone')
    .addEventListener('drop', onDrop);
  document.getElementById('file-input')
    .addEventListener('change', handleFileSelect);

  // ── Chat ──────────────────────────────────────────────────
  document.getElementById('send-btn')
    .addEventListener('click', sendChat);
  document.getElementById('chat-input')
    .addEventListener('keydown', onChatKey);
  document.getElementById('chat-input')
    .addEventListener('input', function () { autoResize(this); });

  // ── Bootstrap ─────────────────────────────────────────────
  if (App.token) showApp();
});
