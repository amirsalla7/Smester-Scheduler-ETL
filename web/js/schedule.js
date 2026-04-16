/**
 * schedule.js
 * Schedule table: rendering, filtering, sorting, pagination, editing.
 * Uses real field names from SF constants (config.js).
 * No mock data.
 */

const ScheduleModule = (() => {
  // ── State ────────────────────────────────────────────────────────────────────
  let _data = [];
  let _filtered = [];
  let _sortCol = null;
  let _sortDir = 1;
  let _currentPage = 1;
  const PAGE_SIZE = 12;

  let _editingIndex = null;
  let _resources = { instructors: [], rooms: [] };

  // ── Init ─────────────────────────────────────────────────────────────────────
  function init(data) {
    _data = Array.isArray(data) ? data : [];
    _filtered = [..._data];
    _sortCol = null;
    _sortDir = 1;
    _currentPage = 1;
    _editingIndex = null;
    _render();
  }

  // ── Resources for edit dropdowns ─────────────────────────────────────────────
  function setResources(resources) {
    _resources = resources || { instructors: [], rooms: [] };
  }

  // ── Filter ───────────────────────────────────────────────────────────────────
  function applyFilters() {
    const search = (document.getElementById('sched-search')?.value || '').toLowerCase().trim();
    const day = document.getElementById('sched-filter-day')?.value || '';
    const hrs = document.getElementById('sched-filter-hours')?.value || '';

    _filtered = _data.filter(r => {
      const matchText =
        !search ||
        String(r[SF.COURSE_NAME] || '').toLowerCase().includes(search) ||
        String(r[SF.COURSE_ID] || '').toLowerCase().includes(search) ||
        String(r[SF.INSTRUCTOR_NAME] || '').toLowerCase().includes(search) ||
        String(r[SF.ROOM_NAME] || r[SF.ROOM_ID] || '').toLowerCase().includes(search);

      const matchDay = !day || r[SF.DAY] === day;
      const matchHrs = !hrs || String(r[SF.CREDIT_HOURS] || '') === hrs;

      return matchText && matchDay && matchHrs;
    });

    if (_sortCol) _applySort();
    _currentPage = 1;
    _render();
  }

  function clearFilters() {
    const ids = ['sched-search', 'sched-filter-day', 'sched-filter-hours'];
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });

    _filtered = [..._data];
    _currentPage = 1;
    _render();
  }

  // ── Sort ─────────────────────────────────────────────────────────────────────
  function sort(col) {
    if (_sortCol === col) _sortDir *= -1;
    else {
      _sortCol = col;
      _sortDir = 1;
    }

    _applySort();
    _render();
  }

  function _applySort() {
    _filtered.sort((a, b) => {
      let va, vb;

      switch (_sortCol) {
        case 'course_id':
          va = a[SF.COURSE_ID];
          vb = b[SF.COURSE_ID];
          break;
        case 'course_name':
          va = a[SF.COURSE_NAME];
          vb = b[SF.COURSE_NAME];
          break;
        case 'instructor_name':
          va = a[SF.INSTRUCTOR_NAME];
          vb = b[SF.INSTRUCTOR_NAME];
          break;
        case 'start_time':
          va = a[SF.START_TIME];
          vb = b[SF.START_TIME];
          break;
        case 'credit_hours':
          return (Number(a[SF.CREDIT_HOURS] || 0) - Number(b[SF.CREDIT_HOURS] || 0)) * _sortDir;
        case 'total_demand':
          return (Number(a[SF.TOTAL_DEMAND] || 0) - Number(b[SF.TOTAL_DEMAND] || 0)) * _sortDir;
        default:
          va = '';
          vb = '';
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

  // ── Edit helpers ─────────────────────────────────────────────────────────────
  function toggleEdit(globalIndex) {
    _editingIndex = globalIndex;
    _render();
  }

  function cancelEdit() {
    _editingIndex = null;
    _render();
  }

  function _roomOptions(selectedRoomId) {
    return (_resources.rooms || []).map(room => `
      <option value="${room.room_id}" ${String(room.room_id) === String(selectedRoomId) ? 'selected' : ''}>
        ${room.room_name || room.room_id} (${room.room_type || 'Lecture'} - ${room.capacity || 0})
      </option>
    `).join('');
  }

  function _instructorOptions(selectedInstructorId) {
    return (_resources.instructors || []).map(inst => `
      <option value="${inst.instructor_id}" ${String(inst.instructor_id) === String(selectedInstructorId) ? 'selected' : ''}>
        ${inst.instructor_name}
      </option>
    `).join('');
  }

function saveEdit(globalIndex) {
  const row = _filtered[globalIndex];
  if (!row) return;

  const instructorSelect = document.getElementById(`edit-instructor-${globalIndex}`);
  const roomSelect = document.getElementById(`edit-room-${globalIndex}`);
  const daySelect = document.getElementById(`edit-day-${globalIndex}`);
  const startInput = document.getElementById(`edit-start-${globalIndex}`);
  const endInput = document.getElementById(`edit-end-${globalIndex}`);

  const selectedInstructorId = instructorSelect?.value;
  const selectedInstructor = (_resources.instructors || []).find(
    i => String(i.instructor_id) === String(selectedInstructorId)
  );

  const selectedRoomId = roomSelect?.value;
  const selectedRoom = (_resources.rooms || []).find(
    r => String(r.room_id) === String(selectedRoomId)
  );

  row[SF.INSTRUCTOR_ID] = selectedInstructorId;
  row[SF.INSTRUCTOR_NAME] = selectedInstructor
    ? selectedInstructor.instructor_name
    : row[SF.INSTRUCTOR_NAME];

  row[SF.ROOM_ID] = selectedRoomId;
  row[SF.ROOM_NAME] = selectedRoom
    ? selectedRoom.room_name
    : row[SF.ROOM_NAME];
  row[SF.ROOM_TYPE] = selectedRoom
    ? selectedRoom.room_type
    : row[SF.ROOM_TYPE];
  row[SF.ROOM_CAPACITY] = selectedRoom
    ? selectedRoom.capacity
    : row[SF.ROOM_CAPACITY];

  row[SF.DAY] = daySelect?.value || row[SF.DAY];
  row[SF.START_TIME] = startInput?.value ? `${startInput.value}:00` : row[SF.START_TIME];
  row[SF.END_TIME] = endInput?.value ? `${endInput.value}:00` : row[SF.END_TIME];

  // تحديث _data أيضًا
  const original = _data.find(x =>
    String(x[SF.COURSE_ID]) === String(row[SF.COURSE_ID]) &&
    String(x[SF.SECTION_NO]) === String(row[SF.SECTION_NO])
  );

  if (original) {
    Object.assign(original, row);
  }

  // تحديث AppState.schedule أيضًا
  if (window.AppState && Array.isArray(AppState.schedule)) {
    const appRow = AppState.schedule.find(x =>
      String(x[SF.COURSE_ID]) === String(row[SF.COURSE_ID]) &&
      String(x[SF.SECTION_NO]) === String(row[SF.SECTION_NO])
    );

    if (appRow) {
      Object.assign(appRow, row);
    }
  }

  _editingIndex = null;
  _render();
}

  // ── Render ───────────────────────────────────────────────────────────────────
  function _render() {
    const tbody = document.getElementById('schedule-tbody');
    if (!tbody) return;

    if (_filtered.length === 0) {
      showEmptyState(
        'schedule-tbody',
        _data.length === 0
          ? 'No schedule generated yet. Run the pipeline first.'
          : 'No results match your filters.',
        _data.length === 0 ? 'Run Pipeline' : 'Clear Filters',
        _data.length === 0 ? 'runFullPipeline()' : 'ScheduleModule.clearFilters()'
      );
      _updatePager(0, 0, 1);
      return;
    }

    const total = _filtered.length;
    const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    _currentPage = Math.min(_currentPage, totalPages);

    const start = (_currentPage - 1) * PAGE_SIZE;
    const slice = _filtered.slice(start, start + PAGE_SIZE);

    tbody.innerHTML = slice.map((r, localIndex) => {
      const globalIndex = start + localIndex;
      const isEditing = _editingIndex === globalIndex;

      if (isEditing) {
        return `
          <tr class="data-row transition-colors bg-yellow-50">
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
            <td class="px-5 py-3.5">
              <select id="edit-instructor-${globalIndex}" class="w-full px-2 py-1 rounded border text-sm">
                ${_instructorOptions(r[SF.INSTRUCTOR_ID])}
              </select>
            </td>
            <td class="px-5 py-3.5">
              <select id="edit-room-${globalIndex}" class="w-full px-2 py-1 rounded border text-sm">
                ${_roomOptions(r[SF.ROOM_ID])}
              </select>
            </td>
            <td class="px-5 py-3.5">
              <select id="edit-day-${globalIndex}" class="w-full px-2 py-1 rounded border text-sm">
                <option value="Sun/Tue" ${r[SF.DAY] === 'Sun/Tue' ? 'selected' : ''}>Sun/Tue</option>
                <option value="Mon/Wed" ${r[SF.DAY] === 'Mon/Wed' ? 'selected' : ''}>Mon/Wed</option>
              </select>
            </td>
            <td class="px-5 py-3.5">
              <input id="edit-start-${globalIndex}" type="time" value="${String(r[SF.START_TIME] || '').slice(0, 5)}" class="w-full px-2 py-1 rounded border text-sm">
            </td>
            <td class="px-5 py-3.5">
              <input id="edit-end-${globalIndex}" type="time" value="${String(r[SF.END_TIME] || '').slice(0, 5)}" class="w-full px-2 py-1 rounded border text-sm">
            </td>
            <td class="px-5 py-3.5 text-right font-semibold text-secondary">
              ${r[SF.CREDIT_HOURS] ?? ''}
            </td>
            <td class="px-5 py-3.5 text-center">
              <div class="flex gap-2 justify-center">
                <button onclick="ScheduleModule.saveEdit(${globalIndex})" class="px-3 py-1 rounded bg-green-600 text-white text-xs font-bold">Save</button>
                <button onclick="ScheduleModule.cancelEdit()" class="px-3 py-1 rounded bg-gray-500 text-white text-xs font-bold">Cancel</button>
              </div>
            </td>
          </tr>
        `;
      }

      return `
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
          <td class="px-5 py-3.5 text-center">
            <button onclick="ScheduleModule.toggleEdit(${globalIndex})" class="px-3 py-1 rounded bg-primary text-white text-xs font-bold hover:bg-primary-container transition-colors">
              Edit
            </button>
          </td>
        </tr>`;
    }).join('');

    _updatePager(start, total, totalPages);

    const countEl = document.getElementById('schedule-count');
    if (countEl) {
      countEl.textContent = `${total} course section${total !== 1 ? 's' : ''} found`;
    }
  }

  function _updatePager(start, total, totalPages) {
    const infoEl = document.getElementById('sched-pager-info');
    const pageEl = document.getElementById('sched-page-num');
    const prevBtn = document.getElementById('sched-prev');
    const nextBtn = document.getElementById('sched-next');

    const end = Math.min(start + PAGE_SIZE, total);

    if (infoEl) {
      infoEl.textContent = total > 0
        ? `Showing ${start + 1}–${end} of ${total}`
        : 'No results';
    }

    if (pageEl) pageEl.textContent = _currentPage;
    if (prevBtn) prevBtn.disabled = _currentPage <= 1;
    if (nextBtn) nextBtn.disabled = _currentPage >= totalPages;
  }

  // ── Quick Stats ──────────────────────────────────────────────────────────────
  function renderQuickStats(schedule) {
    if (!schedule || schedule.length === 0) return;

    const uniqueCourses = new Set(schedule.map(r => r[SF.COURSE_ID])).size;
    const uniqueInstructors = new Set(schedule.map(r => r[SF.INSTRUCTOR_ID])).size;
    const uniqueRooms = new Set(schedule.map(r => r[SF.ROOM_ID])).size;

    const elMap = {
      'qs-courses': uniqueCourses,
      'qs-instructors': uniqueInstructors,
      'qs-rooms': uniqueRooms,
      'qs-sections': schedule.length,
    };

    Object.entries(elMap).forEach(([id, val]) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    });
  }

  // ── Public API ───────────────────────────────────────────────────────────────
  return {
    init,
    applyFilters,
    clearFilters,
    sort,
    changePage,
    renderQuickStats,
    setResources,
    toggleEdit,
    saveEdit,
    cancelEdit
  };
})();