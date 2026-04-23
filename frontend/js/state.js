export const App = {
  API: (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, ''),
  token: localStorage.getItem('token') || null,
  userEmail: localStorage.getItem('userEmail') || '',
  folders: [],
  activeFolderId: null,
  pollTimer: null,
  authTab: 'login',
};
