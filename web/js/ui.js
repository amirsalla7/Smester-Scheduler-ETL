/**
 * ui.js
 * Pure UI helpers: navigation, formatting, toast, modal DOM management,
 * day chip rendering, reason badge rendering, and empty-state rendering.
 * No data fetching or business logic here.
 */

// ─── PAGE NAVIGATION ──────────────────────────────────────────────────────────
const ALL_PAGES = ['dashboard', 'schedule', 'reports', 'analytics', 'actions'];

function showPage(page) {
  ALL_PAGES.forEach(p => {
    const el = document.getElementById('content-' + p);
    if (el) el.classList.add('hidden');
  });

  const target = document.getElementById('content-' + page);
  if (target) target.classList.remove('hidden');

  document.querySelectorAll('[data-page]').forEach(el => {
    el.classList.toggle('active', el.dataset.page === page);
  });

  AppState.currentPage = page;
  window.scrollTo(0, 0);
}

// ─── TIME FORMATTING ─────────────────────────────────────────────────────────
/**
 * Strips seconds from backend time strings.
 * "08:00:00" → "08:00"
 * "09:30:00" → "09:30"
 */
function formatTime(t) {
  if (!t) return '';
  return String(t).slice(0, 5);
}

// ─── DAY CHIPS ────────────────────────────────────────────────────────────────
/**
 * Renders coloured day-pattern chips matching backend "day" field values.
 * "Sun/Tue"  → navy chips
 * "Mon/Wed"  → light-blue chips
 * anything else → dark chip with raw value
 */
function dayChips(day) {
  if (!day) return '<span class="text-on-surface-variant text-xs">—</span>';

  if (day === 'Sun/Tue') {
    return `<div class="flex gap-1">
      <span class="px-1.5 py-0.5 rounded text-[9px] font-bold chip-st">SUN</span>
      <span class="px-1.5 py-0.5 rounded text-[9px] font-bold chip-st">TUE</span>
    </div>`;
  }
  if (day === 'Mon/Wed') {
    return `<div class="flex gap-1">
      <span class="px-1.5 py-0.5 rounded text-[9px] font-bold chip-mw">MON</span>
      <span class="px-1.5 py-0.5 rounded text-[9px] font-bold chip-mw">WED</span>
    </div>`;
  }
  // Generic fallback for any other pattern (e.g. "Sun/Tue/Thu")
  return `<span class="px-2 py-0.5 rounded text-[9px] font-bold chip-other">${day}</span>`;
}

// ─── REASON BADGES ────────────────────────────────────────────────────────────
/**
 * Maps reason strings from student_summary.py to styled badge HTML.
 * Exact values from backend: "Graduating priority" | "High demand" |
 *   "Normal demand" | "Low demand"
 */
function reasonBadge(reason) {
  const text = String(reason || '').trim();

  if (text === REASON.GRADUATING) {
    return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[9px] font-bold badge-grad uppercase tracking-wider">Graduating Priority</span>`;
  }
  if (text === REASON.HIGH) {
    return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[9px] font-bold badge-high uppercase tracking-wider">High Demand</span>`;
  }
  if (text === REASON.NORMAL) {
    return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[9px] font-bold badge-normal uppercase tracking-wider">Normal Demand</span>`;
  }
  if (text === REASON.LOW) {
    return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[9px] font-bold badge-low uppercase tracking-wider">Low Demand</span>`;
  }
  // Unknown reason fallback
  return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[9px] font-bold badge-low uppercase tracking-wider">${text || '—'}</span>`;
}

// ─── TOAST NOTIFICATION ───────────────────────────────────────────────────────
let _toastTimer = null;

/**
 * @param {string} message
 * @param {'success'|'error'} type
 */
function showToast(message, type = 'success') {
  const toast    = document.getElementById('toast');
  const toastMsg = document.getElementById('toast-msg');
  const toastIcon = document.getElementById('toast-icon');

  if (!toast || !toastMsg) return;

  toastMsg.textContent = message;
  if (toastIcon) {
    toastIcon.textContent = type === 'error' ? 'error' : 'check_circle';
    toastIcon.className = `material-symbols-outlined ${type === 'error' ? 'text-error' : 'text-tertiary-fixed-dim'}`;
  }

  toast.classList.remove('hidden');
  toast.style.display = 'block';

  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => {
    toast.style.display = 'none';
    toast.classList.add('hidden');
  }, 3500);
}

// ─── PDF OPEN ─────────────────────────────────────────────────────────────────
/**
 * Opens the real backend-generated PDF in a new tab.
 * Files live in web/ folder served by eel.
 * @param {'schedule'|'report'} type
 */
function openPDF(type) {
  const path = (type === 'schedule') ? CONFIG.SCHEDULE_PDF : CONFIG.REPORT_PDF;
  window.open(path, '_blank');
  showToast(type === 'schedule' ? 'Opening Schedule PDF…' : 'Opening Report PDF…');
}

// ─── EMPTY STATE ─────────────────────────────────────────────────────────────
/**
 * Renders an empty state with icon, message and optional CTA button.
 * @param {string} containerId  - ID of element to fill
 * @param {string} message      - main message text
 * @param {string} [ctaLabel]   - button label (optional)
 * @param {string} [ctaAction]  - onclick JS string (optional)
 */
function showEmptyState(containerId, message, ctaLabel, ctaAction) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `
    <td colspan="20">
      <div class="empty-state">
        <span class="material-symbols-outlined">inbox</span>
        <p class="text-sm font-semibold text-on-surface-variant">${message}</p>
        ${ctaLabel
          ? `<button onclick="${ctaAction}" class="mt-2 px-5 py-2 bg-primary text-white rounded-xl text-sm font-bold hover:bg-primary-container transition-colors">${ctaLabel}</button>`
          : ''}
      </div>
    </td>`;
}

// ─── PASSWORD TOGGLE ─────────────────────────────────────────────────────────
function togglePassword() {
  const inp  = document.getElementById('login-pass');
  const icon = document.getElementById('eye-icon');
  if (!inp || !icon) return;
  if (inp.type === 'password') {
    inp.type = 'text';
    icon.textContent = 'visibility_off';
  } else {
    inp.type = 'password';
    icon.textContent = 'visibility';
  }
}

// ─── GLOBAL SEARCH ───────────────────────────────────────────────────────────
function globalSearch(val) {
  if (!val) return;
  showPage('schedule');
  const si = document.getElementById('sched-search');
  if (si) {
    si.value = val;
    ScheduleModule.applyFilters();
  }
}
