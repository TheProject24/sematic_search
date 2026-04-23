import { App } from './state.js';
import { apiFetch } from './api.js';
import { toast } from './utils.js';

export function switchTab(tab) {
  App.authTab = tab;
  document.getElementById('tab-login').classList.toggle('active', tab === 'login');
  document.getElementById('tab-register').classList.toggle('active', tab === 'register');
  document.getElementById('auth-btn').textContent = tab === 'login' ? 'Sign In' : 'Create Account';
  document.getElementById('auth-error').textContent = '';
}

export async function handleAuth() {
  const email = document.getElementById('auth-email').value.trim();
  const password = document.getElementById('auth-password').value;
  const errorEl = document.getElementById('auth-error');
  const btn = document.getElementById('auth-btn');

  if (!email || !password) { errorEl.textContent = 'Email and password required.'; return; }

  btn.disabled = true;
  btn.textContent = 'Please wait...';
  errorEl.textContent = '';

  const path = App.authTab === 'login' ? '/api/v1/auth/login' : '/api/v1/auth/register';

  try {
    const data = await apiFetch(path, { method: 'POST', body: { email, password } }, false);

    if (App.authTab === 'register') {
      toast('Registration successful! Please sign in.');
      switchTab('login');
    } else {
      App.token = data.access_token;
      App.userEmail = email;
      localStorage.setItem('token', App.token);
      localStorage.setItem('userEmail', email);
      showApp();
    }
  } catch (e) {
    errorEl.textContent = e.message || 'Authentication failed.';
  } finally {
    btn.disabled = false;
    btn.textContent = App.authTab === 'login' ? 'Sign In' : 'Create Account';
  }
}

export function logout() {
  App.token = null;
  App.userEmail = '';
  localStorage.removeItem('token');
  localStorage.removeItem('userEmail');
  clearInterval(App.pollTimer);
  App.pollTimer = null;
  location.reload(); // Simplest way to clear state
}

export function showApp() {
  document.getElementById('auth-screen').style.display = 'none';
  document.getElementById('app-screen').style.display = 'block';
  document.getElementById('topbar-email').textContent = App.userEmail;
  import('./folders.js').then(m => m.loadFolders());
}
