/**
 * schedule.js
 * Schedule table: rendering, filtering, sorting, pagination.
 * Uses real field names from SF constants (config.js).
 * No mock data.
 */

const ScheduleModule = (() => {

  // ── State ────────────────────────────────────────────────────────────────────
  let _data        = [];   // full dataset
  let _filtered    = [];   // after filters applied
  let _sortCol     = null;
  let _sortDir     = 1;    // 1 = asc, -1 = desc
  let _currentPage = 1;
  const PAGE_SIZE  = 12;

  // ── Init ─────────────────────────────────────────────────────────────────────
  function init(data) {
    _data        = Array.isArray(data) ? data : [];
    _filtered    = [..._data];
    _sortCol     = null;
    _sortDir     = 1;
    _currentPage = 1;
    _render();
  }

  // ── Filter ───────────────────────────────────────────────────────────────────
  function applyFilters() {
    const search = (document.getElementById('sched-search')?.value || '').toLowerCase().trim();
    const day    = document.getElementById('sched-filter-day')?.value   || '';
    const hrs    = document.getElementById('sched-filter-hours')?.value || '';

    _filtered = _data.filter(r => {
      const matchText = !search
        || String(r[SF.COURSE_NAME]      || '').toLowerCase().includes(search)
        || String(r[SF.COURSE_ID]        || '').toLowerCase().includes(search)
        || String(r[SF.INSTRUCTOR_NAME]  || '').toLowerCase().includes(search)
        || String(r[SF.ROOM_NAME]        || r[SF.ROOM_ID] || '').toLowerCase().includes(search);

      const matchDay  = !day || r[SF.DAY] === day;
      const matchHrs  = !hrs || String(r[SF.CREDIT_HOURS] || '') === hrs;

      return matchText && matchDay && matchHrs;
    });

    if (_sortCol) _applySort();
    _currentPage = 1;
    _render();
  }

  function clearFilters() {
    const ids = ['sched-search', 'sched-filter-day', 'sched-filter-hours'];
    ids.forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
    _filtered    = [..._data];
    _currentPage = 1;
    _render();
  }

  // ── Sort ─────────────────────────────────────────────────────────────────────
  function sort(col) {
    if (_sortCol === col) _sortDir *= -1;
    else { _sortCol = col; _sortDir = 1; }
    _applySort();
    _render();
  }

  function _applySort() {
    _filtered.sort((a, b) => {
      let va, vb;
      switch (_sortCol) {
        case 'course_id':       va = a[SF.COURSE_ID];       vb = b[SF.COURSE_ID];       break;
        case 'course_name':     va = a[SF.COURSE_NAME];     vb = b[SF.COURSE_NAME];     break;
        case 'instructor_name': va = a[SF.INSTRUCTOR_NAME]; vb = b[SF.INSTRUCTOR_NAME]; break;
        case 'start_time':      va = a[SF.START_TIME];      vb = b[SF.START_TIME];      break;
        case 'credit_hours':
          return (Number(a[SF.CREDIT_HOURS] || 0) - Number(b[SF.CREDIT_HOURS] || 0)) * _sortDir;
        case 'total_demand':
          return (Number(a[SF.TOTAL_DEMAND] || 0) - Number(b[SF.TOTAL_DEMAND] || 0)) * _sortDir;
        default: va = ''; vb = '';
      }
      return String(va || '').localeCompare(String(vb || '')) * _sortDir;
    });
  }

  // ── Pagination ───────────────────────────────────────────────────────────────
  function changePage(dir) {
    const totalPages = Math.max(1, Math.ceil(_filtered.length / PAGE_SIZE));
    _currentPage = Math.max(1, Math.min(totalPages, _currentPage + dir));
    _render();
  }

  // ── Render ───────────────────────────────────────────────────────────────────
  function _render() {
    const tbody = document.getElementById('schedule-tbody');
    if (!tbody) return;

    // Empty state
    if (_filtered.length === 0) {
      showEmptyState(
        'schedule-tbody',
        _data.length === 0
          ? 'No schedule generated yet. Run the pipeline first.'
          : 'No results match your filters.',
        _data.length === 0 ? 'Run Pipeline' : 'Clear Filters',
        _data.length === 0 ? "showPage('actions')" : 'ScheduleModule.clearFilters()'
      );
      _updatePager(0, 0, 1);
      return;
    }

    const total      = _filtered.length;
    const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    _currentPage     = Math.min(_currentPage, totalPages);

    const start = (_currentPage - 1) * PAGE_SIZE;
    const slice = _filtered.slice(start, start + PAGE_SIZE);

    tbody.innerHTML = slice.map(r => `
      <tr class="data-row transition-colors">
        <td class="px-5 py-3.5 font-mono text-xs font-semibold text-secondary">
          ${r[SF.COURSE_ID] ?? ''}
        </td>
        <td class="px-5 py-3.5 font-medium text-primary text-sm">
          ${r[SF.COURSE_NAME] ?? ''}
        </td>
        <td class="px-5 py-3.5 text-center">
          <span class="px-2 py-0.5 bg-secondary-container text-on-secondary-container text-[9px] font-bold rounded">
            ${r[SF.SECTION_NO] ?? ''}
          </span>
        </td>
        <td class="px-5 py-3.5 text-on-surface-variant text-sm">
          ${r[SF.INSTRUCTOR_NAME] ?? ''}
        </td>
        <td class="px-5 py-3.5 text-on-surface-variant text-sm">
          ${r[SF.ROOM_NAME] ?? r[SF.ROOM_ID] ?? ''}
        </td>
        <td class="px-5 py-3.5">
          ${dayChips(r[SF.DAY])}
        </td>
        <td class="px-5 py-3.5 text-sm tabular-nums font-medium">
          ${formatTime(r[SF.START_TIME])}
        </td>
        <td class="px-5 py-3.5 text-sm tabular-nums font-medium">
          ${formatTime(r[SF.END_TIME])}
        </td>
        <td class="px-5 py-3.5 text-right font-semibold text-secondary">
          ${r[SF.CREDIT_HOURS] ?? ''}
        </td>
      </tr>`).join('');

    _updatePager(start, total, totalPages);

    // Update count label in page header
    const countEl = document.getElementById('schedule-count');
    if (countEl) {
      countEl.textContent = `${total} course section${total !== 1 ? 's' : ''} found`;
    }
  }

  function _updatePager(start, total, totalPages) {
    const infoEl   = document.getElementById('sched-pager-info');
    const pageEl   = document.getElementById('sched-page-num');
    const prevBtn  = document.getElementById('sched-prev');
    const nextBtn  = document.getElementById('sched-next');

    const end = Math.min(start + PAGE_SIZE, total);

    if (infoEl) infoEl.textContent = total > 0
      ? `Showing ${start + 1}–${end} of ${total}`
      : 'No results';

    if (pageEl) pageEl.textContent  = _currentPage;
    if (prevBtn) prevBtn.disabled   = _currentPage <= 1;
    if (nextBtn) nextBtn.disabled   = _currentPage >= totalPages;
  }

  // ── Quick Stats (above table) ────────────────────────────────────────────────
  function renderQuickStats(schedule) {
    if (!schedule || schedule.length === 0) return;

    const uniqueCourses     = new Set(schedule.map(r => r[SF.COURSE_ID])).size;
    const uniqueInstructors = new Set(schedule.map(r => r[SF.INSTRUCTOR_ID])).size;
    const uniqueRooms       = new Set(schedule.map(r => r[SF.ROOM_ID])).size;

    const elMap = {
      'qs-courses':     uniqueCourses,
      'qs-instructors': uniqueInstructors,
      'qs-rooms':       uniqueRooms,
      'qs-sections':    schedule.length,
    };
    Object.entries(elMap).forEach(([id, val]) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    });
  }

  // ── Public API ───────────────────────────────────────────────────────────────
  return { init, applyFilters, clearFilters, sort, changePage, renderQuickStats };
})();
