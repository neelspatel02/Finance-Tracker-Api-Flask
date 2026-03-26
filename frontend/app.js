const API = '';

async function apiFetch(path, options = {}) {
  const res = await fetch(API + path, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options
  });
  const data = await res.json();
  if (!res.ok) throw { status: res.status, message: data.message || 'Error' };
  return data;
}

function toast(msg, type = 'success') {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    el.className = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.className = `toast ${type} show`;
  setTimeout(() => el.classList.remove('show'), 3000);
}

function formatRupees(val) {
  const n = parseFloat(val);
  if (isNaN(n)) return '0.00';
  return n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function getUser() {
  return JSON.parse(localStorage.getItem('pft_user') || 'null');
}

function setUser(user) {
  localStorage.setItem('pft_user', JSON.stringify(user));
}

function clearUser() {
  localStorage.removeItem('pft_user');
}

function requireAuth() {
  const user = getUser();
  if (!user) { window.location.href = 'index.html'; return null; }
  return user;
}

function renderSidebar(activePage) {
  const user = getUser();
  const pages = [
    { id: 'dashboard', label: 'Dashboard', href: 'dashboard.html', icon: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="1" width="6" height="6" rx="1"/><rect x="9" y="1" width="6" height="6" rx="1"/><rect x="1" y="9" width="6" height="6" rx="1"/><rect x="9" y="9" width="6" height="6" rx="1"/></svg>` },
    { id: 'transactions', label: 'Transactions', href: 'transactions.html', icon: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 5h12M2 8h8M2 11h5"/></svg>` },
    { id: 'categories', label: 'Categories', href: 'categories.html', icon: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="5" cy="5" r="3"/><circle cx="11" cy="11" r="3"/><path d="M8 2h6M2 8h3"/></svg>` },
    { id: 'analysis', label: 'Analysis', href: 'analysis.html', icon: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 12l3-4 3 2 3-5 3 2"/></svg>` },
  ];

  return `
  <aside class="sidebar">
    <div class="sidebar-logo">
      <div class="logo-text">PFT</div>
      <div class="logo-sub">personal finance tracker</div>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-label">Menu</div>
      ${pages.map(p => `
        <a href="${p.href}" class="nav-item ${activePage === p.id ? 'active' : ''}">
          <span class="nav-icon">${p.icon}</span>
          ${p.label}
        </a>
      `).join('')}
    </nav>
    <div class="sidebar-footer">
      <div class="user-badge">
        <div class="user-avatar">${user ? user.username[0].toUpperCase() : '?'}</div>
        <span class="user-name">${user ? user.username : ''}</span>
        <button class="logout-btn" onclick="handleLogout()" title="Logout">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M6 2H3a1 1 0 00-1 1v10a1 1 0 001 1h3M10 11l3-3-3-3M13 8H6"/>
          </svg>
        </button>
      </div>
    </div>
  </aside>`;
}

async function handleLogout() {
  try {
    await apiFetch('/api/auth/logout', { method: 'POST' });
  } catch(e) {}
  clearUser();
  window.location.href = 'index.html';
}
