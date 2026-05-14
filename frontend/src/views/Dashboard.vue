<template>
<div>
  <div class="dashboard">
    <div class="container py-6">
      <div class="dash-header">
        <div>
          <h1>My courses</h1>
          <p class="text-muted">Course overview</p>
        </div>
        <!-- Only admins can create courses -->
        <button v-if="isAdmin" class="btn btn-primary" @click="showCreate = true">+ New Course</button>
      </div>

      <div class="filters-bar card card-body">
        <select v-model="filterBy" class="filter-select">
          <option value="all">All courses</option>
        </select>
        <input v-model="search" class="form-control search-input" placeholder="🔍  Search courses…" />
        <select v-model="sortBy" class="filter-select">
          <option value="name">Sort by name</option>
          <option value="code">Sort by code</option>
        </select>
        <div class="view-toggle">
          <button :class="['toggle-btn', viewMode==='card'&&'active']" @click="viewMode='card'">⊞</button>
          <button :class="['toggle-btn', viewMode==='list'&&'active']" @click="viewMode='list'">☰</button>
        </div>
      </div>

      <div v-if="loading" class="spinner"></div>
      <div v-else-if="error" class="alert alert-error">{{ error }}</div>

      <!-- Card grid -->
      <div v-else-if="viewMode === 'card'" class="courses-grid">
        <div v-for="course in filteredCourses" :key="course.courseCode || course.code"
          class="course-card"
          @click="$router.push(`/course/${course.courseCode || course.code}`)">
          <div class="course-banner" :style="{ background: bannerColor(course) }">
            <div class="banner-pattern"></div>
            <div class="banner-code">{{ course.courseCode || course.code }}</div>
          </div>
          <div class="course-body">
            <div class="course-semester">{{ course.courseCode || course.code }} | S2_2025/26</div>
            <div class="course-name">
              <span class="star">★</span>
              <span>{{ course.courseName || course.name }}</span>
            </div>
            <div class="course-category">COMP Undergraduate Courses</div>
            <div class="course-footer">
              <span class="text-sm text-muted">
                {{ isLecturer ? '🎓 Teaching' : isAdmin ? '⚙️ Admin' : '📚 Enrolled' }}
              </span>
              <button class="more-btn" @click.stop>⋮</button>
            </div>
          </div>
        </div>

        <div v-if="filteredCourses.length === 0" class="empty-state">
          <div class="empty-icon">📚</div>
          <h3>No courses found</h3>
          <p>{{ isStudent ? 'You are not enrolled in any courses yet.' : 'No courses assigned yet.' }}</p>
        </div>
      </div>

      <!-- List view -->
      <div v-else class="courses-list card">
        <div v-for="course in filteredCourses" :key="course.courseCode||course.code"
          class="course-row"
          @click="$router.push(`/course/${course.courseCode||course.code}`)">
          <div class="row-dot" :style="{ background: bannerColor(course) }"></div>
          <div class="row-info">
            <div class="row-name">{{ course.courseName || course.name }}</div>
            <div class="row-code text-muted text-sm">{{ course.courseCode || course.code }} · S2_2025/26</div>
          </div>
          <span class="badge badge-green">{{ isLecturer ? 'Teaching' : 'Enrolled' }}</span>
          <span class="row-arrow">›</span>
        </div>
        <div v-if="!filteredCourses.length" class="empty-list">No courses found.</div>
      </div>
    </div>

    <!-- Create Course Modal (admin only) -->
    <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate = false">
      <div class="modal">
        <div class="modal-header"><h3>Create New Course</h3><button class="close-btn" @click="showCreate = false">✕</button></div>
        <div class="modal-body">
          <div v-if="createError" class="alert alert-error">{{ createError }}</div>
          <div class="form-group"><label class="form-label">Course Code</label><input v-model="newCourse.code" class="form-control" placeholder="e.g. COMP3161" /></div>
          <div class="form-group"><label class="form-label">Course Name</label><input v-model="newCourse.name" class="form-control" placeholder="e.g. Introduction to Database Management" /></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showCreate = false">Cancel</button>
          <button class="btn btn-primary" @click="createCourse" :disabled="creating">{{ creating ? 'Creating…' : 'Create Course' }}</button>
        </div>
      </div>
    </div>
  </div>
<!-- Available courses to enrol in (students only) -->
<div v-if="isStudent && availableCourses.length" class="mt-4">
  <h2 class="section-heading">Available Courses</h2>
  <div class="courses-grid">
    <div v-for="course in availableCourses" :key="course.courseCode"
      class="course-card"
      @click="$router.push(`/course/${course.courseCode}`)">
      <div class="course-banner" :style="{ background: bannerColor(course) }">
        <div class="banner-pattern"></div>
        <div class="banner-code">{{ course.courseCode }}</div>
      </div>
      <div class="course-body">
        <div class="course-semester">{{ course.courseCode }} | S2_2025/26</div>
        <div class="course-name"><span class="star">★</span><span>{{ course.courseName }}</span></div>
        <div class="course-category">COMP Undergraduate Courses</div>
        <div class="course-footer">
          <span class="text-sm text-muted">📋 Not enrolled</span>
          <button class="btn btn-gold btn-sm" @click.stop="quickEnrol(course.courseCode)">
            + Enrol
          </button>
        </div>
      </div>
    </div>
  </div>
</div>
</div>
</template>

<script setup>
import { ref, computed, watch,onMounted} from 'vue'
import { useRoute } from 'vue-router'
import { courseService } from '../services/api.js'
import { useRole } from '../composables/useRole.js'

const route = useRoute()
const { isAdmin, isStudent, isLecturer } = useRole()

const loading  = ref(true)
const error    = ref('')
const courses  = ref([])
const search   = ref('')
const filterBy = ref('all')
const sortBy   = ref('name')
const viewMode = ref('card')
const showCreate  = ref(false)
const newCourse   = ref({ code: '', name: '' })
const createError = ref('')
const creating    = ref(false)

const COLORS = ['#e8ecf0','#c8a84b','#e8809a','#3498db','#2ecc71','#9b59b6','#1abc9c','#e67e22','#c0392b','#16a085']
const bannerColor = c => {
  const key = c.courseCode || c.code || ''
  return COLORS[key.charCodeAt(0) % COLORS.length]
}

const filteredCourses = computed(() => {
  let list = [...courses.value]
  if (search.value) list = list.filter(c =>
    (c.courseName||c.name||'').toLowerCase().includes(search.value.toLowerCase()) ||
    (c.courseCode||c.code||'').toLowerCase().includes(search.value.toLowerCase())
  )
  if (sortBy.value === 'name') list.sort((a,b) => (a.courseName||a.name||'').localeCompare(b.courseName||b.name||''))
  if (sortBy.value === 'code') list.sort((a,b) => (a.courseCode||a.code||'').localeCompare(b.courseCode||b.code||''))
  return list
})

const fetchCourses = async () => {
  loading.value = true; error.value = ''
  try {
    const res = await courseService.getMyCourses()
    courses.value = res.data.courses || res.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to load courses.'
    courses.value = []
  } finally { loading.value = false }
}


const createCourse = async () => {
  createError.value = ''; creating.value = true
  try {
    await courseService.create(newCourse.value)
    await fetchCourses()
    showCreate.value = false
    newCourse.value = { code: '', name: '' }
  } catch (e) {
    createError.value = e.response?.data?.error || 'Failed to create.'
  } finally { creating.value = false }
}

onMounted(fetchCourses)
watch(() => route.path, newPath => {
  if (newPath === '/dashboard') fetchCourses()
  fetchAllCourses()   // for students to see available courses to enrol in
})

const allCourses     = ref([])

// Courses the student is NOT yet enrolled in
const availableCourses = computed(() => {
  const enrolled = new Set(courses.value.map(c => c.courseCode || c.code))
  return allCourses.value.filter(c => !enrolled.has(c.courseCode))
})

const quickEnrol = async (courseCode) => {
  try {
    await courseService.enroll(courseCode)
    await fetchCourses()   // refresh enrolled list
  } catch (e) {
    alert(e.response?.data?.error || 'Enrolment failed.')
  }
}

// Fetch all courses for students so they can see what to enrol in
const fetchAllCourses = async () => {
  if (!isStudent.value) return
  try {
    const res = await courseService.getAll()
    allCourses.value = res.data.courses || res.data
  } catch {}
}
</script>

<style scoped>
.py-6 { padding: 32px 0 60px; }
.dash-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; }
.dash-header h1 { font-size: 30px; margin-bottom: 2px; }
.filters-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding: 12px 16px; flex-wrap: wrap; }
.filter-select { padding: 7px 12px; border: 1.5px solid var(--border); border-radius: 8px; font-family: 'DM Sans', sans-serif; font-size: 14px; color: var(--text); background: white; cursor: pointer; outline: none; }
.search-input { flex: 1; min-width: 200px; }
.view-toggle { display: flex; gap: 4px; margin-left: auto; }
.toggle-btn { width: 34px; height: 34px; border: 1.5px solid var(--border); border-radius: 6px; background: white; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; transition: all .15s; }
.toggle-btn.active { background: var(--primary-light); border-color: var(--primary); color: var(--primary); }
.courses-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.course-card { background: white; border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); border: 1px solid var(--border); cursor: pointer; overflow: hidden; transition: all .2s; }
.course-card:hover { box-shadow: var(--shadow); transform: translateY(-2px); }
.course-banner { height: 100px; position: relative; overflow: hidden; display: flex; align-items: flex-end; padding: 10px 14px; }
.banner-pattern { position: absolute; inset: 0; opacity: .3; background-image: repeating-linear-gradient(45deg, rgba(255,255,255,.3) 0, rgba(255,255,255,.3) 1px, transparent 0, transparent 50%); background-size: 20px 20px; }
.banner-code { color: white; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; text-shadow: 0 1px 4px rgba(0,0,0,.3); position: relative; }
.course-body { padding: 14px 16px 12px; }
.course-semester { font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
.course-name { display: flex; align-items: flex-start; gap: 6px; margin-bottom: 4px; font-weight: 500; font-size: 14px; color: var(--uwi-red); line-height: 1.35; }
.star { color: var(--uwi-red); font-size: 13px; flex-shrink: 0; }
.course-category { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; }
.course-footer { display: flex; align-items: center; justify-content: space-between; }
.more-btn { background: none; border: none; cursor: pointer; font-size: 18px; color: var(--text-muted); padding: 0 4px; }
.courses-list { overflow: hidden; }
.course-row { display: flex; align-items: center; gap: 14px; padding: 14px 20px; cursor: pointer; transition: background .15s; border-bottom: 1px solid var(--border); }
.course-row:last-child { border-bottom: none; }
.course-row:hover { background: var(--surface-2); }
.row-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.row-info { flex: 1; }
.row-name { font-weight: 500; font-size: 14px; }
.row-arrow { color: var(--text-muted); font-size: 20px; }
.empty-state { grid-column: 1/-1; text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state h3 { font-size: 18px; margin-bottom: 8px; }
.empty-list { padding: 40px; text-align: center; color: var(--text-muted); }
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 300; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal { background: white; border-radius: var(--radius-lg); width: 100%; max-width: 480px; box-shadow: var(--shadow-lg); }
.modal-header { padding: 20px 24px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }
.modal-header h3 { font-size: 18px; }
.close-btn { background: none; border: none; font-size: 18px; cursor: pointer; color: var(--text-muted); }
.modal-body { padding: 20px 24px; }
.modal-footer { padding: 16px 24px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 10px; }
</style>
