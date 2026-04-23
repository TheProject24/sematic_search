import { App } from './state.js';
import { apiFetch } from './api.js';
import { esc } from './utils.js';

export function onChatKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); }
}

export function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

export async function sendChat() {
  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-btn');
  const query = input.value.trim();
  if (!query || !App.activeFolderId) return;

  appendUserMsg(query);
  input.value = '';
  input.style.height = 'auto';
  input.disabled = true;
  sendBtn.disabled = true;

  const thinkingId = appendThinking();

  try {
    const data = await apiFetch(`/api/v2/chat/${App.activeFolderId}`, {
      method: 'POST',
      body: { query },
    });
    removeThinking(thinkingId);
    appendAssistantMsg(data.answer, data.context || []);
  } catch (e) {
    removeThinking(thinkingId);
    appendAssistantMsg('⚠️ ' + (e.message || 'Something went wrong.'), []);
  } finally {
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

export function appendUserMsg(text) {
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'msg user';
  div.innerHTML = `
    <div class="msg-avatar">👤</div>
    <div class="msg-body"><div class="msg-bubble">${esc(text)}</div></div>
  `;
  container.appendChild(div);
  scrollChat();
}

export function appendAssistantMsg(text, context) {
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'msg assistant';

  const sources = [...new Set(context.map(c => c.source).filter(Boolean))];

  const sourcesHTML = sources.length
    ? `<div class="msg-sources">
         <span class="msg-sources-label">Sources:</span>
         ${sources.map(s =>
      `<button class="source-chip" data-source="${esc(s)}" title="Jump to retrieved chunk">📄 ${esc(s)}</button>`
    ).join('')}
       </div>`
    : '';

  const snippetsHTML = context.length
    ? `<div class="msg-context">
         <button class="msg-context-toggle">
           ▶ Show ${context.length} retrieved chunk${context.length !== 1 ? 's' : ''}
         </button>
         <div class="msg-context-snippets">
           ${context.map(c => `
             <div class="snippet" data-source="${esc(c.source)}">
               <div class="snippet-source">📄 ${esc(c.source)}</div>
               <div class="snippet-text">${esc(c.text)}</div>
             </div>
           `).join('')}
         </div>
       </div>`
    : '';

  div.innerHTML = `
    <div class="msg-avatar">🤖</div>
    <div class="msg-body">
      <div class="msg-bubble">${esc(text)}</div>
      ${sourcesHTML}
      ${snippetsHTML}
    </div>
  `;

  div.querySelectorAll('.source-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const src = chip.dataset.source;
      const toggle = div.querySelector('.msg-context-toggle');
      const snippetsEl = div.querySelector('.msg-context-snippets');
      if (!toggle || !snippetsEl) return;

      openSnippets(toggle, snippetsEl);

      const target = [...snippetsEl.querySelectorAll('.snippet')]
        .find(s => s.dataset.source === src);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
  });

  const toggle = div.querySelector('.msg-context-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const snippetsEl = div.querySelector('.msg-context-snippets');
      toggleSnippets(toggle, snippetsEl);
    });
  }

  container.appendChild(div);
  scrollChat();
}

export function openSnippets(toggle, snippetsEl) {
  if (snippetsEl.classList.contains('open')) return;
  snippetsEl.classList.add('open');
  const n = snippetsEl.querySelectorAll('.snippet').length;
  toggle.textContent = `▼ Hide ${n} retrieved chunk${n !== 1 ? 's' : ''}`;
  scrollChat();
}

export function toggleSnippets(toggle, snippetsEl) {
  const open = snippetsEl.classList.toggle('open');
  const n = snippetsEl.querySelectorAll('.snippet').length;
  toggle.textContent = `${open ? '▼ Hide' : '▶ Show'} ${n} retrieved chunk${n !== 1 ? 's' : ''}`;
  if (open) scrollChat();
}

export function appendThinking() {
  const container = document.getElementById('chat-messages');
  const id = 'thinking-' + Date.now();
  const div = document.createElement('div');
  div.className = 'msg assistant';
  div.id = id;
  div.innerHTML = `
    <div class="msg-avatar">🤖</div>
    <div class="msg-thinking"><span></span><span></span><span></span></div>
  `;
  container.appendChild(div);
  scrollChat();
  return id;
}

export function removeThinking(id) {
  document.getElementById(id)?.remove();
}

export function scrollChat() {
  const c = document.getElementById('chat-messages');
  c.scrollTop = c.scrollHeight;
}
