<template>
  <div class="dashboard">
    <div class="container py-6">

      <!-- Header -->
      <div class="dash-header">
        <div>
          <h1>My courses</h1>
          <p class="text-muted">Course overview</p>
        </div>
        <button v-if="isAdmin" class="btn btn-primary" @click="showCreate = true">+ New Course</button>
      </div>

      <!-- Filters bar -->
      <div class="filters-bar card card-body">
        <select v-model="filterStarred" class="filter-select">
          <option value="all">All courses</option>
          <option value="starred">Starred</option>
        </select>
        <input v-model="search" class="form-control search-input" placeholder="🔍  Search courses…" />
        <select v-model="sortBy" class="filter-select">
          <option value="name">Sort by name</option>
          <option value="code">Sort by code</option>
        </select>
        <div class="view-toggle">
          <button :class="['toggle-btn', viewMode==='card' && 'active']" @click="viewMode='card'">⊞</button>
          <button :class="['toggle-btn', viewMode==='list' && 'active']" @click="viewMode='list'">☰</button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="spinner"></div>

      <!-- Error -->
      <div v-else-if="error" class="alert alert-error">{{ error }}</div>

      <!-- Card grid view -->
      <div v-else-if="viewMode === 'card'" class="courses-grid">
        <div
          v-for="course in filteredCourses" :key="course.id"
          class="course-card"
          @click="$router.push(`/course/${course.id}`)"
        >
          <div class="course-banner" :style="{ background: course.color || bannerColor(course.id) }">
            <div class="banner-pattern"></div>
            <div class="banner-code">{{ course.code }}</div>
          </div>
          <div class="course-body">
            <div class="course-semester">{{ course.code }} | {{ course.semester || 'S2_2025/26' }}</div>
            <div class="course-name">
              <span class="star">★</span>
              <a href="#" @click.prevent>{{ course.name }}</a>
            </div>
            <div class="course-category">COMP Undergraduate Courses</div>
            <div class="course-footer">
              <span v-if="course.progress !== undefined" class="progress-label">{{ course.progress }}% complete</span>
              <button class="more-btn">⋮</button>
            </div>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="filteredCourses.length === 0" class="empty-state">
          <div class="empty-icon">📚</div>
          <h3>No courses found</h3>
          <p>Try adjusting your search or filters.</p>
        </div>
      </div>

      <!-- List view -->
      <div v-else class="courses-list card">
        <div v-for="course in filteredCourses" :key="course.id" class="course-row" @click="$router.push(`/course/${course.id}`)">
          <div class="row-dot" :style="{ background: course.color || bannerColor(course.id) }"></div>
          <div class="row-info">
            <div class="row-name">{{ course.name }}</div>
            <div class="row-code text-muted text-sm">{{ course.code }} · {{ course.semester || 'S2_2025/26' }}</div>
          </div>
          <span class="badge badge-green">Enrolled</span>
          <span class="row-arrow">›</span>
        </div>
      </div>

    </div>

    <!-- Create Course Modal -->
    <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Create New Course</h3>
          <button class="close-btn" @click="showCreate = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="createError" class="alert alert-error">{{ createError }}</div>
          <div class="form-group">
            <label class="form-label">Course Name</label>
            <input v-model="newCourse.name" class="form-control" placeholder="e.g. Introduction to Database Management" />
          </div>
          <div class="form-group">
            <label class="form-label">Course Code</label>
            <input v-model="newCourse.code" class="form-control" placeholder="e.g. COMP3161" />
          </div>
          <div class="form-group">
            <label class="form-label">Description</label>
            <textarea v-model="newCourse.description" class="form-control" rows="3" placeholder="Course description…"></textarea>
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

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { courseService } from '../services/api.js'

const loading = ref(true)
const error = ref('')
const courses = ref([])
const search = ref('')
const filterStarred = ref('all')
const sortBy = ref('name')
const viewMode = ref('card')
const showCreate = ref(false)
const newCourse = ref({ name: '', code: '', description: '' })
const createError = ref('')
const creating = ref(false)

const user = computed(() => JSON.parse(localStorage.getItem('user') || 'null'))
const isAdmin = computed(() => user.value?.role === 'admin')

const COLORS = ['#e8ecf0','#c8a84b','#e8809a','#3498db','#2ecc71','#9b59b6','#1abc9c','#e67e22']
const bannerColor = (id) => COLORS[id % COLORS.length]

const filteredCourses = computed(() => {
  let list = [...courses.value]
  if (search.value) list = list.filter(c => c.name.toLowerCase().includes(search.value.toLowerCase()) || c.code.toLowerCase().includes(search.value.toLowerCase()))
  if (sortBy.value === 'name') list.sort((a, b) => a.name.localeCompare(b.name))
  if (sortBy.value === 'code') list.sort((a, b) => a.code.localeCompare(b.code))
  return list
})

const createCourse = async () => {
  createError.value = ''
  creating.value = true
  try {
    const res = await courseService.create(newCourse.value)
    courses.value.unshift(res.data)
    showCreate.value = false
    newCourse.value = { name: '', code: '', description: '' }
  } catch (e) {
    createError.value = e.response?.data?.message || 'Failed to create course.'
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  try {
    const res = await courseService.getMyCourses()
    courses.value = res.data
  } catch (e) {
    error.value = 'Failed to load courses. Make sure your backend is running.'
    // Demo data fallback
    courses.value = [
      { id: 1, code: 'BIOC1016', name: 'Anti-Doping in Sports', semester: 'S2_2025/26', progress: 0, color: '#e8ecf0' },
      { id: 2, code: 'COMP2211', name: 'Analysis of Algorithms', semester: 'S2_2025/26', color: '#c8a84b' },
      { id: 3, code: 'COMP2340', name: 'Computer Systems Organization', semester: 'S2_2025/26', color: '#e8809a' },
      { id: 4, code: 'COMP3161', name: 'Introduction to Database Management Systems', semester: 'S2_2025/26', color: '#3498db' },
      { id: 5, code: 'INFO3180', name: 'Dynamic Web Development II', semester: 'S2_2025/26', color: '#2ecc71' },
    ]
    error.value = ''
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard { min-height: 100vh; }
.py-6 { padding: 32px 0 60px; }

.dash-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: 24px;
}
.dash-header h1 { font-size: 30px; color: var(--text); margin-bottom: 2px; }

.filters-bar {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 24px; padding: 12px 16px; flex-wrap: wrap;
}
.filter-select {
  padding: 7px 12px; border: 1.5px solid var(--border); border-radius: 8px;
  font-family: 'DM Sans', sans-serif; font-size: 14px; color: var(--text);
  background: white; cursor: pointer; outline: none;
}
.search-input { flex: 1; min-width: 200px; }
.view-toggle { display: flex; gap: 4px; margin-left: auto; }
.toggle-btn {
  width: 34px; height: 34px; border: 1.5px solid var(--border);
  border-radius: 6px; background: white; cursor: pointer; font-size: 16px;
  display: flex; align-items: center; justify-content: center; transition: all .15s;
}
.toggle-btn.active { background: var(--primary-light); border-color: var(--primary); color: var(--primary); }

/* Cards */
.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}
.course-card {
  background: white; border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm); border: 1px solid var(--border);
  cursor: pointer; overflow: hidden; transition: all .2s;
}
.course-card:hover { box-shadow: var(--shadow); transform: translateY(-2px); }

.course-banner {
  height: 100px; position: relative; overflow: hidden;
  display: flex; align-items: flex-end; padding: 10px 14px;
}
.banner-pattern {
  position: absolute; inset: 0; opacity: .3;
  background-image: repeating-linear-gradient(45deg, rgba(255,255,255,.3) 0, rgba(255,255,255,.3) 1px, transparent 0, transparent 50%);
  background-size: 20px 20px;
}
.banner-code { color: white; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; text-shadow: 0 1px 4px rgba(0,0,0,.3); position: relative; }

.course-body { padding: 14px 16px 12px; }
.course-semester { font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
.course-name { display: flex; align-items: flex-start; gap: 6px; margin-bottom: 4px; }
.course-name a { color: var(--uwi-red); font-weight: 500; font-size: 14px; line-height: 1.35; text-decoration: none; }
.course-name a:hover { text-decoration: underline; }
.star { color: var(--uwi-red); font-size: 13px; margin-top: 2px; }
.course-category { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; }
.course-footer { display: flex; align-items: center; justify-content: space-between; }
.progress-label { font-size: 12px; color: var(--text-muted); }
.more-btn { background: none; border: none; cursor: pointer; font-size: 18px; color: var(--text-muted); padding: 0 4px; }

/* List */
.courses-list { overflow: hidden; }
.course-row {
  display: flex; align-items: center; gap: 14px; padding: 14px 20px;
  cursor: pointer; transition: background .15s; border-bottom: 1px solid var(--border);
}
.course-row:last-child { border-bottom: none; }
.course-row:hover { background: var(--surface-2); }
.row-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.row-info { flex: 1; }
.row-name { font-weight: 500; font-size: 14px; }
.row-arrow { color: var(--text-muted); font-size: 20px; }

/* Empty */
.empty-state { grid-column: 1/-1; text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state h3 { font-size: 18px; margin-bottom: 8px; }
.empty-state p { color: var(--text-muted); }

/* Modal */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 300;
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.modal { background: white; border-radius: var(--radius-lg); width: 100%; max-width: 480px; box-shadow: var(--shadow-lg); }
.modal-header { padding: 20px 24px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }
.modal-header h3 { font-size: 18px; }
.close-btn { background: none; border: none; font-size: 18px; cursor: pointer; color: var(--text-muted); }
.modal-body { padding: 20px 24px; }
.modal-footer { padding: 16px 24px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 10px; }
</style>
