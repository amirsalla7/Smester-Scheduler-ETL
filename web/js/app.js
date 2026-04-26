/**
 * app.js
 * Application entry point: AppState, login/logout, initialization.
 * Must be loaded LAST (after all modules).
 */

// ─── GLOBAL STATE ─────────────────────────────────────────────────────────────
const AppState = {
  schedule: [],
  report: [],
  stats: null,
  isLoggedIn: false,
  currentPage: 'dashboard',
};

// ─── LOAD RESOURCES ───────────────────────────────────────────────────────────
async function loadAvailableResources() {
  try {
    const resources = await eel.get_available_resources()();
    ScheduleModule.setResources(resources);
    console.log("Resources loaded:", resources);
  } catch (err) {
    console.error("Failed to load resources:", err);
  }
}

// ─── INIT ─────────────────────────────────────────────────────────────────────
async function _initApp() {
  showPage('dashboard');
  await loadAvailableResources();
  await PipelineModule.loadAllData();
}

// ─── LOGIN ────────────────────────────────────────────────────────────────────
async function doLogin() {
  const u = (document.getElementById('login-user')?.value || '').trim();
  const p = (document.getElementById('login-pass')?.value || '').trim();
  const errEl = document.getElementById('login-error');

  const validUser = u.length > 0;
  const validPass = p.length > 0;

  if (!validUser || !validPass) {
    if (errEl) errEl.classList.remove('hidden');
    return;
  }

  if (errEl) errEl.classList.add('hidden');
  AppState.isLoggedIn = true;

  const loginPage = document.getElementById('page-login');
  const appShell = document.getElementById('app-shell');

  if (loginPage) loginPage.style.display = 'none';
  if (appShell) appShell.classList.remove('hidden');

  await _initApp();
}

function doLogout() {
  AppState.isLoggedIn = false;

  const loginPage = document.getElementById('page-login');
  const appShell = document.getElementById('app-shell');

  if (loginPage) loginPage.style.display = 'flex';
  if (appShell) appShell.classList.add('hidden');

  const u = document.getElementById('login-user');
  const p = document.getElementById('login-pass');

  if (u) u.value = '';
  if (p) p.value = '';

  AppState.schedule = [];
  AppState.report = [];
  AppState.stats = null;
}

// ─── KEYBOARD SHORTCUTS ───────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    const loginPage = document.getElementById('page-login');
    if (loginPage && loginPage.style.display !== 'none') {
      doLogin();
    }
  }

  if (e.key === 'Escape') {
    const modal = document.getElementById('processing-modal');
    if (modal && modal.style.display !== 'none') {
      const doneBtn = document.getElementById('modal-done');
      if (doneBtn && !doneBtn.classList.contains('hidden')) {
        PipelineModule.closeModal();
      }
    }
  }
});

// ─── DOMContentLoaded ─────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  const loginPage = document.getElementById('page-login');
  if (loginPage) loginPage.style.display = 'flex';
});

