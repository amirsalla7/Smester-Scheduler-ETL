/**
 * app.js
 * Application entry point: AppState, login/logout, initialization.
 * Must be loaded LAST (after all modules).
 */

// ─── GLOBAL STATE ─────────────────────────────────────────────────────────────
const AppState = {
  schedule:    [],
  report:      [],
  stats:       null,
  isLoggedIn:  false,
  currentPage: 'dashboard',
};

// ─── CREDENTIALS (change these to whatever you want) ─────────────────────────
const VALID_USER = 'admin';
const VALID_PASS = 'admin123';

// ─── LOGIN ────────────────────────────────────────────────────────────────────
function doLogin() {
  const u     = (document.getElementById('login-user')?.value || '').trim();
  const p     = (document.getElementById('login-pass')?.value || '').trim();
  const errEl = document.getElementById('login-error');

  // Clear previous error
  if (errEl) errEl.classList.add('hidden');

  // Empty fields check
  if (!u || !p) {
    if (errEl) {
      errEl.textContent = 'Please enter your username and password.';
      errEl.classList.remove('hidden');
    }
    return;
  }

  // Wrong credentials check
  if (u !== VALID_USER || p !== VALID_PASS) {
    if (errEl) {
      errEl.textContent = `Invalid credentials. Use: ${VALID_USER} / ${VALID_PASS}`;
      errEl.classList.remove('hidden');
    }
    return;
  }

  // ✓ Correct — proceed
  AppState.isLoggedIn = true;

  const loginPage = document.getElementById('page-login');
  const appShell  = document.getElementById('app-shell');

  if (loginPage) loginPage.style.display = 'none';
  if (appShell)  appShell.classList.remove('hidden');

  _initApp();
}

// ─── LOGOUT ───────────────────────────────────────────────────────────────────
function doLogout() {
  AppState.isLoggedIn = false;
  AppState.schedule   = [];
  AppState.report     = [];
  AppState.stats      = null;

  const loginPage = document.getElementById('page-login');
  const appShell  = document.getElementById('app-shell');
  if (loginPage) loginPage.style.display = 'flex';
  if (appShell)  appShell.classList.add('hidden');

  const u = document.getElementById('login-user');
  const p = document.getElementById('login-pass');
  if (u) u.value = '';
  if (p) p.value = '';
}

// ─── INIT ─────────────────────────────────────────────────────────────────────
async function _initApp() {
  showPage('dashboard');

  // Guard: PipelineModule might not be loaded if a JS file failed
  if (typeof PipelineModule === 'undefined') {
    console.error('PipelineModule not found. Check that pipeline.js loaded correctly.');
    return;
  }

  try {
    await PipelineModule.loadAllData();
  } catch (e) {
    console.warn('Could not load JSON files on startup (not yet generated):', e.message);
  }
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
    const modal   = document.getElementById('processing-modal');
    const doneBtn = document.getElementById('modal-done');
    if (modal && modal.style.display !== 'none') {
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