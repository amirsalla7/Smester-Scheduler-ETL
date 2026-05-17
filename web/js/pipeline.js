/**
 * pipeline.js  —  updated
 * New in this version:
 *   • saveEdits()  — validates + persists the edited schedule via eel
 */

const PipelineModule = (() => {

  // ── JSON Loaders ───────────────────────────────────────────────────────────
  async function _fetchJSON(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`${path} returned ${res.status}`);
    return res.json();
  }

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

  function _refreshAllPages() {
    DashboardModule.render(AppState.stats, AppState.schedule);
    ScheduleModule.init(AppState.schedule);
    ScheduleModule.renderQuickStats(AppState.schedule);
    ReportModule.init(AppState.report);
    AnalyticsModule.render(AppState.schedule, AppState.stats);
  }

  // ── Run Full Pipeline ──────────────────────────────────────────────────────
  let _isRunning = false;

  async function runPipeline() {
    // Prevent double-clicks / re-entry while Python is still working
    if (_isRunning) {
      showToast('Pipeline is already running. Please wait.', 'error');
      return;
    }
    _isRunning = true;

    _openModal();
    _startStepAnimation();

    let result;
    try {
      if (typeof eel === 'undefined')
        throw new Error('eel is not available. Run the app via web_app.py.');
      result = await eel.run_pipeline()();
    } catch (e) {
      _isRunning = false;
      _stopStepAnimation();
      _showModalError(e.message || 'Unknown error calling backend.');
      return;
    }
    _isRunning = false;

    _stopStepAnimation();

    if (!result || result.status !== 'success') {
      _showModalError(result?.message || 'Pipeline returned an error.', result?.failed_step);
      return;
    }

    if (!result.sections_generated || result.sections_generated === 0) {
      _showModalError('No sections were generated. The API server may be offline or the database has no data.');
      return;
    }

    _markAllStepsDone();
    document.getElementById('modal-progress-bar').style.width = '100%';
    document.getElementById('modal-pct').textContent           = '100%';
    document.getElementById('modal-step-label').textContent    = '✓ Schedule Generated Successfully';
    document.getElementById('modal-status').textContent =
      `✓ ${result.sections_generated} sections generated · 0 conflicts`;
    document.getElementById('spinner-svg')?.classList.remove('spinner');
    const doneBtn = document.getElementById('modal-done');
    if (doneBtn) {
      const btn = doneBtn.querySelector('button');
      if (btn) btn.textContent = 'View Schedule →';
      doneBtn.classList.remove('hidden');
    }

    await loadAllData();
  }

  // ── Save Edited Schedule ───────────────────────────────────────────────────
  /**
   * Called by the Save Changes button in the save bar.
   * Flow:
   *   1. Get the full schedule with pending edits merged in
   *   2. Call eel.save_schedule_edits() — backend validates + saves
   *   3. On success → reload all JSON data → refresh all pages
   *   4. On conflict → show conflicts panel in the schedule page
   */
  async function saveEdits() {
    if (!ScheduleModule.hasEdits()) {
      showToast('No changes to save.', 'error');
      return;
    }

    const editedSchedule = ScheduleModule.getEditedSchedule();

    // Update save button state
    const saveBtn = document.getElementById('save-bar-save-btn');
    if (saveBtn) { saveBtn.disabled = true; saveBtn.textContent = 'Saving…'; }

    // Clear previous conflicts
    ScheduleModule.hideConflicts();

    try {
      if (typeof eel === 'undefined')
        throw new Error('eel is not available. Run via web_app.py.');

      const result = await eel.save_schedule_edits(editedSchedule)();

      if (result.status === 'success') {
        await loadAllData();               // reloads and re-renders everything
        showToast('Schedule saved! PDFs regenerated.', 'success');
      } else {
        showToast(result.message || 'Save failed — see conflicts below.', 'error');
        if (result.conflicts?.length) {
          showPage('schedule');
          ScheduleModule.showConflicts(result.conflicts);
        }
      }
    } catch (e) {
      showToast('Error: ' + e.message, 'error');
    } finally {
      if (saveBtn) {
        saveBtn.disabled    = false;
        saveBtn.textContent = '';
        saveBtn.innerHTML   = `<span class="flex items-center gap-2">
          <span class="material-symbols-outlined text-[18px]">save</span>
          Save Changes
        </span>`;
      }
    }
  }

  // ── Close Modal ────────────────────────────────────────────────────────────
  function closeModal() {
    const modal = document.getElementById('processing-modal');
    if (modal) { modal.style.display = 'none'; modal.classList.add('hidden'); }
    showPage('schedule');
  }

  // ── Modal Helpers ──────────────────────────────────────────────────────────
  function _openModal() {
    const modal = document.getElementById('processing-modal');
    if (!modal) return;
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    document.getElementById('modal-done')?.classList.add('hidden');
    document.getElementById('modal-error-box')?.classList.add('hidden');
    document.getElementById('spinner-svg')?.classList.add('spinner');
    document.getElementById('modal-progress-bar').style.width            = '0%';
    document.getElementById('modal-progress-bar').style.backgroundColor = '';
    document.getElementById('modal-pct').textContent                     = '0%';
    document.getElementById('modal-step-label').textContent   = 'Initializing…';
    document.getElementById('modal-status').textContent       = 'Connecting to SQL Server…';
    PIPELINE_STEPS.forEach((_, i) => _resetStepIcon(i));
  }

  let _stepInterval    = null;
  let _stepIdx         = 0;
  let _msgIdx          = 0;
  let _animationStopped = false;

  function _startStepAnimation() {
    _stepIdx = 0; _msgIdx = 0;
    _animationStopped = false;
    _advanceStep();
  }

  function _advanceStep() {
    if (_animationStopped) return;
    if (_stepIdx >= PIPELINE_STEPS.length) return;
    const step = PIPELINE_STEPS[_stepIdx];
    const pct  = Math.round((_stepIdx / PIPELINE_STEPS.length) * 90);
    document.getElementById('modal-progress-bar').style.width = pct + '%';
    document.getElementById('modal-pct').textContent           = pct + '%';
    document.getElementById('modal-step-label').textContent    = step.label + '…';
    for (let i = 0; i < _stepIdx; i++) _markStepDone(i);
    _markStepActive(_stepIdx);
    _msgIdx = 0;
    _stepInterval = setInterval(() => {
      if (_animationStopped) { clearInterval(_stepInterval); return; }
      const msg = step.msgs[_msgIdx] || step.msgs[step.msgs.length - 1];
      document.getElementById('modal-status').textContent = msg;
      _msgIdx++;
      if (_msgIdx >= step.msgs.length) {
        clearInterval(_stepInterval);
        _stepIdx++;
        setTimeout(() => { if (!_animationStopped) _advanceStep(); }, 300);
      }
    }, 550);
  }

  function _stopStepAnimation() {
    _animationStopped = true;
    if (_stepInterval) { clearInterval(_stepInterval); _stepInterval = null; }
  }

  function _resetStepIcon(i) {
    const icon = document.getElementById(`mstep-icon-${i}`);
    const text = document.getElementById(`mstep-text-${i}`);
    if (icon) {
      icon.innerHTML  = `<span class="material-symbols-outlined text-sm text-on-surface-variant">radio_button_unchecked</span>`;
      icon.className  = 'w-7 h-7 rounded-full bg-surface-container-low flex items-center justify-center flex-shrink-0';
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

  function _showModalError(msg, failAtStep) {
    _stopStepAnimation();
    // Stop the app-icon spinner
    document.getElementById('spinner-svg')?.classList.remove('spinner');
    // Use failAtStep if provided, otherwise use current animation step (clamped)
    const fi = (failAtStep !== undefined && failAtStep !== null)
      ? failAtStep
      : Math.min(_stepIdx, PIPELINE_STEPS.length - 1);
    // Mark steps before the failing one green, failing one red, rest reset
    PIPELINE_STEPS.forEach((_, i) => {
      const icon = document.getElementById(`mstep-icon-${i}`);
      const text = document.getElementById(`mstep-text-${i}`);
      if (!icon) return;
      if (i < fi) {
        _markStepDone(i);
      } else if (i === fi) {
        icon.innerHTML = `<span class="material-symbols-outlined text-sm text-white">close</span>`;
        icon.className = 'w-7 h-7 rounded-full bg-red-500 flex items-center justify-center flex-shrink-0';
        if (text) text.className = 'text-red-500 font-bold';
      } else {
        _resetStepIcon(i);
      }
    });
    document.getElementById('modal-progress-bar').style.width = '100%';
    document.getElementById('modal-progress-bar').style.backgroundColor = '#ef4444';
    document.getElementById('modal-pct').textContent        = 'Error';
    document.getElementById('modal-step-label').textContent = '✕ Pipeline failed';
    document.getElementById('modal-status').textContent     = msg;
    const errBox = document.getElementById('modal-error-box');
    if (errBox) { errBox.textContent = msg; errBox.classList.remove('hidden'); }
    // Show close button — relabel it so it doesn't say "View Schedule"
    const doneBtn = document.getElementById('modal-done');
    if (doneBtn) {
      const btn = doneBtn.querySelector('button');
      if (btn) btn.textContent = 'Close';
      doneBtn.classList.remove('hidden');
    }
  }

  // ── Public API ─────────────────────────────────────────────────────────────
  return { runPipeline, saveEdits, loadAllData, closeModal };
})();
