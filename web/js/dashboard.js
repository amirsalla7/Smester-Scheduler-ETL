/**
 * dashboard.js
 * Renders the Dashboard page: stat cards, demand bar chart,
 * open/closed donut, room utilization rings.
 * All data is derived from real backend JSON (no hardcoded values).
 */

const DashboardModule = (() => {

  // ── Stats Cards ─────────────────────────────────────────────────────────────
  function renderStats(stats) {
  const map = {
    'stat-students':    STAT_F.STUDENTS,
    'stat-courses':     STAT_F.COURSES,
    'stat-instructors': STAT_F.INSTRUCTORS,
    'stat-rooms':       STAT_F.ROOMS,
    'stat-opened':      STAT_F.OPENED_COURSES,
    'stat-sections':    STAT_F.SECTIONS_GENERATED,
  };

  Object.entries(map).forEach(([elId, field]) => {
    const el = document.getElementById(elId);
    if (el) el.textContent = (stats && stats[field] != null) ? stats[field] : '—';
  });

  // Conflicts card
const conflicts = Number(stats?.[STAT_F.CONFLICTS] ?? 0);

const conflictsEl = document.getElementById('stat-conflicts');
const conflictsBarEl = document.getElementById('stat-conflicts-bar');
const conflictsTextEl = document.getElementById('stat-conflicts-text');

console.log("DASHBOARD CONFLICTS =", conflicts);

if (conflictsEl) {
  conflictsEl.innerText = `${conflicts} Conflict${conflicts !== 1 ? 's' : ''}`;
}

if (conflictsBarEl) {
  const width = conflicts === 0 ? 100 : Math.max(15, 100 - conflicts * 15);
  conflictsBarEl.style.width = `${width}%`;
}

if (conflictsTextEl) {
  conflictsTextEl.innerText = conflicts === 0
    ? 'No room or instructor conflicts detected'
    : `${conflicts} room/instructor conflict${conflicts !== 1 ? 's' : ''} detected`;
}
}

  // ── Demand Bars (top 6 courses) ──────────────────────────────────────────────
  /**
   * Derives unique courses from schedule rows, picks top 6 by total_demand.
   * @param {Array} schedule
   */
  function renderDemandBars(schedule) {
    const container = document.getElementById('demand-bars');
    if (!container) return;

    if (!schedule || schedule.length === 0) {
      container.innerHTML = `<p class="text-xs text-on-surface-variant text-center py-8">No schedule data yet. Run the pipeline first.</p>`;
      return;
    }

    const seen   = new Set();
    const unique = [];
    for (const row of schedule) {
      if (!seen.has(row[SF.COURSE_ID])) {
        seen.add(row[SF.COURSE_ID]);
        unique.push({ name: row[SF.COURSE_NAME], demand: Number(row[SF.TOTAL_DEMAND] || 0) });
      }
    }
    unique.sort((a, b) => b.demand - a.demand);
    const top6   = unique.slice(0, 6);
    const maxVal = top6[0]?.demand || 1;

    container.innerHTML = top6.map(d => `
      <div class="space-y-1.5">
        <div class="flex justify-between text-xs font-semibold text-secondary">
          <span class="truncate max-w-[65%]">${d.name}</span>
          <span>${d.demand} students</span>
        </div>
        <div class="h-2.5 w-full bg-surface-container-low rounded-full overflow-hidden">
          <div class="h-full bg-gradient-to-r from-primary to-primary-container rounded-full"
               style="width:${Math.round(d.demand / maxVal * 100)}%"></div>
        </div>
      </div>`).join('');
  }

  // ── Open / Closed Donut ──────────────────────────────────────────────────────
  function renderDonut(stats) {
    if (!stats) return;

    const total  = Number(stats[STAT_F.COURSES] || 0);
    const opened = Number(stats[STAT_F.OPENED_COURSES] || 0);
    const closed = total - opened;
    const pct    = total > 0 ? Math.round(opened / total * 100) : 0;

    const openDash   = document.getElementById('donut-open');
    const closedDash = document.getElementById('donut-closed');
    const donutTotal = document.getElementById('donut-total');
    const openCount  = document.getElementById('donut-open-count');
    const closedCount= document.getElementById('donut-closed-count');

    if (openDash)    openDash.setAttribute('stroke-dasharray',   `${pct} 100`);
    if (closedDash)  closedDash.setAttribute('stroke-dasharray', `${100 - pct} 100`);
    if (closedDash)  closedDash.setAttribute('stroke-dashoffset',`-${pct}`);
    if (donutTotal)  donutTotal.textContent = total;
    if (openCount)   openCount.textContent  = opened;
    if (closedCount) closedCount.textContent = closed;
  }

  // ── Room Utilization ─────────────────────────────────────────────────────────
  /**
   * Counts sections per room_name, renders top 4 utilization rings.
   * Utilisation pct = sections_in_room / total_sections * 100 (relative, not absolute).
   */
  function renderRoomUsage(schedule) {
    const container = document.getElementById('room-usage-grid');
    if (!container) return;

    if (!schedule || schedule.length === 0) {
      container.innerHTML = `<p class="col-span-4 text-xs text-on-surface-variant text-center py-4">No data.</p>`;
      return;
    }

    const counts = {};
    const names  = {};
    for (const row of schedule) {
      const rid = row[SF.ROOM_ID];
      counts[rid] = (counts[rid] || 0) + 1;
      names[rid]  = row[SF.ROOM_NAME] || String(rid);
    }

    const total = schedule.length;
    const top4  = Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 4);

    const COLORS = ['#051125', '#94ccff', '#1B263B', '#ba1a1a'];

    container.innerHTML = top4.map(([rid, cnt], i) => {
      const pct   = Math.round(cnt / total * 100);
      const color = COLORS[i] || '#051125';
      return `
        <div class="flex flex-col items-center text-center">
          <div class="relative w-24 h-24 mb-3">
            <svg viewBox="0 0 42 42" class="w-full h-full -rotate-90">
              <circle class="donut-ring" cx="21" cy="21" r="16" stroke="#f2f4f7"/>
              <circle class="donut-ring" cx="21" cy="21" r="16"
                      stroke="${color}" stroke-dasharray="${pct} 100"/>
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <span class="text-base font-extrabold font-headline" style="color:${color}">${pct}%</span>
            </div>
          </div>
          <p class="text-sm font-bold text-primary">${names[rid]}</p>
          <p class="text-[10px] text-on-surface-variant">${cnt} section${cnt !== 1 ? 's' : ''}</p>
        </div>`;
    }).join('');
  }

  // ── Graduating Banner ────────────────────────────────────────────────────────
  function renderGraduatingBanner(schedule) {
    const gradCount   = document.getElementById('banner-grad-count');
    const sectCount   = document.getElementById('banner-grad-sections');

    if (!schedule || schedule.length === 0) return;

    // Count sections that have graduating_demand > 0
    const gradSections = schedule.filter(r => Number(r[SF.GRADUATING_DEMAND] || 0) > 0);
    const totalGrad    = gradSections.reduce((s, r) => s + Number(r[SF.GRADUATING_DEMAND] || 0), 0);
    const uniqueGrad   = new Set(gradSections.map(r => r[SF.GRADUATING_DEMAND])).size;

    if (gradCount)  gradCount.textContent  = totalGrad > 0 ? totalGrad : '—';
    if (sectCount)  sectCount.textContent  = gradSections.length;
  }

  // ── Public API ───────────────────────────────────────────────────────────────
  function render(stats, schedule) {
    renderStats(stats);
    renderDemandBars(schedule);
    renderDonut(stats);
    renderRoomUsage(schedule);
    renderGraduatingBanner(schedule);
  }

  return { render, renderStats, renderDemandBars, renderDonut, renderRoomUsage };
})();
