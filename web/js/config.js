/**
 * config.js  —  updated
 * Central configuration: file paths, field name constants, pipeline steps.
 * New in this version:
 *   SF.ROOM_TYPE   — 'room_type' field in schedule rows
 *   RF.ROOM_TYPE   — 'room_type' field in report rows
 */

// ── File Paths ────────────────────────────────────────────────────────────────
const CONFIG = {
  SCHEDULE_JSON:  'schedule.json',
  REPORT_JSON:    'report.json',
  STATS_JSON:     'stats.json',
  SCHEDULE_PDF:   'semester_schedule.pdf',
  REPORT_PDF:     'summary_report.pdf',
};

// ── Schedule Row Fields  (matches scheduler_engine output + schedule.json) ────
const SF = {
  SCHEDULE_ID:       'schedule_id',
  COURSE_ID:         'course_id',
  COURSE_NAME:       'course_name',
  SECTION_NO:        'section_no',
  TOTAL_DEMAND:      'total_demand',
  GRADUATING_DEMAND: 'graduating_demand',
  INSTRUCTOR_ID:     'instructor_id',
  INSTRUCTOR_NAME:   'instructor_name',
  ROOM_ID:           'room_id',
  ROOM_NAME:         'room_name',
  ROOM_TYPE:         'room_type',        // ← NEW
  TIME_ID:           'time_id',
  DAY:               'day',
  START_TIME:        'start_time',
  END_TIME:          'end_time',
  CREDIT_HOURS:      'credit_hours',
};

// ── Report Row Fields  (matches student_summary.py build_summary output) ──────
const RF = {
  COURSE_ID:           'course_id',
  COURSE_NAME:         'course_name',
  SECTION:             'section',
  ROOM:                'room',            // room_id integer (kept for compat)
  ROOM_NAME:           'room_name',       // human-readable room label
  ROOM_TYPE:           'room_type',       // ← NEW
  ROOM_CAPACITY:       'room_capacity',
  INSTRUCTOR:          'instructor',
  STUDENTS:            'students',
  GRADUATING_STUDENTS: 'graduating_students',
  REMAINING_STUDENTS:  'remaining_students',
  REASON:              'reason',
};

// ── Stats Fields  (matches stats.json written by web_app.py) ─────────────────
const STAT_F = {
  STUDENTS:           'students',
  COURSES:            'courses',
  INSTRUCTORS:        'instructors',
  ROOMS:              'rooms',
  SECTIONS_GENERATED: 'sections_generated',
  OPENED_COURSES:     'opened_courses',
  CONFLICTS:          'conflicts',
};

// ── Reason Values  (exact strings from student_summary.py) ───────────────────
const REASON = {
  GRADUATING: 'Graduating priority',
  HIGH:       'High demand',
  NORMAL:     'Normal demand',
  LOW:        'Low demand',
};

// ── Valid Day Patterns ────────────────────────────────────────────────────────
const VALID_DAYS = ['Sun/Tue', 'Mon/Wed'];

// ── Pipeline Step Definitions ─────────────────────────────────────────────────
const PIPELINE_STEPS = [
  {
    id:    'load',
    label: 'Load Data',
    msgs: [
      'Connecting to SQL Server…',
      'Loading student records (std table)…',
      'Importing course catalog…',
      'Loading rooms and time slots…',
    ],
  },
  {
    id:    'analyze',
    label: 'Analyze Students',
    msgs: [
      'Scanning student transcripts…',
      'Checking prerequisite completions…',
      'Flagging graduating students…',
      'Computing eligible course demand…',
    ],
  },
  {
    id:    'offer',
    label: 'Build Course Offerings',
    msgs: [
      'Ranking courses by total demand…',
      'Applying graduation priority rules…',
      'Computing required section counts…',
      'Opening sections in database…',
    ],
  },
  {
    id:    'schedule',
    label: 'Generate Schedule',
    msgs: [
      'Sorting sections by demand (high → low)…',
      'Assigning largest suitable rooms first…',
      'Assigning instructors to sections…',
      'Applying Sun/Tue · Mon/Wed patterns…',
      'Final conflict scan… 0 found ✓',
    ],
  },
];
