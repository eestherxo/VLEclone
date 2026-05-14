<template>
  <div class="dashboard">
    <div class="container py-6">

      <div class="dash-header">
        <div>
          <h1 v-if="isStudent">Browse Courses</h1>
          <h1 v-else-if="isLecturer">My Courses</h1>
          <h1 v-else-if="isAdmin">Manage Courses</h1>
          <p class="text-muted">
            <span v-if="isStudent">Enrol in courses available to you</span>
            <span v-else-if="isLecturer">Courses you are assigned to teach</span>
            <span v-else-if="isAdmin">Create, view and remove courses</span>
          </p>
        </div>
        <button v-if="isAdmin" class="btn btn-primary" @click="showCreate = true">+ New Course</button>
      </div>

      <div class="filters-bar card card-body">
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

      <!-- ── STUDENT: unenrolled courses ── -->
      <template v-else-if="isStudent">
        <div v-if="viewMode === 'card'" class="courses-grid">
          <div v-for="course in filteredCourses" :key="course.courseCode"
            class="course-card"
            @click="$router.push(`/course/${course.courseCode}`)">
            <div class="course-banner" :style="{ background: bannerColor(course) }">
              <div class="banner-pattern"></div>
              <div class="banner-code">{{ course.courseCode }}</div>
            </div>
            <div class="course-body">
              <div class="course-semester">{{ course.courseCode }} | S2_2025/26</div>
              <div class="course-name"><span class="star">★</span><span>{{ course.courseName }}</span></div>
              <div class="course-category">Available to enrol</div>
              <div class="course-footer">
                <span class="text-sm text-muted">📋 Not enrolled</span>
                <button class="btn btn-gold btn-sm" @click.stop="quickEnrol(course.courseCode)">
                  + Enrol
                </button>
              </div>
            </div>
          </div>
          <div v-if="filteredCourses.length === 0" class="empty-state">
            <div class="empty-icon">🎉</div>
            <h3>You're enrolled in all available courses!</h3>
          </div>
        </div>

        <div v-else class="courses-list card">
          <div v-for="course in filteredCourses" :key="course.courseCode" class="course-row">
            <div class="row-dot" :style="{ background: bannerColor(course) }"></div>
            <div class="row-info" @click="$router.push(`/course/${course.courseCode}`)">
              <div class="row-name">{{ course.courseName }}</div>
              <div class="row-code text-muted text-sm">{{ course.courseCode }} · S2_2025/26</div>
            </div>
            <button class="btn btn-gold btn-sm" @click="quickEnrol(course.courseCode)">+ Enrol</button>
            <span class="row-arrow" @click="$router.push(`/course/${course.courseCode}`)">›</span>
          </div>
          <div v-if="!filteredCourses.length" class="empty-list">No unenrolled courses found.</div>
        </div>
      </template>

      <!-- ── LECTURER: assigned courses ── -->
      <template v-else-if="isLecturer">
        <div v-if="viewMode === 'card'" class="courses-grid">
          <div v-for="course in filteredCourses" :key="course.courseCode || course.code"
            class="course-card"
            @click="$router.push(`/course/${course.courseCode || course.code}`)">
            <div class="course-banner" :style="{ background: bannerColor(course) }">
              <div class="banner-pattern"></div>
              <div class="banner-code">{{ course.courseCode || course.code }}</div>
            </div>
            <div class="course-body">
              <div class="course-semester">{{ course.courseCode || course.code }} | S2_2025/26</div>
              <div class="course-name"><span class="star">★</span><span>{{ course.courseName || course.name }}</span></div>
              <div class="course-category">COMP Undergraduate Courses</div>
              <div class="course-footer">
                <span class="text-sm text-muted">🎓 Teaching</span>
                <button class="more-btn" @click.stop>⋮</button>
              </div>
            </div>
          </div>
          <div v-if="filteredCourses.length === 0" class="empty-state">
            <div class="empty-icon">📚</div>
            <h3>No courses assigned yet.</h3>
          </div>
        </div>

        <div v-else class="courses-list card">
          <div v-for="course in filteredCourses" :key="course.courseCode||course.code"
            class="course-row"
            @click="$router.push(`/course/${course.courseCode||course.code}`)">
            <div class="row-dot" :style="{ background: bannerColor(course) }"></div>
            <div class="row-info">
              <div class="row-name">{{ course.courseName || course.name }}</div>
              <div class="row-code text-muted text-sm">{{ course.courseCode || course.code }} · S2_2025/26</div>
            </div>
            <span class="badge badge-blue">Teaching</span>
            <span class="row-arrow">›</span>
          </div>
          <div v-if="!filteredCourses.length" class="empty-list">No courses found.</div>
        </div>
      </template>

      <!-- ── ADMIN: all courses with delete ── -->
      <template v-else-if="isAdmin">
        <div v-if="viewMode === 'card'" class="courses-grid">
          <div v-for="course in filteredCourses" :key="course.courseCode || course.code"
            class="course-card">
            <div class="course-banner" :style="{ background: bannerColor(course) }"
              @click="$router.push(`/course/${course.courseCode || course.code}`)">
              <div class="banner-pattern"></div>
              <div class="banner-code">{{ course.courseCode || course.code }}</div>
            </div>
            <div class="course-body">
              <div class="course-semester">{{ course.courseCode || course.code }} | S2_2025/26</div>
              <div class="course-name" @click="$router.push(`/course/${course.courseCode || course.code}`)">
                <span class="star">★</span><span>{{ course.courseName || course.name }}</span>
              </div>
              <div class="course-category">COMP Undergraduate Courses</div>
              <div class="course-footer">
                <span class="text-sm text-muted">⚙️ Admin</span>
                <button class="btn btn-danger btn-sm" @click.stop="confirmDelete(course)">🗑 Delete</button>
              </div>
            </div>
          </div>
          <div v-if="filteredCourses.length === 0" class="empty-state">
            <div class="empty-icon">📚</div>
            <h3>No courses yet.</h3>
          </div>
        </div>

        <div v-else class="courses-list card">
          <div v-for="course in filteredCourses" :key="course.courseCode||course.code" class="course-row">
            <div class="row-dot" :style="{ background: bannerColor(course) }"></div>
            <div class="row-info" @click="$router.push(`/course/${course.courseCode||course.code}`)">
              <div class="row-name">{{ course.courseName || course.name }}</div>
              <div class="row-code text-muted text-sm">{{ course.courseCode || course.code }} · S2_2025/26</div>
            </div>
            <button class="btn btn-danger btn-sm" @click="confirmDelete(course)">🗑 Delete</button>
            <span class="row-arrow" @click="$router.push(`/course/${course.courseCode||course.code}`)">›</span>
          </div>
          <div v-if="!filteredCourses.length" class="empty-list">No courses found.</div>
        </div>
      </template>

    </div>

    <!-- Create Course Modal (admin only) -->
    <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Create New Course</h3>
          <button class="close-btn" @click="showCreate = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="createError" class="alert alert-error">{{ createError }}</div>
          <div class="form-group">
            <label class="form-label">Course Code</label>
            <input v-model="newCourse.code" class="form-control" placeholder="e.g. COMP3161" />
          </div>
          <div class="form-group">
            <label class="form-label">Course Name</label>
            <input v-model="newCourse.name" class="form-control" placeholder="e.g. Introduction to Database Management" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showCreate = false">Cancel</button>
          <button class="btn btn-primary" @click="createCourse" :disabled="creating">
            {{ creating ? 'Creating…' : 'Create Course' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm Modal (admin only) -->
    <div v-if="showDelete" class="modal-backdrop" @click.self="showDelete = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Delete Course</h3>
          <button class="close-btn" @click="showDelete = false">✕</button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ deletingCourse?.courseCode || deletingCourse?.code }}</strong> — {{ deletingCourse?.courseName || deletingCourse?.name }}?</p>
          <p class="text-muted text-sm" style="margin-top:8px">This action cannot be undone.</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showDelete = false">Cancel</button>
          <button class="btn btn-danger" @click="deleteCourse" :disabled="deleting">
            {{ deleting ? 'Deleting…' : 'Delete Course' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { courseService } from '../services/api.js'
import { useRole } from '../composables/useRole.js'

const route = useRoute()
const { isAdmin, isStudent, isLecturer } = useRole()
const user = computed(() => JSON.parse(localStorage.getItem('user') || 'null'))

const loading  = ref(true)
const error    = ref('')
const courses  = ref([])   // enrolled (student) or assigned (lecturer) or all (admin)
const enrolled = ref([])   // student's enrolled course codes
const search   = ref('')
const sortBy   = ref('name')
const viewMode = ref('card')

// Create
const showCreate  = ref(false)
const newCourse   = ref({ code: '', name: '' })
const createError = ref('')
const creating    = ref(false)

// Delete
const showDelete    = ref(false)
const deletingCourse= ref(null)
const deleting      = ref(false)

const COLORS = ['#e8ecf0','#c8a84b','#e8809a','#3498db','#2ecc71','#9b59b6','#1abc9c','#e67e22','#c0392b','#16a085']
const bannerColor = c => {
  const key = c.courseCode || c.code || ''
  return COLORS[key.charCodeAt(0) % COLORS.length]
}

// For students: show only courses NOT yet enrolled in
const filteredCourses = computed(() => {
  let list = [...courses.value]
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(c =>
      (c.courseName||c.name||'').toLowerCase().includes(q) ||
      (c.courseCode||c.code||'').toLowerCase().includes(q)
    )
  }
  if (sortBy.value === 'name') list.sort((a,b) => (a.courseName||a.name||'').localeCompare(b.courseName||b.name||''))
  if (sortBy.value === 'code') list.sort((a,b) => (a.courseCode||a.code||'').localeCompare(b.courseCode||b.code||''))
  return list
})

const fetchCourses = async () => {
  loading.value = true; error.value = ''
  try {
    if (isStudent.value) {
      // fetch all courses AND enrolled courses, then subtract
      const [allRes, enrolledRes] = await Promise.all([
        courseService.getAll(),
        courseService.getMyCourses(),
      ])
      const all      = allRes.data.courses      || allRes.data
      const myList   = enrolledRes.data.courses || enrolledRes.data
      enrolled.value = new Set(myList.map(c => c.courseCode || c.code))
      courses.value  = all.filter(c => !enrolled.value.has(c.courseCode || c.code))
    } else if (isLecturer.value) {
      const res = await courseService.getMyCourses()
      courses.value = res.data.courses || res.data
    } else if (isAdmin.value) {
      const res = await courseService.getAll()
      courses.value = res.data.courses || res.data
    }
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

const confirmDelete = (course) => {
  deletingCourse.value = course
  showDelete.value = true
}

const deleteCourse = async () => {
  deleting.value = true
  try {
    await courseService.remove(deletingCourse.value.courseCode || deletingCourse.value.code)
    await fetchCourses()
    showDelete.value = false
    deletingCourse.value = null
  } catch (e) {
    alert(e.response?.data?.error || 'Failed to delete course.')
  } finally { deleting.value = false }
}

const quickEnrol = async (courseCode) => {
  try {
    await courseService.enroll(courseCode)
    await fetchCourses()  // removes the course from the unenrolled list
  } catch (e) {
    alert(e.response?.data?.error || 'Enrolment failed.')
  }
}

onMounted(fetchCourses)
watch(() => route.path, p => { if (p === '/dashboard') fetchCourses() })
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
.course-card { background: white; border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); border: 1px solid var(--border); overflow: hidden; transition: all .2s; }
.course-card:hover { box-shadow: var(--shadow); transform: translateY(-2px); }
.course-banner { height: 100px; position: relative; overflow: hidden; display: flex; align-items: flex-end; padding: 10px 14px; cursor: pointer; }
.banner-pattern { position: absolute; inset: 0; opacity: .3; background-image: repeating-linear-gradient(45deg, rgba(255,255,255,.3) 0, rgba(255,255,255,.3) 1px, transparent 0, transparent 50%); background-size: 20px 20px; }
.banner-code { color: white; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; text-shadow: 0 1px 4px rgba(0,0,0,.3); position: relative; }
.course-body { padding: 14px 16px 12px; }
.course-semester { font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
.course-name { display: flex; align-items: flex-start; gap: 6px; margin-bottom: 4px; font-weight: 500; font-size: 14px; color: var(--uwi-red); line-height: 1.35; cursor: pointer; }
.star { color: var(--uwi-red); font-size: 13px; flex-shrink: 0; }
.course-category { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; }
.course-footer { display: flex; align-items: center; justify-content: space-between; }
.more-btn { background: none; border: none; cursor: pointer; font-size: 18px; color: var(--text-muted); padding: 0 4px; }
.btn-danger { background: #e74c3c; color: white; border: none; }
.btn-danger:hover { background: #c0392b; }
.courses-list { overflow: hidden; }
.course-row { display: flex; align-items: center; gap: 14px; padding: 14px 20px; transition: background .15s; border-bottom: 1px solid var(--border); }
.course-row:last-child { border-bottom: none; }
.course-row:hover { background: var(--surface-2); }
.row-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.row-info { flex: 1; cursor: pointer; }
.row-name { font-weight: 500; font-size: 14px; }
.row-arrow { color: var(--text-muted); font-size: 20px; cursor: pointer; }
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