/**
 * pipeline.js
 * Backend integration: eel bridge, data loading from JSON files,
 * pipeline modal orchestration.
 *
 * eel.run_pipeline() is the single Python function exposed by web_app.py.
 * It returns: { status: "success", sections_generated, conflicts }
 *          or { status: "error",   message }
 */

const PipelineModule = (() => {

  // ── Helpers ──────────────────────────────────────────────────────────────────
  async function _fetchJSON(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`${path} returned ${res.status}`);
    return res.json();
  }

  // ── Load All JSON Files ───────────────────────────────────────────────────────
  /**
   * Attempts to load schedule.json, report.json, stats.json.
   * Updates AppState and re-renders all pages.
   * Silently ignores 404s (files not yet generated).
   */
  async function loadAllData() {
    try {
      const schedule = await _fetchJSON(CONFIG.SCHEDULE_JSON);
      AppState.schedule = Array.isArray(schedule) ? schedule : [];
    } catch (e) {
      AppState.schedule = [];
      console.log('[UniPlan] schedule.json not ready:', e.message);
    }

    try {
      const report = await _fetchJSON(CONFIG.REPORT_JSON);
      AppState.report = Array.isArray(report) ? report : [];
    } catch (e) {
      AppState.report = [];
      console.log('[UniPlan] report.json not ready:', e.message);
    }

    try {
      const stats = await _fetchJSON(CONFIG.STATS_JSON);
      AppState.stats = stats || null;
    } catch (e) {
      AppState.stats = null;
      console.log('[UniPlan] stats.json not ready:', e.message);
    }

    _refreshAllPages();
  }

  // ── Refresh All Pages After Data Load ────────────────────────────────────────
  function _refreshAllPages() {
    DashboardModule.render(AppState.stats, AppState.schedule);
    ScheduleModule.init(AppState.schedule);
    ScheduleModule.renderQuickStats(AppState.schedule);
    ReportModule.init(AppState.report);
    AnalyticsModule.render(AppState.schedule, AppState.stats);
  }

  // ── Run Full Pipeline ─────────────────────────────────────────────────────────
  /**
   * Calls eel.run_pipeline() (Python), shows animated modal while running,
   * then reloads all JSON data on success.
   *
   * eel syntax: await eel.function_name()()  ← double parens required
   */
  async function runPipeline() {
    _openModal();
    _startStepAnimation();

    let result;
    try {
      // Check eel is available (running inside eel, not standalone browser)
      if (typeof eel === 'undefined') {
        throw new Error('eel is not available. Run the app via web_app.py.');
      }
      result = await eel.run_pipeline()();
    } catch (e) {
      _showModalError(e.message || 'Unknown error calling backend.');
      return;
    }

    _stopStepAnimation();

    if (!result || result.status !== 'success') {
      _showModalError(result?.message || 'Pipeline returned an error.');
      return;
    }

    // Mark all steps done
    _markAllStepsDone();

    document.getElementById('modal-progress-bar').style.width  = '100%';
    document.getElementById('modal-pct').textContent            = '100%';
    document.getElementById('modal-step-label').textContent     = '✓ Schedule Generated Successfully';
    document.getElementById('modal-status').textContent =
      `✓ ${result.sections_generated} sections generated · 0 conflicts`;

    document.getElementById('spinner-svg').classList.remove('spinner');
    document.getElementById('modal-done').classList.remove('hidden');

    // Load fresh data
    await loadAllData();
  }

  // ── Modal Orchestration ───────────────────────────────────────────────────────
  function _openModal() {
    const modal = document.getElementById('processing-modal');
    if (!modal) return;
    modal.classList.remove('hidden');
    modal.style.display = 'flex';

    // Reset UI
    document.getElementById('modal-done')?.classList.add('hidden');
    document.getElementById('modal-error-box')?.classList.add('hidden');
    document.getElementById('spinner-svg')?.classList.add('spinner');
    document.getElementById('modal-progress-bar').style.width = '0%';
    document.getElementById('modal-pct').textContent          = '0%';
    document.getElementById('modal-step-label').textContent   = 'Initializing…';
    document.getElementById('modal-status').textContent       = 'Connecting to SQL Server…';

    // Reset all step icons
    PIPELINE_STEPS.forEach((_, i) => _resetStepIcon(i));
  }

  function closeModal() {
    const modal = document.getElementById('processing-modal');
    if (!modal) return;
    modal.style.display = 'none';
    modal.classList.add('hidden');
    showPage('schedule');
  }

  // Animated step cycling — simulates progress while eel runs in background
  let _stepInterval  = null;
  let _stepIdx       = 0;
  let _msgIdx        = 0;

  function _startStepAnimation() {
    _stepIdx = 0;
    _msgIdx  = 0;
    _advanceStep();
  }

  function _advanceStep() {
    if (_stepIdx >= PIPELINE_STEPS.length) return;

    const step = PIPELINE_STEPS[_stepIdx];
    const pct  = Math.round((_stepIdx / PIPELINE_STEPS.length) * 90); // reserve 10% for final

    document.getElementById('modal-progress-bar').style.width = pct + '%';
    document.getElementById('modal-pct').textContent           = pct + '%';
    document.getElementById('modal-step-label').textContent    = step.label + '…';

    // Mark previous steps done
    for (let i = 0; i < _stepIdx; i++) _markStepDone(i);
    _markStepActive(_stepIdx);

    _msgIdx = 0;
    _stepInterval = setInterval(() => {
      const msg = step.msgs[_msgIdx] || step.msgs[step.msgs.length - 1];
      document.getElementById('modal-status').textContent = msg;
      _msgIdx++;

      if (_msgIdx >= step.msgs.length) {
        clearInterval(_stepInterval);
        _stepIdx++;
        // Move to next step after brief pause
        setTimeout(_advanceStep, 300);
      }
    }, 550);
  }

  function _stopStepAnimation() {
    if (_stepInterval) { clearInterval(_stepInterval); _stepInterval = null; }
  }

  function _resetStepIcon(i) {
    const icon = document.getElementById(`mstep-icon-${i}`);
    const text = document.getElementById(`mstep-text-${i}`);
    if (icon) {
      icon.innerHTML = `<span class="material-symbols-outlined text-sm text-on-surface-variant">radio_button_unchecked</span>`;
      icon.className = 'w-7 h-7 rounded-full bg-surface-container-low flex items-center justify-center flex-shrink-0';
    }
    if (text) text.className = 'text-on-surface-variant';
  }

  function _markStepDone(i) {
    const icon = document.getElementById(`mstep-icon-${i}`);
    const text = document.getElementById(`mstep-text-${i}`);
    if (icon) {
      icon.innerHTML = `<span class="material-symbols-outlined text-sm text-white">check</span>`;
      icon.className = 'w-7 h-7 rounded-full bg-emerald-500 flex items-center justify-center flex-shrink-0';
    }
    if (text) text.className = 'text-on-surface font-semibold';
  }

  function _markStepActive(i) {
    const icon = document.getElementById(`mstep-icon-${i}`);
    const text = document.getElementById(`mstep-text-${i}`);
    if (icon) {
      icon.innerHTML = `<div class="w-3 h-3 border-2 border-primary border-t-transparent rounded-full spinner"></div>`;
      icon.className = 'w-7 h-7 rounded-full bg-surface-container-high flex items-center justify-center flex-shrink-0';
    }
    if (text) text.className = 'text-primary font-bold';
  }

  function _markAllStepsDone() {
    PIPELINE_STEPS.forEach((_, i) => _markStepDone(i));
  }

  function _showModalError(msg) {
    _stopStepAnimation();
    document.getElementById('spinner-svg')?.classList.remove('spinner');
    document.getElementById('modal-step-label').textContent = '✕ Pipeline failed';
    document.getElementById('modal-status').textContent     = msg;

    const errBox = document.getElementById('modal-error-box');
    if (errBox) {
      errBox.textContent = msg;
      errBox.classList.remove('hidden');
    }
  }

  // ── Public API ───────────────────────────────────────────────────────────────
  return { runPipeline, loadAllData, closeModal };
})();
