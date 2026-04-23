import { App } from './state.js';
import { logout } from './auth.js';

// JSON API calls
export async function apiFetch(path, opts = {}, auth = true) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth && App.token) headers['Authorization'] = `Bearer ${App.token}`;

  const res = await fetch(App.API + path, {
    method: opts.method || 'GET',
    headers,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });

  if (res.status === 401 && auth) {
    logout();
    throw new Error('Session expired — please sign in again.');
  }

  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try { const j = await res.json(); msg = j.detail || j.msg || msg; } catch { }
    throw new Error(msg);
  }

  if (res.status === 204) return null;
  return res.json();
}

// Multipart file upload (no Content-Type header — browser sets boundary automatically)
export async function uploadFetch(path, formData) {
  const res = await fetch(App.API + path, {
    method: 'POST',
    headers: { Authorization: `Bearer ${App.token}` },
    body: formData,
  });

  if (res.status === 401) {
    logout();
    throw new Error('Session expired — please sign in again.');
  }

  if (!res.ok) {
    let msg = `Upload failed (${res.status})`;
    try { const j = await res.json(); msg = j.detail || msg; } catch { }
    throw new Error(msg);
  }

  return res.json();
}
