/**
 * reports.js  —  updated
 * New in this version:
 *   • room_type column added to the report table (RF.ROOM_TYPE)
 *   • Filter dropdown option labels now use the exact backend reason strings
 */

const ReportModule = (() => {

  let _data     = [];
  let _filtered = [];

  // ── Init ───────────────────────────────────────────────────────────────────
  function init(data) {
    _data     = Array.isArray(data) ? data : [];
    _filtered = [..._data];
    _render();
    _renderStats();
  }

  // ── Filter ─────────────────────────────────────────────────────────────────
  function applyFilters() {
    const search = (document.getElementById('report-search')?.value || '').toLowerCase().trim();
    const reason = document.getElementById('report-filter-reason')?.value || '';

    _filtered = _data.filter(r => {
      const matchText = !search
        || String(r[RF.COURSE_NAME] || '').toLowerCase().includes(search)
        || String(r[RF.INSTRUCTOR]  || '').toLowerCase().includes(search)
        || String(r[RF.COURSE_ID]   || '').toLowerCase().includes(search);
      const matchReason = !reason || r[RF.REASON] === reason;
      return matchText && matchReason;
    });

    _render();
  }

  function clearFilters() {
    ['report-search', 'report-filter-reason'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });
    _filtered = [..._data];
    _render();
  }

  // ── Render Table ───────────────────────────────────────────────────────────
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
      const roomDisplay = r[RF.ROOM_NAME] || r[RF.ROOM] || '—';
      const roomType    = r[RF.ROOM_TYPE] || '—';
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
          <td class="px-5 py-4">
            <span class="text-[9px] font-bold bg-surface-container-low text-on-surface-variant px-2 py-1 rounded uppercase tracking-wider">
              ${roomType}
            </span>
          </td>
          <td class="px-5 py-4 text-sm font-medium text-secondary">${r[RF.INSTRUCTOR] ?? ''}</td>
          <td class="px-5 py-4 text-center text-sm tabular-nums">${students} / ${capacity}</td>
          <td class="px-5 py-4 text-center text-sm font-semibold ${isHighGrad ? 'text-error' : 'text-on-surface-variant'}">
            ${graduating}
          </td>
          <td class="px-7 py-4 text-right">${reasonBadge(r[RF.REASON])}</td>
        </tr>`;
    }).join('');

    _updateCount(_filtered.length);
  }

  function _updateCount(n) {
    const el = document.getElementById('report-count');
    if (el) el.textContent = `Showing ${n} of ${_data.length} section${_data.length !== 1 ? 's' : ''}`;
  }

  // ── Report Stats ───────────────────────────────────────────────────────────
  function _renderStats() {
    const secEl  = document.getElementById('rpt-stat-sections');
    const gradEl = document.getElementById('rpt-stat-graduating');
    if (secEl)  secEl.textContent  = _data.length;
    // True count of unique graduating students comes from the scheduler
    // (stats.graduating_students), NOT summed from per-section report rows.
    if (gradEl) {
      const n = (typeof AppState !== 'undefined' && AppState.stats)
        ? Number(AppState.stats.graduating_students || 0)
        : 0;
      gradEl.textContent = n > 0 ? n : '—';
    }
  }

  // ── Public API ─────────────────────────────────────────────────────────────
  return { init, applyFilters, clearFilters };
})();
