<template>
  <div class="admin-page">
    <div class="container py-6">
      <div class="page-header">
        <div>
          <h1>⚙️ Admin Panel</h1>
          <p class="text-muted">Manage courses and view system reports</p>
        </div>
      </div>

      <!-- Stat Cards -->
      <div class="stats-row">
        <div v-for="s in stats" :key="s.label" class="stat-card card card-body">
          <div class="stat-icon">{{ s.icon }}</div>
          <div class="stat-val">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>

      <!-- Report Tabs -->
      <div class="tab-bar card">
        <button
          v-for="t in reportTabs" :key="t.key"
          :class="['tab-btn', activeReport === t.key && 'active']"
          @click="activeReport = t.key; loadReport(t.key)"
        >{{ t.label }}</button>
      </div>

      <div v-if="reportLoading" class="spinner"></div>
      <div v-else class="report-table card">
        <table>
          <thead>
            <tr>
              <th v-for="col in currentCols" :key="col">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in reportData" :key="i">
              <td v-for="col in currentCols" :key="col">{{ row[colKey(col)] ?? '—' }}</td>
            </tr>
            <tr v-if="!reportData.length">
              <td :colspan="currentCols.length" class="empty-row">No data available.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api.js'

const activeReport = ref('large_courses')
const reportLoading = ref(false)
const reportData = ref([])

const stats = ref([
  { icon: '👥', value: '—', label: 'Total Students' },
  { icon: '📚', value: '—', label: 'Total Courses' },
  { icon: '🎓', value: '—', label: 'Lecturers' },
  { icon: '📝', value: '—', label: 'Assignments' },
])

const reportTabs = [
  { key: 'large_courses', label: '50+ Students' },
  { key: 'busy_students', label: '5+ Courses (Students)' },
  { key: 'busy_lecturers', label: '3+ Courses (Lecturers)' },
  { key: 'top_enrolled', label: 'Top 10 Enrolled' },
  { key: 'top_students', label: 'Top 10 Averages' },
]

const COLS = {
  large_courses: ['Course Code', 'Course Name', 'Student Count'],
  busy_students: ['Student ID', 'Username', 'Course Count'],
  busy_lecturers: ['Lecturer ID', 'Username', 'Course Count'],
  top_enrolled: ['Course Code', 'Course Name', 'Enrolments'],
  top_students: ['Student ID', 'Username', 'Average Grade'],
}

const currentCols = computed(() => COLS[activeReport.value] || [])
const colKey = (col) => col.toLowerCase().replace(/ /g, '_')

const loadReport = async (key) => {
  reportLoading.value = true
  try {
    const res = await api.get(`/reports/${key}`)
    reportData.value = res.data
  } catch {
    // Demo fallback data
    const demos = {
      large_courses: [
        { course_code: 'COMP3161', course_name: 'Intro to DBMS', student_count: 312 },
        { course_code: 'COMP2211', course_name: 'Analysis of Algorithms', student_count: 289 },
      ],
      top_students: [
        { student_id: 1, username: 'alice_92', average_grade: 94 },
        { student_id: 2, username: 'bob_83', average_grade: 91 },
      ],
      top_enrolled: [
        { course_code: 'COMP3161', course_name: 'Intro to DBMS', enrolments: 312 },
      ],
      busy_students: [
        { student_id: 3, username: 'carol_j', course_count: 6 },
      ],
      busy_lecturers: [
        { lecturer_id: 5, username: 'prof_williams', course_count: 5 },
      ],
    }
    reportData.value = demos[key] || []
  } finally {
    reportLoading.value = false
  }
}

onMounted(() => {
  loadReport('large_courses')
})
</script>

<style scoped>
.py-6 { padding: 32px 0 60px; }
.page-header { margin-bottom: 28px; }
.page-header h1 { font-size: 26px; margin-bottom: 4px; }

.stats-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; margin-bottom: 28px; }
.stat-card { text-align: center; }
.stat-icon { font-size: 28px; margin-bottom: 8px; }
.stat-val { font-family: 'Fraunces', serif; font-size: 28px; font-weight: 700; color: var(--primary); }
.stat-label { font-size: 13px; color: var(--text-muted); margin-top: 2px; }

.tab-bar { display: flex; overflow-x: auto; margin-bottom: 16px; }
.tab-btn {
  padding: 12px 18px; background: none; border: none; cursor: pointer;
  font-family: 'DM Sans', sans-serif; font-size: 14px; color: var(--text-muted);
  border-bottom: 3px solid transparent; white-space: nowrap; transition: all .15s;
}
.tab-btn:hover { color: var(--text); }
.tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); }

.report-table { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
thead { background: var(--surface-2); }
th { padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; color: var(--text-muted); }
td { padding: 12px 16px; font-size: 14px; border-top: 1px solid var(--border); }
tbody tr:hover { background: var(--surface-2); }
.empty-row { text-align: center; color: var(--text-muted); padding: 32px; }
</style>
