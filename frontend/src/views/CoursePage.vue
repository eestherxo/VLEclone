<template>
  <div class="course-page">
    <div v-if="loading" class="spinner"></div>
    <template v-else>
      <!-- Course Hero -->
      <div class="course-hero" :style="{ background: heroColor }">
        <div class="hex-overlay"></div>
        <div class="container hero-inner">
          <button class="back-btn" @click="$router.push('/dashboard')">← My Courses</button>
          <div class="hero-content">
            <span class="course-code-badge">{{ course.code }}</span>
            <h1>{{ course.name }}</h1>
            <p class="hero-meta">{{ course.semester || 'S2_2025/26' }} · COMP Undergraduate Courses</p>
            <div class="hero-actions" v-if="isStudent && !enrolled">
              <button class="btn btn-gold" @click="enrollCourse" :disabled="enrolling">
                {{ enrolling ? 'Enrolling…' : 'Enrol in Course' }}
              </button>
            </div>
            <div class="hero-actions" v-else-if="enrolled">
              <span class="badge badge-green">✓ Enrolled</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tab-bar">
        <div class="container">
          <div class="tabs">
            <button
              v-for="tab in tabs" :key="tab.key"
              :class="['tab', activeTab === tab.key && 'active']"
              @click="activeTab = tab.key"
            >
              <span>{{ tab.icon }}</span> {{ tab.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="container tab-body">

        <!-- Content -->
        <div v-if="activeTab === 'content'">
          <div class="section-header">
            <h2>Course Content</h2>
            <button v-if="isLecturer" class="btn btn-primary btn-sm" @click="showAddContent = true">+ Add Content</button>
          </div>
          <div v-if="contentLoading" class="spinner"></div>
          <div v-else-if="contentItems.length === 0" class="empty-tab">No content uploaded yet.</div>
          <div v-else>
            <div v-for="section in groupedContent" :key="section.name" class="content-section">
              <div class="section-title">📁 {{ section.name }}</div>
              <div v-for="item in section.items" :key="item.id" class="content-item">
                <span class="content-icon">{{ contentIcon(item.type) }}</span>
                <div class="content-info">
                  <div class="content-name">{{ item.title }}</div>
                  <div class="text-sm text-muted">{{ item.type }} · Added {{ formatDate(item.created_at) }}</div>
                </div>
                <a v-if="item.url" :href="item.url" target="_blank" class="btn btn-outline btn-sm">Open</a>
              </div>
            </div>
          </div>
        </div>

        <!-- Assignments -->
        <div v-if="activeTab === 'assignments'">
          <div class="section-header">
            <h2>Assignments</h2>
            <button v-if="isLecturer" class="btn btn-primary btn-sm" @click="showAddAssignment = true">+ New Assignment</button>
          </div>
          <div v-if="assignLoading" class="spinner"></div>
          <div v-else-if="assignments.length === 0" class="empty-tab">No assignments posted yet.</div>
          <div v-else class="assign-list">
            <div v-for="a in assignments" :key="a.id" class="assign-card card">
              <div class="card-body">
                <div class="flex justify-between items-center">
                  <h3 class="assign-title">{{ a.title }}</h3>
                  <span :class="['badge', dueBadge(a.due_date).class]">{{ dueBadge(a.due_date).label }}</span>
                </div>
                <p class="text-muted text-sm mt-2">{{ a.description }}</p>
                <div class="assign-footer">
                  <span class="text-sm text-muted">Due: {{ formatDate(a.due_date) }}</span>
                  <div class="flex gap-2">
                    <button v-if="isStudent" class="btn btn-primary btn-sm" @click="openSubmit(a)">Submit</button>
                    <button v-if="isLecturer" class="btn btn-outline btn-sm" @click="openGrade(a)">Grade</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Forums -->
        <div v-if="activeTab === 'forums'">
          <div class="section-header">
            <h2>Forums</h2>
            <button class="btn btn-primary btn-sm" @click="showAddForum = true">+ New Forum</button>
          </div>
          <div v-if="forumLoading" class="spinner"></div>
          <div v-else-if="forums.length === 0" class="empty-tab">No forums created yet.</div>
          <div v-else class="forum-list">
            <div
              v-for="f in forums" :key="f.id"
              class="forum-item card"
              @click="$router.push(`/course/${courseId}/forums/${f.id}`)"
            >
              <div class="card-body flex items-center gap-3">
                <div class="forum-icon">💬</div>
                <div class="flex-1">
                  <div class="forum-name">{{ f.name || f.title }}</div>
                  <div class="text-sm text-muted">{{ f.thread_count || 0 }} threads</div>
                </div>
                <span class="row-arrow">›</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Members -->
        <div v-if="activeTab === 'members'">
          <div class="section-header"><h2>Course Members</h2></div>
          <div v-if="membersLoading" class="spinner"></div>
          <div v-else class="members-grid">
            <div v-for="m in members" :key="m.id" class="member-card card card-body">
              <div class="member-avatar">{{ m.username.slice(0,2).toUpperCase() }}</div>
              <div class="member-name">{{ m.username }}</div>
              <span :class="['badge', m.role === 'lecturer' ? 'badge-gold' : 'badge-blue']">{{ m.role }}</span>
            </div>
          </div>
        </div>

        <!-- Calendar -->
        <div v-if="activeTab === 'calendar'">
          <div class="section-header">
            <h2>Calendar Events</h2>
            <button v-if="isLecturer || isAdmin" class="btn btn-primary btn-sm" @click="showAddEvent = true">+ Add Event</button>
          </div>
          <div v-if="eventsLoading" class="spinner"></div>
          <div v-else-if="events.length === 0" class="empty-tab">No events scheduled.</div>
          <div v-else class="events-list">
            <div v-for="e in events" :key="e.id" class="event-item card card-body flex gap-3 items-center">
              <div class="event-date-box">
                <div class="event-month">{{ eventMonth(e.date) }}</div>
                <div class="event-day">{{ eventDay(e.date) }}</div>
              </div>
              <div>
                <div class="font-medium">{{ e.title }}</div>
                <div class="text-sm text-muted">{{ e.description }}</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </template>

    <!-- Submit Assignment Modal -->
    <div v-if="showSubmit" class="modal-backdrop" @click.self="showSubmit = false">
      <div class="modal">
        <div class="modal-header"><h3>Submit: {{ selectedAssignment?.title }}</h3><button class="close-btn" @click="showSubmit = false">✕</button></div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Submission Link / Notes</label>
            <textarea v-model="submission.content" class="form-control" rows="4" placeholder="Paste your link or write your submission notes…"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showSubmit = false">Cancel</button>
          <button class="btn btn-primary" @click="submitAssignment">Submit</button>
        </div>
      </div>
    </div>

    <!-- Add Forum Modal -->
    <div v-if="showAddForum" class="modal-backdrop" @click.self="showAddForum = false">
      <div class="modal">
        <div class="modal-header"><h3>Create Forum</h3><button class="close-btn" @click="showAddForum = false">✕</button></div>
        <div class="modal-body">
          <div class="form-group"><label class="form-label">Forum Title</label><input v-model="newForum.title" class="form-control" placeholder="e.g. Week 1 Discussion" /></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showAddForum = false">Cancel</button>
          <button class="btn btn-primary" @click="createForum">Create</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { courseService, assignmentService, contentService, forumService, eventService } from '../services/api.js'

const route = useRoute()
const courseId = computed(() => route.params.id)

const loading = ref(true)
const course = ref({})
const enrolled = ref(false)
const enrolling = ref(false)

const user = computed(() => JSON.parse(localStorage.getItem('user') || 'null'))
const isStudent = computed(() => user.value?.role === 'student')
const isLecturer = computed(() => user.value?.role === 'lecturer')
const isAdmin = computed(() => user.value?.role === 'admin')

const COLORS = ['#3a6186','#89216b','#1c6c3a','#7b4397','#c0392b','#16a085']
const heroColor = computed(() => COLORS[courseId.value % COLORS.length])

const tabs = [
  { key: 'content', label: 'Course Content', icon: '📖' },
  { key: 'assignments', label: 'Assignments', icon: '📝' },
  { key: 'forums', label: 'Forums', icon: '💬' },
  { key: 'members', label: 'Members', icon: '👥' },
  { key: 'calendar', label: 'Calendar', icon: '📅' },
]
const activeTab = ref('content')

// Content
const contentItems = ref([])
const contentLoading = ref(false)
const showAddContent = ref(false)
const groupedContent = computed(() => {
  const sections = {}
  contentItems.value.forEach(item => {
    const s = item.section || 'General'
    if (!sections[s]) sections[s] = { name: s, items: [] }
    sections[s].items.push(item)
  })
  return Object.values(sections)
})

// Assignments
const assignments = ref([])
const assignLoading = ref(false)
const showAddAssignment = ref(false)
const showSubmit = ref(false)
const selectedAssignment = ref(null)
const submission = ref({ content: '' })

// Forums
const forums = ref([])
const forumLoading = ref(false)
const showAddForum = ref(false)
const newForum = ref({ title: '' })

// Members
const members = ref([])
const membersLoading = ref(false)

// Events
const events = ref([])
const eventsLoading = ref(false)
const showAddEvent = ref(false)

const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-JM', { year: 'numeric', month: 'short', day: 'numeric' }) : '—'
const contentIcon = (type) => ({ link: '🔗', file: '📄', slide: '📊', video: '🎥' }[type] || '📄')
const eventMonth = (d) => d ? new Date(d).toLocaleString('default', { month: 'short' }).toUpperCase() : ''
const eventDay = (d) => d ? new Date(d).getDate() : ''
const dueBadge = (due) => {
  if (!due) return { class: 'badge-grey', label: 'No due date' }
  const diff = new Date(due) - new Date()
  if (diff < 0) return { class: 'badge-red', label: 'Overdue' }
  if (diff < 86400000 * 3) return { class: 'badge-gold', label: 'Due soon' }
  return { class: 'badge-green', label: 'Upcoming' }
}

const openSubmit = (a) => { selectedAssignment.value = a; showSubmit.value = true }
const submitAssignment = async () => {
  try {
    await assignmentService.submit(selectedAssignment.value.id, submission.value)
    showSubmit.value = false
    submission.value = { content: '' }
    alert('Assignment submitted!')
  } catch (e) { alert('Submission failed.') }
}

const enrollCourse = async () => {
  enrolling.value = true
  try {
    await courseService.register(courseId.value)
    enrolled.value = true
  } catch (e) { alert('Enrollment failed.') }
  finally { enrolling.value = false }
}

const createForum = async () => {
  try {
    const res = await forumService.create({ ...newForum.value, course_id: courseId.value })
    forums.value.push(res.data)
    showAddForum.value = false
    newForum.value = { title: '' }
  } catch (e) { alert('Failed to create forum.') }
}

const loadTab = async (tab) => {
  if (tab === 'content' && !contentItems.value.length) {
    contentLoading.value = true
    try { const r = await contentService.getByCourse(courseId.value); contentItems.value = r.data } catch {}
    contentLoading.value = false
  }
  if (tab === 'assignments' && !assignments.value.length) {
    assignLoading.value = true
    try { const r = await assignmentService.getByCourse(courseId.value); assignments.value = r.data } catch {}
    assignLoading.value = false
  }
  if (tab === 'forums' && !forums.value.length) {
    forumLoading.value = true
    try { const r = await forumService.getByCourse(courseId.value); forums.value = r.data } catch {}
    forumLoading.value = false
  }
  if (tab === 'members' && !members.value.length) {
    membersLoading.value = true
    try { const r = await courseService.getMembers(courseId.value); members.value = r.data } catch {}
    membersLoading.value = false
  }
  if (tab === 'calendar' && !events.value.length) {
    eventsLoading.value = true
    try { const r = await eventService.getByCourse(courseId.value); events.value = r.data } catch {}
    eventsLoading.value = false
  }
}

watch(activeTab, loadTab)

onMounted(async () => {
  try {
    const r = await courseService.getById(courseId.value)
    course.value = r.data
    enrolled.value = r.data.enrolled ?? true
  } catch {
    course.value = { code: 'COMP3161', name: 'Introduction to Database Management Systems', semester: 'S2_2025/26' }
  } finally {
    loading.value = false
  }
  loadTab('content')
})
</script>

<style scoped>
.course-hero {
  position: relative; padding: calc(var(--nav-height) + 24px) 0 32px; overflow: hidden;
}
.hex-overlay {
  position: absolute; inset: 0; opacity: .12;
  background-image: url("data:image/svg+xml,%3Csvg width='56' height='100' viewBox='0 0 56 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M28 66L0 50V16L28 0l28 16v34z' fill='none' stroke='%23fff' stroke-width='1.5'/%3E%3C/svg%3E");
  background-size: 56px 100px;
}
.hero-inner { position: relative; }
.back-btn { background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.3); color: white; border-radius: 8px; padding: 6px 14px; font-size: 13px; cursor: pointer; margin-bottom: 16px; font-family: 'DM Sans', sans-serif; transition: background .15s; }
.back-btn:hover { background: rgba(255,255,255,.25); }
.course-code-badge { display: inline-block; background: rgba(255,255,255,.2); color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; letter-spacing: .5px; margin-bottom: 10px; }
.hero-content h1 { font-size: 28px; color: white; margin-bottom: 6px; text-shadow: 0 2px 8px rgba(0,0,0,.2); }
.hero-meta { color: rgba(255,255,255,.75); font-size: 14px; margin-bottom: 16px; }
.hero-actions { display: flex; gap: 10px; align-items: center; }

.tab-bar { background: white; border-bottom: 1px solid var(--border); position: sticky; top: var(--nav-height); z-index: 40; }
.tabs { display: flex; gap: 0; overflow-x: auto; }
.tab {
  padding: 14px 18px; background: none; border: none; cursor: pointer;
  font-family: 'DM Sans', sans-serif; font-size: 14px; font-weight: 500;
  color: var(--text-muted); border-bottom: 3px solid transparent;
  transition: all .15s; white-space: nowrap; display: flex; align-items: center; gap: 6px;
}
.tab:hover { color: var(--text); background: var(--surface-2); }
.tab.active { color: var(--primary); border-bottom-color: var(--primary); }

.tab-body { padding: 28px 0 60px; }

.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.section-header h2 { font-size: 20px; }

.empty-tab { text-align: center; color: var(--text-muted); padding: 48px 0; font-size: 15px; }

/* Content */
.content-section { margin-bottom: 28px; }
.section-title { font-weight: 600; font-size: 14px; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
.content-item { display: flex; align-items: center; gap: 14px; padding: 12px 16px; background: white; border-radius: var(--radius); border: 1px solid var(--border); margin-bottom: 8px; }
.content-icon { font-size: 20px; }
.content-info { flex: 1; }
.content-name { font-weight: 500; font-size: 14px; }

/* Assignments */
.assign-list { display: flex; flex-direction: column; gap: 14px; }
.assign-title { font-size: 16px; }
.assign-footer { display: flex; align-items: center; justify-content: space-between; margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--border); }

/* Forums */
.forum-list { display: flex; flex-direction: column; gap: 10px; }
.forum-item { cursor: pointer; transition: box-shadow .15s; }
.forum-item:hover { box-shadow: var(--shadow); }
.forum-icon { font-size: 24px; }
.forum-name { font-weight: 500; }
.row-arrow { color: var(--text-muted); font-size: 22px; }

/* Members */
.members-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px; }
.member-card { display: flex; flex-direction: column; align-items: center; gap: 8px; text-align: center; }
.member-avatar {
  width: 48px; height: 48px; border-radius: 50%; background: var(--uwi-green);
  color: white; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 16px;
}
.member-name { font-size: 13px; font-weight: 500; }

/* Events */
.events-list { display: flex; flex-direction: column; gap: 10px; }
.event-item { margin-bottom: 0; }
.event-date-box { min-width: 52px; text-align: center; background: var(--primary-light); border-radius: 8px; padding: 6px; }
.event-month { font-size: 10px; font-weight: 700; color: var(--primary); text-transform: uppercase; }
.event-day { font-size: 22px; font-weight: 700; color: var(--primary); line-height: 1; }

/* Modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 300; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal { background: white; border-radius: var(--radius-lg); width: 100%; max-width: 480px; box-shadow: var(--shadow-lg); }
.modal-header { padding: 20px 24px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }
.modal-header h3 { font-size: 17px; }
.close-btn { background: none; border: none; font-size: 18px; cursor: pointer; color: var(--text-muted); }
.modal-body { padding: 20px 24px; }
.modal-footer { padding: 16px 24px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 10px; }
</style>
