/**
 * reports.js
 * Summary report table: rendering and filtering.
 * Uses real field names from RF constants (config.js).
 * Matches exact output of student_summary.py build_summary().
 */

const ReportModule = (() => {

  // ── State ────────────────────────────────────────────────────────────────────
  let _data     = [];
  let _filtered = [];

  // ── Init ─────────────────────────────────────────────────────────────────────
  function init(data) {
    _data     = Array.isArray(data) ? data : [];
    _filtered = [..._data];
    _render();
    _renderStats();
  }

  // ── Filter ───────────────────────────────────────────────────────────────────
  function applyFilters() {
    const search = (document.getElementById('report-search')?.value || '').toLowerCase().trim();
    const reason = document.getElementById('report-filter-reason')?.value || '';

    _filtered = _data.filter(r => {
      const matchText = !search
        || String(r[RF.COURSE_NAME] || '').toLowerCase().includes(search)
        || String(r[RF.INSTRUCTOR]  || '').toLowerCase().includes(search)
        || String(r[RF.COURSE_ID]   || '').toLowerCase().includes(search);

      const matchReason = !reason || String(r[RF.REASON] || '') === reason;

      return matchText && matchReason;
    });

    _render();
  }

  function clearFilters() {
    const els = ['report-search', 'report-filter-reason'];
    els.forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
    _filtered = [..._data];
    _render();
  }

  // ── Render Table ─────────────────────────────────────────────────────────────
  function _render() {
    const tbody = document.getElementById('report-tbody');
    if (!tbody) return;

    if (_filtered.length === 0) {
      showEmptyState(
        'report-tbody',
        _data.length === 0
          ? 'No report data yet. Run the pipeline first.'
          : 'No results match your filters.',
        _data.length === 0 ? 'Run Pipeline' : 'Clear Filters',
        _data.length === 0 ? "showPage('actions')" : 'ReportModule.clearFilters()'
      );
      _updateCount(0);
      return;
    }

    tbody.innerHTML = _filtered.map(r => {
      // room_name: prefer updated field, fall back to room (id)
      const roomDisplay = r[RF.ROOM_NAME] || r[RF.ROOM] || '—';
      const capacity    = r[RF.ROOM_CAPACITY] != null ? r[RF.ROOM_CAPACITY] : '—';
      const students    = r[RF.STUDENTS]  ?? 0;
      const graduating  = r[RF.GRADUATING_STUDENTS] ?? 0;
      const isHighGrad  = Number(graduating) > 10;

      return `
        <tr class="data-row transition-colors">
          <td class="px-7 py-4">
            <div class="flex flex-col">
              <span class="font-bold text-primary text-sm">${r[RF.COURSE_NAME] ?? ''}</span>
              <span class="text-[10px] text-on-surface-variant font-mono">${r[RF.COURSE_ID] ?? ''}</span>
            </div>
          </td>
          <td class="px-5 py-4 text-center">
            <span class="px-2 py-0.5 bg-secondary-container text-on-secondary-container text-[9px] font-bold rounded">
              ${r[RF.SECTION] ?? ''}
            </span>
          </td>
          <td class="px-5 py-4 text-sm text-on-surface-variant">
            <div class="flex items-center gap-1.5">
              <span class="material-symbols-outlined text-sm">location_on</span>
              ${roomDisplay}
            </div>
          </td>
          <td class="px-5 py-4 text-sm font-medium text-secondary">
            ${r[RF.INSTRUCTOR] ?? ''}
          </td>
          <td class="px-5 py-4 text-center text-sm tabular-nums">
            ${students} / ${capacity}
          </td>
          <td class="px-5 py-4 text-center text-sm font-semibold ${isHighGrad ? 'text-error' : 'text-on-surface-variant'}">
            ${graduating}
          </td>
          <td class="px-7 py-4 text-right">
            ${reasonBadge(r[RF.REASON])}
          </td>
        </tr>`;
    }).join('');

    _updateCount(_filtered.length);
  }

  function _updateCount(n) {
    const el = document.getElementById('report-count');
    if (el) el.textContent = `Showing ${n} of ${_data.length} section${_data.length !== 1 ? 's' : ''}`;
  }

  // ── Report-Level Stats ───────────────────────────────────────────────────────
  function _renderStats() {
    const totalSections = document.getElementById('rpt-stat-sections');
    const totalGrad     = document.getElementById('rpt-stat-graduating');

    if (totalSections) totalSections.textContent = _data.length;

    if (totalGrad) {
      const gradTotal = _data.reduce((s, r) => s + Number(r[RF.GRADUATING_STUDENTS] || 0), 0);
      totalGrad.textContent = gradTotal;
    }
  }

  // ── Public API ───────────────────────────────────────────────────────────────
  return { init, applyFilters, clearFilters };
})();
