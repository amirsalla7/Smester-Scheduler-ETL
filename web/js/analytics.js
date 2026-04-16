/**
 * analytics.js
 * Analytics page: all charts derived from real schedule data.
 * No hardcoded values. Reads SF field names from config.js.
 */

const AnalyticsModule = (() => {

  // ── Full Demand Bars ─────────────────────────────────────────────────────────
  function renderDemandBars(schedule) {
    const container = document.getElementById('analytics-full-bars');
    if (!container) return;

    if (!schedule || schedule.length === 0) {
      container.innerHTML = '<p class="text-xs text-on-surface-variant py-4 text-center">No data yet.</p>';
      return;
    }

    // Unique courses by course_id
    const seen   = new Set();
    const unique = [];
    for (const row of schedule) {
      if (!seen.has(row[SF.COURSE_ID])) {
        seen.add(row[SF.COURSE_ID]);
        unique.push({
          course_id: row[SF.COURSE_ID],
          name:      row[SF.COURSE_NAME],
          demand:    Number(row[SF.TOTAL_DEMAND] || 0),
        });
      }
    }
    unique.sort((a, b) => b.demand - a.demand);
    const maxVal = unique[0]?.demand || 1;

    container.innerHTML = unique.map(d => `
      <div class="space-y-1">
        <div class="flex justify-between text-xs font-semibold text-secondary">
          <span class="truncate max-w-[70%]">${d.name}</span>
          <span>${d.demand}</span>
        </div>
        <div class="h-2 w-full bg-surface-container-low rounded-full overflow-hidden">
          <div class="h-full bg-gradient-to-r from-primary to-primary-container rounded-full"
               style="width:${Math.round(d.demand / maxVal * 100)}%"></div>
        </div>
      </div>`).join('');
  }

  // ── Section Distribution ─────────────────────────────────────────────────────
  /**
   * Counts how many sections each course_id has, then buckets into 1, 2, 3, 4+
   */
  function renderSectionDistribution(schedule) {
    const container = document.getElementById('analytics-section-dist');
    if (!container) return;

    if (!schedule || schedule.length === 0) {
      container.innerHTML = '<p class="text-xs text-on-surface-variant">No data.</p>';
      return;
    }

    const sectionCounts = {};
    for (const row of schedule) {
      sectionCounts[row[SF.COURSE_ID]] = (sectionCounts[row[SF.COURSE_ID]] || 0) + 1;
    }

    const buckets = { 1: 0, 2: 0, 3: 0, '4+': 0 };
    Object.values(sectionCounts).forEach(n => {
      if      (n === 1) buckets[1]++;
      else if (n === 2) buckets[2]++;
      else if (n === 3) buckets[3]++;
      else              buckets['4+']++;
    });

    const totalCourses = Object.keys(sectionCounts).length;
    const colors = ['#c2dcff', '#051125', '#94ccff', '#ba1a1a'];
    const labels = ['1 Section', '2 Sections', '3 Sections', '4+ Sections'];
    const keys   = [1, 2, 3, '4+'];

    container.innerHTML = keys.map((k, i) => {
      const count = buckets[k];
      const pct   = totalCourses > 0 ? Math.round(count / totalCourses * 100) : 0;
      return `
        <div class="space-y-1.5">
          <div class="flex justify-between text-xs font-semibold text-secondary">
            <span>${labels[i]}</span><span>${count} courses</span>
          </div>
          <div class="h-2.5 w-full bg-surface-container-low rounded-full overflow-hidden">
            <div class="h-full rounded-full" style="width:${pct}%;background:${colors[i]}"></div>
          </div>
        </div>`;
    }).join('');
  }

  // ── Day Pattern Split ────────────────────────────────────────────────────────
  function renderDayPatternSplit(schedule) {
    const container = document.getElementById('analytics-day-split');
    if (!container) return;

    if (!schedule || schedule.length === 0) {
      container.innerHTML = '<p class="text-xs text-on-surface-variant">No data.</p>';
      return;
    }

    const counts = {};
    for (const row of schedule) {
      const day = row[SF.DAY] || 'Unknown';
      counts[day] = (counts[day] || 0) + 1;
    }

    const total  = schedule.length;
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    const colors = ['#051125', '#94ccff', '#c2dcff', '#1B263B'];

    container.innerHTML = sorted.map(([day, cnt], i) => {
      const pct   = Math.round(cnt / total * 100);
      const color = colors[i] || '#45474d';
      return `
        <div class="flex items-center gap-3">
          <span class="w-28 text-xs font-bold text-secondary truncate">${day}</span>
          <div class="flex-1 h-2.5 bg-surface-container-low rounded-full overflow-hidden">
            <div class="h-full rounded-full" style="width:${pct}%;background:${color}"></div>
          </div>
          <span class="text-xs font-bold text-primary w-8 text-right">${pct}%</span>
        </div>`;
    }).join('');
  }

  // ── Room Usage ───────────────────────────────────────────────────────────────
  function renderRoomUsage(schedule) {
    const container = document.getElementById('analytics-room-usage');
    if (!container) return;

    if (!schedule || schedule.length === 0) {
      container.innerHTML = '<p class="text-xs text-on-surface-variant">No data.</p>';
      return;
    }

    const counts = {};
    const names  = {};
    for (const row of schedule) {
      const rid   = row[SF.ROOM_ID];
      counts[rid] = (counts[rid] || 0) + 1;
      names[rid]  = row[SF.ROOM_NAME] || String(rid);
    }

    const total = schedule.length;
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);

    container.innerHTML = sorted.map(([rid, cnt]) => {
      const pct = Math.round(cnt / total * 100);
      return `
        <div class="space-y-1">
          <div class="flex justify-between text-xs font-semibold text-secondary">
            <span>${names[rid]}</span><span>${cnt} sections</span>
          </div>
          <div class="h-2 w-full bg-surface-container-low rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-primary to-primary-container rounded-full"
                 style="width:${pct}%"></div>
          </div>
        </div>`;
    }).join('');
  }

  // ── Summary Metrics ──────────────────────────────────────────────────────────
  function renderMetrics(schedule, stats) {
    const totalSections  = schedule ? schedule.length : 0;
    const uniqueCourses  = schedule ? new Set(schedule.map(r => r[SF.COURSE_ID])).size : 0;
    const uniqueRooms    = schedule ? new Set(schedule.map(r => r[SF.ROOM_ID])).size : 0;

    const elMap = {
      'an-total-sections':  totalSections,
      'an-unique-courses':  uniqueCourses,
      'an-unique-rooms':    uniqueRooms,
      'an-total-students':  stats ? (stats[STAT_F.STUDENTS]  || 0) : '—',
    };
    Object.entries(elMap).forEach(([id, val]) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    });
  }

  // ── Public API ───────────────────────────────────────────────────────────────
  function render(schedule, stats) {
    renderMetrics(schedule, stats);
    renderDemandBars(schedule);
    renderSectionDistribution(schedule);
    renderDayPatternSplit(schedule);
    renderRoomUsage(schedule);
  }

  return { render };
})();
