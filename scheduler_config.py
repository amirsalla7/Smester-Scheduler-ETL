SERVER = "localhost"
DATABASE = "UniversityDB"
DRIVER = "ODBC Driver 17 for SQL Server"

USE_TRUSTED_CONNECTION = True

# إعدادات الجدولة
DEFAULT_ROOM_CAPACITY_FALLBACK = 30
DEFAULT_MAX_SECTIONS_PER_COURSE = 1

# ساعات الحمل التدريسي حسب الدرجة
LOAD_RULES = {
    "Professor": 15,
    "Associate Professor": 12,
    "Assistant Professor": 9,
    "Doctor": 12,
    "Master": 9,
    "Bachelor": 6
}

# إذا المدرس إداري نطرح من الحمل
ADMIN_LOAD_REDUCTION = 3

# وقت المحاضرات المسموح
ALLOWED_START = "08:00:00"
ALLOWED_END = "16:00:00"

# نوع القاعة الافتراضي إذا ما كان عند المادة نوع محدد
DEFAULT_ROOM_TYPE = "Lecture"

# هل نحذف الجدول القديم قبل إنشاء جدول جديد؟
CLEAR_OLD_SCHEDULE = True

# شرط فتح المادة
MIN_STUDENTS_TO_OPEN_COURSE = 5

# أولوية الخريجين
GRADUATING_PRIORITY_ENABLED = True