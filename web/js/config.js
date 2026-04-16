/**
 * config.js
 * Central configuration: file paths, field name constants,
 * pipeline step definitions. Edit here to update globally.
 */

// ─── FILE PATHS ───────────────────────────────────────────────────────────────
// These match what web_app.py writes into the web/ folder.
const CONFIG = {
  SCHEDULE_JSON:  'schedule.json',
  REPORT_JSON:    'report.json',
  STATS_JSON:     'stats.json',
  SCHEDULE_PDF:   'semester_schedule.pdf',
  REPORT_PDF:     'summary_report.pdf',
};

// ─── FIELD NAMES: SCHEDULE (matches scheduler_engine output) ─────────────────
// Reference: schedule.json keys
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
  TIME_ID:           'time_id',
  DAY:               'day',
  START_TIME:        'start_time',
  END_TIME:          'end_time',
  CREDIT_HOURS:      'credit_hours',
};

// ─── FIELD NAMES: REPORT (matches student_summary.py output) ─────────────────
// Reference: report.json keys
const RF = {
  COURSE_ID:           'course_id',
  COURSE_NAME:         'course_name',
  SECTION:             'section',
  ROOM:                'room',
  ROOM_NAME:           'room_name',      // added in updated student_summary.py
  ROOM_CAPACITY:       'room_capacity',
  INSTRUCTOR:          'instructor',
  STUDENTS:            'students',
  GRADUATING_STUDENTS: 'graduating_students',
  REMAINING_STUDENTS:  'remaining_students',
  REASON:              'reason',
};

// ─── FIELD NAMES: STATS (matches web_app.py stats dict) ──────────────────────
const STAT_F = {
  STUDENTS:           'students',
  COURSES:            'courses',
  INSTRUCTORS:        'instructors',
  ROOMS:              'rooms',
  SECTIONS_GENERATED: 'sections_generated',
  OPENED_COURSES:     'opened_courses',
  CONFLICTS:          'conflicts',
};

// ─── REASON VALUES (exact strings from student_summary.py) ───────────────────
const REASON = {
  GRADUATING: 'Graduating priority',
  HIGH:       'High demand',
  NORMAL:     'Normal demand',
  LOW:        'Low demand',
};

// ─── PIPELINE STEP DEFINITIONS ────────────────────────────────────────────────
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
      'Assigning instructors to sections…',
      'Allocating rooms without conflicts…',
      'Applying Sun/Tue · Mon/Wed patterns…',
      'Verifying time slot integrity…',
      'Final conflict scan… 0 found ✓',
    ],
  },
];
