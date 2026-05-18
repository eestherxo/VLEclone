<template>
  <div class="course-page">
    <div v-if="loading" class="spinner"></div>
    <template v-else>

      <!-- Hero -->
      <div class="course-hero" :style="{ background: heroColor }">
        <div class="hex-overlay"></div>
        <div class="container hero-inner">
          <button class="back-btn" @click="$router.push('/dashboard')">← My Courses</button>
          <div class="hero-content">
            <span class="course-code-badge">{{ course.courseCode || course.code }}</span>
            <h1>{{ course.courseName || course.name }}</h1>
            <div class="hero-meta-row">
              <span v-if="isAdmin" class="role-chip admin">⚙️ Admin · Lecturer</span>
              <span v-else-if="isLecturer" class="role-chip lecturer">🎓 Lecturer</span>
              <span v-else class="role-chip student">📚 Student</span>
            </div>
            <div class="hero-actions" v-if="isStudent && !enrolled">
              <button class="btn btn-gold" @click="enrollCourse" :disabled="enrolling">
                {{ enrolling ? 'Enrolling…' : '+ Enrol in Course' }}
              </button>
            </div>
            <div v-else-if="isStudent">
              <span class="badge badge-green">✓ Enrolled</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tab-bar">
        <div class="container">
          <div class="tabs">
            <button v-for="tab in visibleTabs" :key="tab.key"
              :class="['tab', activeTab === tab.key && 'active']"
              @click="activeTab = tab.key; loadTab(tab.key)">
              {{ tab.icon }} {{ tab.label }}
            </button>
          </div>
        </div>
      </div>

      <div class="container tab-body">

        <!-- CONTENT TAB -->
        <div v-if="activeTab === 'content'">
          <div class="section-header">
            <h2>Course Content</h2>
            <button v-if="canManageCourse" class="btn btn-primary btn-sm" @click="showAddContent = true">+ Add Content</button>
          </div>
          <div v-if="contentLoading" class="spinner"></div>
          <div v-else-if="!contentItems.length" class="empty-tab">
            <div class="empty-icon">📖</div>
            <p>No content uploaded yet{{ canManageCourse ? ' — add some using the button above.' : '.' }}</p>
          </div>
          <div v-else>
            <div v-for="section in groupedContent" :key="section.name" class="content-section">
              <div class="section-label">📁 {{ section.name }}</div>
              <div v-for="item in section.items" :key="item.id" class="content-item">
                <span class="content-icon">{{ contentIcon(item.type) }}</span>
                <div class="content-info">
                  <div class="content-name">{{ item.title }}</div>
                  <div class="text-sm text-muted">{{ item.type }}</div>
                </div>
                <a v-if="item.url" :href="item.url" target="_blank" class="btn btn-outline btn-sm">Open</a>
              </div>
            </div>
          </div>
        </div>

        <!-- ASSIGNMENTS TAB -->
        <div v-if="activeTab === 'assignments'">
          <div class="section-header">
            <h2>Assignments</h2>
            <button v-if="canManageCourse" class="btn btn-primary btn-sm" @click="showAddAssignment = true">+ New Assignment</button>
          </div>

          <!-- Grade summary for students -->
          <div v-if="isStudent && assignments.length" class="grade-bar">
            <div class="grade-stat">
              <div class="grade-val">{{ avgGrade }}%</div>
              <div class="grade-label">Average</div>
            </div>
            <div class="grade-stat">
              <div class="grade-val">{{ submittedCount }}/{{ assignments.length }}</div>
              <div class="grade-label">Submitted</div>
            </div>
            <div class="grade-progress-wrap">
              <div class="progress-bar"><div class="progress-fill" :style="{ width: avgGrade + '%' }"></div></div>
              <span class="text-sm" style="color:rgba(255,255,255,.7)">Overall progress</span>
            </div>
          </div>

          <div v-if="assignLoading" class="spinner"></div>
          <div v-else-if="!assignments.length" class="empty-tab">
            <div class="empty-icon">📝</div>
            <p>No assignments yet{{ canManageCourse ? ' — create one above.' : '.' }}</p>
          </div>
          <div v-else class="assign-list">
            <div v-for="a in assignments" :key="a.id" class="assign-card card card-body">
              <div class="assign-top">
                <div>
                  <h3 class="assign-title">{{ a.title }}</h3>
                  <p class="text-muted text-sm mt-1">{{ a.description }}</p>
                </div>
                <span :class="['badge', statusBadge(a).cls]">{{ statusBadge(a).label }}</span>
              </div>
              <div class="assign-meta">
                <span class="meta-chip">📅 Due: {{ formatDate(a.due_date || a.dueDate) }}</span>
                <span class="meta-chip">🏆 Weight: {{ a.weight || 100 }}%</span>
                <span v-if="a.my_grade !== undefined" class="meta-chip grade-chip">Grade: <strong>{{ a.my_grade }}%</strong></span>
              </div>
              <div class="assign-actions">
                <!-- Student actions -->
                <template v-if="isStudent">
                  <button class="btn btn-primary btn-sm" :disabled="!!a.my_submission" @click="openSubmit(a)">
                    {{ a.my_submission ? '✓ Submitted' : 'Submit Assignment' }}
                  </button>
                </template>
                <!-- Lecturer/Admin actions -->
                <template v-if="canManageCourse">
                  <button class="btn btn-outline btn-sm" @click="openGrade(a)">
                    📋 Grade Submissions ({{ a.submission_count || 0 }})
                  </button>
                </template>
              </div>
            </div>
          </div>
        </div>

        <!-- FORUMS TAB -->
        <div v-if="activeTab === 'forums'">
          <div class="section-header">
            <h2>Forums</h2>
            <button class="btn btn-primary btn-sm" @click="showAddForum = true">+ New Forum</button>
          </div>
          <div v-if="forumLoading" class="spinner"></div>
          <div v-else-if="!forums.length" class="empty-tab">
            <div class="empty-icon">💬</div>
            <p>No forums yet — start the first discussion!</p>
          </div>
          <div v-else class="forum-list">
            <div v-for="f in forums" :key="f.id || f.forumID" class="forum-item card"
              @click="$router.push(`/course/${courseCode}/forums/${f.id || f.forumID}`)">
              <div class="card-body flex items-center gap-3">
                <div class="forum-icon">💬</div>
                <div class="flex-1">
                  <div class="forum-name">{{ f.title || f.name || f.forumName }}</div>
                  <div class="text-sm text-muted">{{ f.thread_count || 0 }} threads</div>
                </div>
                <span class="row-arrow">›</span>
              </div>
            </div>
          </div>
        </div>

       <!-- MEMBERS TAB -->
<div v-if="activeTab === 'members'">
  <div class="section-header"><h2>Course Members</h2></div>

  <!-- Filter + Search -->
  <div class="members-filters">
    <div class="filter-tabs">
      <button :class="['filter-tab', memberFilter==='all'&&'active']"    @click="memberFilter='all'">All</button>
      <button :class="['filter-tab', memberFilter==='student'&&'active']" @click="memberFilter='student'">Students</button>
      <button :class="['filter-tab', memberFilter==='lecturer'&&'active']" @click="memberFilter='lecturer'">Lecturers</button>
    </div>
    <input v-model="memberSearch" class="form-control member-search" placeholder="🔍 Search members…" />
  </div>

  <div v-if="membersLoading" class="spinner"></div>
  <div v-else-if="!filteredMembers.length" class="empty-tab">No members found.</div>
  <div v-else class="members-grid">
    <div v-for="(m, i) in filteredMembers" :key="i" class="member-card card card-body">
      <div class="member-avatar" :style="{ background: avatarColor(m) }">{{ memberInitials(m) }}</div>
      <div class="member-name">{{ memberName(m) }}</div>
      <span :class="['badge', memberRole(m) === 'lecturer' ? 'badge-blue' : 'badge-green']">
        {{ memberRole(m) === 'lecturer' ? 'Lecturer' : 'Student' }}
      </span>
    </div>
  </div>
</div>

        <!-- CALENDAR TAB -->
        <div v-if="activeTab === 'calendar'">
          <div class="section-header">
            <h2>Calendar Events</h2>
            <button v-if="canManageCourse" class="btn btn-primary btn-sm" @click="showAddEvent = true">+ Add Event</button>
          </div>
          <div v-if="eventsLoading" class="spinner"></div>
          <div v-else-if="!events.length" class="empty-tab">
            <div class="empty-icon">📅</div>
            <p>No events scheduled{{ canManageCourse ? ' — add one above.' : '.' }}</p>
          </div>
          <div v-else class="events-list">
            <div v-for="e in events" :key="e.id || e.eventID" class="event-item card card-body flex gap-3 items-center">
              <div class="event-date-box">
                <div class="event-month">{{ eventMonth(e.date || e.eventDate) }}</div>
                <div class="event-day">{{ eventDay(e.date || e.eventDate) }}</div>
              </div>
              <div>
                <div class="font-medium">{{ e.title || e.eventName }}</div>
                <div class="text-sm text-muted">{{ e.description }}</div>
              </div>
            </div>
          </div>
        </div>

       <!-- ADMIN TAB -->
<div v-if="activeTab === 'admin'">
  <div class="section-header"><h2>Course Administration</h2></div>
  <div class="admin-grid">
    <div class="card card-body">
      <h3 class="admin-card-title">Assign Lecturer</h3>
      <p class="text-sm text-muted mt-1">Assign a lecturer to this course</p>
      <div class="form-group" style="margin-top:16px">
        <label class="form-label">Select Lecturer</label>
        <div v-if="lecturersLoading" class="spinner-sm"></div>
        <select v-else v-model="assignForm.lecturerId" class="form-control">
          <option value="" disabled>— choose a lecturer —</option>
          <option v-for="l in lecturers" :key="l.userID" :value="l.userID">
            {{ l.firstName }} {{ l.lastName }} ({{ l.userID }})
          </option>
        </select>
      </div>
      <button class="btn btn-primary" @click="doAssignLecturer" :disabled="!assignForm.lecturerId">
        Assign Lecturer
      </button>
    </div>
  </div>
</div>
      </div>
    </template>

    <!-- ── MODALS ── -->

    <!-- Add Content -->
<div v-if="showAddContent" class="modal-backdrop" @click.self="showAddContent = false">
  <div class="modal modal-lg">
    <div class="modal-header">
      <h3>Add Course Content</h3>
      <button class="close-btn" @click="showAddContent = false">✕</button>
    </div>
    <div class="modal-body">
      <div v-if="contentError" class="alert alert-error">{{ contentError }}</div>

      <div class="form-group">
        <label class="form-label">Section Name</label>
        <input v-model="newContent.section" class="form-control" placeholder="e.g. Week 1" />
      </div>

      <div class="form-group">
        <label class="form-label">Content Title</label>
        <input v-model="newContent.title" class="form-control" placeholder="e.g. Week 1 Slides" />
      </div>

      <div class="form-group">
        <label class="form-label">Type</label>
        <div class="type-selector">
          <button v-for="t in ['link','file','slide']" :key="t"
            :class="['type-btn', newContent.type === t && 'active']"
            @click="newContent.type = t; newContent.url = ''">
            {{ t === 'link' ? '🔗 Link' : t === 'file' ? '📄 File' : '📊 Slide' }}
          </button>
        </div>
      </div>

      <!-- Link input -->
      <div v-if="newContent.type === 'link'" class="form-group">
        <label class="form-label">URL</label>
        <input v-model="newContent.url" class="form-control" placeholder="https://…" />
      </div>

      <!-- File / Slide drag-and-drop -->
      <div v-else class="form-group">
        <label class="form-label">{{ newContent.type === 'slide' ? 'Slide File' : 'File' }}</label>
        <div
          class="drop-zone"
          :class="{ 'drag-over': dragging }"
          @dragover.prevent="dragging = true"
          @dragleave="dragging = false"
          @drop.prevent="handleFileDrop($event, 'content')"
          @click="$refs.contentFileInput.click()"
        >
          <input ref="contentFileInput" type="file"
            :accept="newContent.type === 'slide' ? '.pdf,.ppt,.pptx' : '*'"
            style="display:none" @change="handleFileSelect($event, 'content')" />
          <div v-if="!newContent.fileName" class="drop-zone-inner">
            <div class="drop-icon">📁</div>
            <div class="drop-text">Drag & drop or <span class="drop-link">browse</span></div>
            <div class="drop-hint">
              {{ newContent.type === 'slide' ? 'PDF, PPT, PPTX' : 'Any file type' }}
            </div>
          </div>
          <div v-else class="drop-zone-file">
            <span class="file-icon">{{ newContent.type === 'slide' ? '📊' : '📄' }}</span>
            <span class="file-name">{{ newContent.fileName }}</span>
            <button class="remove-file" @click.stop="newContent.fileName = ''; newContent.url = ''">✕</button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" @click="showAddContent = false">Cancel</button>
      <button class="btn btn-primary" @click="addContent" :disabled="addingContent">
        {{ addingContent ? 'Adding…' : 'Add Content' }}
      </button>
    </div>
  </div>
</div>

    <!-- New Assignment -->
    <div v-if="showAddAssignment" class="modal-backdrop" @click.self="showAddAssignment = false">
      <div class="modal">
        <div class="modal-header"><h3>New Assignment</h3><button class="close-btn" @click="showAddAssignment = false">✕</button></div>
        <div class="modal-body">
          <div v-if="assignError" class="alert alert-error">{{ assignError }}</div>
          <div class="form-group"><label class="form-label">Title</label><input v-model="newAssign.title" class="form-control" /></div>
          <div class="form-group"><label class="form-label">Description</label><textarea v-model="newAssign.description" class="form-control" rows="3"></textarea></div>
          <div class="form-group"><label class="form-label">Due Date</label><input v-model="newAssign.due_date" type="datetime-local" class="form-control" /></div>
          <div class="form-group"><label class="form-label">Weight (%)</label><input v-model="newAssign.weight" type="number" class="form-control" placeholder="100" /></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showAddAssignment = false">Cancel</button>
          <button class="btn btn-primary" @click="createAssignment" :disabled="creatingAssign">{{ creatingAssign ? 'Creating…' : 'Create' }}</button>
        </div>
      </div>
    </div>

    <!-- Submit Assignment -->
    <!-- Submit Assignment -->
<div v-if="showSubmit" class="modal-backdrop" @click.self="showSubmit = false">
  <div class="modal">
    <div class="modal-header">
      <h3>Submit: {{ selectedAssignment?.title || selectedAssignment?.assignmentName }}</h3>
      <button class="close-btn" @click="showSubmit = false">✕</button>
    </div>
    <div class="modal-body">
      <div v-if="submitError" class="alert alert-error">{{ submitError }}</div>

      <!-- Submission type toggle -->
      <div class="form-group">
        <label class="form-label">Submission Type</label>
        <div class="type-selector">
          <button :class="['type-btn', submitType==='link'&&'active']" @click="submitType='link'">🔗 Link</button>
          <button :class="['type-btn', submitType==='file'&&'active']" @click="submitType='file'">📄 File Upload</button>
        </div>
      </div>

      <!-- Link submission -->
      <div v-if="submitType === 'link'" class="form-group">
        <label class="form-label">Link (GitHub, Drive, etc.)</label>
        <input v-model="submission.content" class="form-control" placeholder="https://github.com/…" />
      </div>

      <!-- File submission drag-and-drop -->
      <div v-else class="form-group">
        <label class="form-label">Upload File</label>
        <div
          class="drop-zone"
          :class="{ 'drag-over': draggingSubmit }"
          @dragover.prevent="draggingSubmit = true"
          @dragleave="draggingSubmit = false"
          @drop.prevent="handleFileDrop($event, 'submit')"
          @click="$refs.submitFileInput.click()"
        >
          <input ref="submitFileInput" type="file" style="display:none"
            @change="handleFileSelect($event, 'submit')" />
          <div v-if="!submission.fileName" class="drop-zone-inner">
            <div class="drop-icon">📤</div>
            <div class="drop-text">Drag & drop or <span class="drop-link">browse</span></div>
            <div class="drop-hint">Any file type accepted</div>
          </div>
          <div v-else class="drop-zone-file">
            <span class="file-icon">📄</span>
            <span class="file-name">{{ submission.fileName }}</span>
            <button class="remove-file" @click.stop="submission.fileName = ''; submission.content = ''">✕</button>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Notes (optional)</label>
        <textarea v-model="submission.notes" class="form-control" rows="2"
          placeholder="Any notes for your lecturer…"></textarea>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" @click="showSubmit = false">Cancel</button>
      <button class="btn btn-primary" @click="submitAssignment" :disabled="submitting">
        {{ submitting ? 'Submitting…' : 'Submit' }}
      </button>
    </div>
  </div>
</div>

    <!-- Grade Submissions -->
    <div v-if="showGrade" class="modal-backdrop" @click.self="showGrade = false">
  <div class="modal modal-lg">
    <div class="modal-header">
      <h3>Grade: {{ selectedAssignment?.title || selectedAssignment?.assignmentName }}</h3>
      <button class="close-btn" @click="showGrade = false">✕</button>
    </div>
    <div class="modal-body">
      <div v-if="!gradeSubmissions.length" class="empty-tab">No submissions yet.</div>
      <div v-else>
        <div v-for="s in gradeSubmissions" :key="s.student_id" class="grade-row">
          <div class="student-info">
            <div class="student-avatar">{{ String(s.username || s.student_id || '?').slice(0,2).toUpperCase() }}</div>
            <span class="font-medium">{{ s.username || s.student_id }}</span>
          </div>
          <div class="sub-content text-sm">
            <a v-if="s.content && s.content.startsWith('http')"
               :href="s.content" target="_blank" class="btn btn-outline btn-sm">
              🔗 View Submission
            </a>
            <span v-else class="text-muted">📎 {{ s.content || 'No submission' }}</span>
          </div>
          <span v-if="s.grade !== null && s.grade !== undefined"
                class="badge badge-green" style="margin-right:8px">
            Graded: {{ s.grade }}%
          </span>
          <div class="grade-input-wrap">
            <input v-model="s.inputGrade" type="number" min="0" max="100"
              class="form-control grade-input" placeholder="0–100" />
            <button class="btn btn-primary btn-sm" @click="submitGrade(s)">Save</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

    <!-- New Forum -->
    <div v-if="showAddForum" class="modal-backdrop" @click.self="showAddForum = false">
      <div class="modal">
        <div class="modal-header"><h3>Create Forum</h3><button class="close-btn" @click="showAddForum = false">✕</button></div>
        <div class="modal-body">
          <div class="form-group"><label class="form-label">Title</label><input v-model="newForum.title" class="form-control" placeholder="e.g. Week 1 Discussion" /></div>
          <div class="form-group"><label class="form-label">Description</label><textarea v-model="newForum.description" class="form-control" rows="2"></textarea></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showAddForum = false">Cancel</button>
          <button class="btn btn-primary" @click="createForum">Create</button>
        </div>
      </div>
    </div>

    <!-- Add Event -->
    <div v-if="showAddEvent" class="modal-backdrop" @click.self="showAddEvent = false">
      <div class="modal">
        <div class="modal-header"><h3>Add Calendar Event</h3><button class="close-btn" @click="showAddEvent = false">✕</button></div>
        <div class="modal-body">
          <div class="form-group"><label class="form-label">Title</label><input v-model="newEvent.title" class="form-control" placeholder="e.g. Midterm Exam" /></div>
          <div class="form-group"><label class="form-label">Description</label><input v-model="newEvent.description" class="form-control" /></div>
          <div class="form-group"><label class="form-label">Date & Time</label><input v-model="newEvent.date" type="datetime-local" class="form-control" /></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showAddEvent = false">Cancel</button>
          <button class="btn btn-primary" @click="createEvent">Add Event</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useRole } from '../composables/useRole.js'
import { courseService, assignmentService, contentService, forumService, eventService } from '../services/api.js'

const route = useRoute()
const courseCode = computed(() => route.params.id)
const { isStudent, isLecturer, isAdmin, canManageCourse } = useRole()

const loading  = ref(true)
const course   = ref({})
const enrolled = ref(true)
const enrolling= ref(false)
const activeTab= ref('content')

const allTabs = [
  { key: 'content',     label: 'Content',     icon: '📖' },
  { key: 'assignments', label: 'Assignments',  icon: '📝' },
  { key: 'forums',      label: 'Forums',       icon: '💬' },
  { key: 'members',     label: 'Members',      icon: '👥' },
  { key: 'calendar',    label: 'Calendar',     icon: '📅' },
  { key: 'admin',       label: 'Admin',        icon: '⚙️', adminOnly: true },
]
const visibleTabs = computed(() => allTabs.filter(t => !t.adminOnly || isAdmin.value))

const COLORS = ['#3a6186','#89216b','#1c6c3a','#7b4397','#c0392b','#16a085','#2c3e50']
const heroColor = computed(() => COLORS[String(courseCode.value).charCodeAt(0) % COLORS.length])

// Content
// Content
const contentItems   = ref([])
const contentLoading = ref(false)
const showAddContent = ref(false)
const contentError   = ref('')
const addingContent  = ref(false)
const dragging       = ref(false)
const draggingSubmit = ref(false)
const newContent     = ref({ title: '', type: 'link', url: '', section: '', fileName: '' })

const groupedContent = computed(() => {
  // backend returns sections array with contentItems
  if (contentItems.value.length && contentItems.value[0]?.secName) {
    return contentItems.value.map(s => ({
      name: s.secName,
      items: (s.contentItems || []).map(i => ({
        id:    i.contentID,
        title: i.contentName,
        type:  i.type,
        url:   i.content,
      }))
    }))
  }
  // fallback flat list
  const map = {}
  contentItems.value.forEach(item => {
    const s = item.section || item.secName || 'General'
    if (!map[s]) map[s] = { name: s, items: [] }
    map[s].items.push(item)
  })
  return Object.values(map)
})

const contentIcon = t => ({ link: '🔗', file: '📄', slide: '📊', video: '🎥' }[t] || '📄')

const handleFileDrop = (e, target) => {
  const file = e.dataTransfer.files[0]
  if (!file) return
  if (target === 'content') {
    dragging.value = false
    newContent.value.fileName = file.name
    newContent.value.url = file.name // store filename as content since no file server
  } else {
    draggingSubmit.value = false
    submission.value.fileName = file.name
    submission.value.content = file.name
  }
}

const handleFileSelect = (e, target) => {
  const file = e.target.files[0]
  if (!file) return
  if (target === 'content') {
    newContent.value.fileName = file.name
    newContent.value.url = file.name
  } else {
    submission.value.fileName = file.name
    submission.value.content = file.name
  }
}

const addContent = async () => {
  contentError.value = ''
  if (!newContent.value.section || !newContent.value.title) {
    contentError.value = 'Section name and title are required.'
    return
  }
  addingContent.value = true
  try {
    const secRes = await contentService.createSection({
      courseCode: courseCode.value,
      secName: newContent.value.section,
    })
    await contentService.createItem({
      secID:       secRes.data.secID,
      contentName: newContent.value.title,
      type:        newContent.value.type,
      content:     newContent.value.url,
    })
    // reload
    const r = await contentService.getByCourse(courseCode.value)
    contentItems.value = r.data.sections || r.data.content || r.data
    showAddContent.value = false
    newContent.value = { title: '', type: 'link', url: '', section: '', fileName: '' }
  } catch (e) {
    contentError.value = e.response?.data?.error || 'Failed to add content.'
  } finally { addingContent.value = false }
}

// Submission type
const submitType = ref('link')

// Assignments
const assignments    = ref([])
const assignLoading  = ref(false)
const showAddAssignment = ref(false)
const newAssign      = ref({ title: '', description: '', due_date: '', weight: 100 })
const assignError    = ref('')
const creatingAssign = ref(false)
const showSubmit     = ref(false)
const showGrade      = ref(false)
const selectedAssignment = ref(null)
const submission     = ref({ content: '' })
const submitting     = ref(false)
const submitError    = ref('')
const gradeSubmissions = ref([])

const submittedCount = computed(() => assignments.value.filter(a => a.my_submission).length)
const avgGrade = computed(() => {
  const g = assignments.value.filter(a => a.my_grade !== undefined)
  return g.length ? Math.round(g.reduce((s, a) => s + a.my_grade, 0) / g.length) : 0
})
const statusBadge = a => {
  if (a.my_grade !== undefined) return { cls: 'badge-green', label: `Graded: ${a.my_grade}%` }
  if (a.my_submission)          return { cls: 'badge-blue',  label: 'Submitted' }
  if ((a.due_date||a.dueDate) && new Date(a.due_date||a.dueDate) < new Date()) return { cls: 'badge-red', label: 'Overdue' }
  return { cls: 'badge-grey', label: 'Open' }
}
const openSubmit = a => {
  selectedAssignment.value = a
  submission.value = { content: '', fileName: '', notes: '' }
  submitType.value = 'link'
  submitError.value = ''
  showSubmit.value = true
}
const openGrade  = async a => {
  selectedAssignment.value = a; gradeSubmissions.value = []; showGrade.value = true
  try { const r = await assignmentService.getSubmissions(a.id || a.assignmentID); gradeSubmissions.value = (r.data.submissions||r.data).map(s=>({...s,inputGrade:s.grade||''})) } catch {}
}
const submitAssignment = async () => {
  submitError.value = ''; submitting.value = true
  try {
    await assignmentService.submit(selectedAssignment.value.id || selectedAssignment.value.assignmentID, submission.value)
    const idx = assignments.value.findIndex(a => (a.id||a.assignmentID) === (selectedAssignment.value.id||selectedAssignment.value.assignmentID))
    if (idx !== -1) assignments.value[idx].my_submission = { submitted_at: new Date().toISOString() }
    showSubmit.value = false
  } catch (e) { submitError.value = e.response?.data?.error || 'Submission failed.' }
  finally { submitting.value = false }
}
const createAssignment = async () => {
  assignError.value = ''; creatingAssign.value = true
  try {
    const res = await assignmentService.create({ ...newAssign.value, courseCode: courseCode.value })
    assignments.value.unshift(res.data); showAddAssignment.value = false
    newAssign.value = { title: '', description: '', due_date: '', weight: 100 }
  } catch (e) { assignError.value = e.response?.data?.error || 'Failed to create.' }
  finally { creatingAssign.value = false }
}
const submitGrade = async s => {
  try {
    await assignmentService.grade(selectedAssignment.value.id||selectedAssignment.value.assignmentID, s.student_id, { grade: Number(s.inputGrade) })
    s.grade = s.inputGrade; alert(`Grade saved for ${s.username||s.student_id}`)
  } catch { alert('Failed to save grade.') }
}

// Forums
const forums      = ref([])
const forumLoading= ref(false)
const showAddForum= ref(false)
const newForum    = ref({ title: '', description: '' })
const createForum = async () => {
  try {
    const res = await forumService.create({ ...newForum.value, courseCode: courseCode.value })
    forums.value.push(res.data); showAddForum.value = false; newForum.value = { title: '', description: '' }
  } catch { alert('Failed to create forum.') }
}

// Members
const members       = ref([])
const membersLoading= ref(false)
const memberFilter = ref('all')
const memberSearch = ref('')
const AVATAR_COLORS = ['#3a6186','#89216b','#1c6c3a','#7b4397','#c0392b','#16a085']
const memberName    = m => Array.isArray(m) ? `${m[0]||''} ${m[1]||''}`.trim() : `${m.firstName||''} ${m.lastName||''}`.trim() || m.username || String(m.userID||'')
const memberInitials= m => { const n = memberName(m); const p = n.split(' '); return ((p[0]||'')[0]||(p[1]||'')[0]||'?').toUpperCase() + ((p[1]||'')[0]||'').toUpperCase() }
const avatarColor   = m => AVATAR_COLORS[(memberName(m).charCodeAt(0)||0) % AVATAR_COLORS.length]
const filteredMembers = computed(() => {
  let list = members.value
  if (memberFilter.value !== 'all')
    list = list.filter(m => memberRole(m) === memberFilter.value)
  if (memberSearch.value) {
    const q = memberSearch.value.toLowerCase()
    list = list.filter(m => memberName(m).toLowerCase().includes(q))
  }
  return list
})

const memberRole = m => {
  if (Array.isArray(m)) return (m[2] || '').toLowerCase()
  return (m.role || '').toLowerCase()
}
// Calendar
const events       = ref([])
const eventsLoading= ref(false)
const showAddEvent = ref(false)
const newEvent     = ref({ title: '', description: '', date: '' })
const eventMonth   = d => d ? new Date(d).toLocaleString('default',{month:'short'}).toUpperCase() : ''
const eventDay     = d => d ? new Date(d).getDate() : ''
const createEvent = async () => {
  try {
    await eventService.create({
      courseCode:  courseCode.value,
      eventName:   newEvent.value.title,
      createdDate: new Date().toISOString().split('T')[0],
      dueDate:     newEvent.value.date,
    })
    await loadTab('calendar')  // refresh the list
    showAddEvent.value = false
    newEvent.value = { title: '', description: '', date: '' }
  } catch (e) {
    alert(e.response?.data?.error || 'Failed to create event.')
  }
}


// Admin
const lecturers       = ref([])
const lecturersLoading= ref(false)
const assignForm = ref({ lecturerId: '' })
const doAssignLecturer = async () => {
  try {
    await courseService.assignLecturer(Number(assignForm.value.lecturerId), courseCode.value)
    alert('Lecturer assigned!'); assignForm.value.lecturerId = ''
  } catch (e) { alert(e.response?.data?.error || 'Failed.') }
}

// Enrol (students)
const enrollCourse = async () => {
  enrolling.value = true
  try { await courseService.enroll(courseCode.value); enrolled.value = true }
  catch (e) { alert(e.response?.data?.error || 'Enrollment failed.') }
  finally { enrolling.value = false }
}

const formatDate = d => d ? new Date(d).toLocaleDateString('en-JM',{year:'numeric',month:'short',day:'numeric'}) : '—'

// Lazy load tab data
const loadTab = async tab => {
  const code = courseCode.value

  if (tab === 'content' && !contentItems.value.length) {
    contentLoading.value = true
    try {
      const r = await contentService.getByCourse(code)
      contentItems.value = r.data.sections || r.data.content || r.data
    } catch {}
    contentLoading.value = false
  }

  if (tab === 'assignments') {
  assignLoading.value = true
  try {
    const r = await assignmentService.getByCourse(code)
   assignments.value = (r.data.assignments || r.data).map(a => ({
  ...a,
  title:            a.assignmentName  || a.title,
  id:               a.assignmentID    || a.id,
  my_submission:    a.my_submission   || null,
  submission_count: a.submission_count || 0,
}))
  } catch {}
  assignLoading.value = false
}
  if (tab === 'forums' && !forums.value.length) {
    forumLoading.value = true
    try { const r = await forumService.getByCourse(code); forums.value = r.data.forums || r.data } catch {}
    forumLoading.value = false
  }

  if (tab === 'members' && !members.value.length) {
    membersLoading.value = true
    try { const r = await courseService.getMembers(code); members.value = r.data.members || r.data } catch {}
    membersLoading.value = false
  }

  if (tab === 'calendar' && !events.value.length) {
    eventsLoading.value = true
    try { const r = await eventService.getByCourse(code); events.value = r.data.events || r.data } catch {}
    eventsLoading.value = false
  }

  if (tab === 'admin' && !lecturers.value.length) {
    lecturersLoading.value = true
    try {
      const r = await courseService.getLecturers()
      lecturers.value = r.data.lecturers || r.data
    } catch {}
    lecturersLoading.value = false
  }
}

watch(activeTab, loadTab)

onMounted(async () => {
  try {
    const r = await courseService.getMyCourses()
    const list = r.data.courses || r.data
    course.value = list.find(c => (c.courseCode||c.code) === courseCode.value) || { courseCode: courseCode.value }
  } catch {
    course.value = { courseCode: courseCode.value, courseName: courseCode.value }
  } finally { loading.value = false }
  loadTab('content')
})


</script>

<style scoped>
.course-hero { position: relative; padding: calc(var(--nav-height) + 24px) 0 32px; overflow: hidden; }
.hex-overlay { position: absolute; inset: 0; opacity: .12; background-image: url("data:image/svg+xml,%3Csvg width='56' height='100' viewBox='0 0 56 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M28 66L0 50V16L28 0l28 16v34z' fill='none' stroke='%23fff' stroke-width='1.5'/%3E%3C/svg%3E"); background-size: 56px 100px; }
.hero-inner { position: relative; }
.back-btn { background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.3); color: white; border-radius: 8px; padding: 6px 14px; font-size: 13px; cursor: pointer; margin-bottom: 16px; font-family: 'DM Sans', sans-serif; transition: background .15s; }
.back-btn:hover { background: rgba(255,255,255,.25); }
.course-code-badge { display: inline-block; background: rgba(255,255,255,.2); color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-bottom: 10px; }
.hero-content h1 { font-size: 26px; color: white; margin-bottom: 8px; text-shadow: 0 2px 8px rgba(0,0,0,.2); }
.hero-meta-row { margin-bottom: 14px; }
.role-chip { font-size: 12px; font-weight: 600; padding: 4px 14px; border-radius: 20px; }
.role-chip.admin    { background: var(--uwi-gold); color: #1a1a1a; }
.role-chip.lecturer { background: rgba(255,255,255,.2); color: white; border: 1px solid rgba(255,255,255,.4); }
.role-chip.student  { background: rgba(255,255,255,.12); color: rgba(255,255,255,.9); border: 1px solid rgba(255,255,255,.3); }
.hero-actions { margin-top: 4px; }

.tab-bar { background: white; border-bottom: 1px solid var(--border); position: sticky; top: var(--nav-height); z-index: 40; }
.tabs { display: flex; overflow-x: auto; }
.tab { padding: 14px 16px; background: none; border: none; cursor: pointer; font-family: 'DM Sans', sans-serif; font-size: 14px; font-weight: 500; color: var(--text-muted); border-bottom: 3px solid transparent; transition: all .15s; white-space: nowrap; gap: 6px; }
.tab:hover { color: var(--text); background: var(--surface-2); }
.tab.active { color: var(--primary); border-bottom-color: var(--primary); }

.tab-body { padding: 28px 0 60px; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.section-header h2 { font-size: 20px; }

.empty-tab { text-align: center; padding: 48px 20px; color: var(--text-muted); }
.empty-icon { font-size: 40px; margin-bottom: 12px; }

/* Content */
.content-section { margin-bottom: 24px; }
.section-label { font-size: 12px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 8px; }
.content-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: white; border-radius: var(--radius); border: 1px solid var(--border); margin-bottom: 8px; }
.content-icon { font-size: 20px; flex-shrink: 0; }
.content-info { flex: 1; }
.content-name { font-weight: 500; font-size: 14px; }

/* Assignments */
.grade-bar { display: flex; align-items: center; gap: 28px; padding: 20px 24px; background: linear-gradient(135deg, var(--uwi-green), #004d2e); border-radius: var(--radius-lg); margin-bottom: 20px; color: white; flex-wrap: wrap; }
.grade-stat { text-align: center; }
.grade-val { font-family: 'Fraunces', serif; font-size: 28px; font-weight: 700; line-height: 1; }
.grade-label { font-size: 11px; opacity: .75; text-transform: uppercase; letter-spacing: .5px; margin-top: 3px; }
.grade-progress-wrap { flex: 1; min-width: 200px; }
.progress-bar { height: 8px; background: rgba(255,255,255,.2); border-radius: 4px; overflow: hidden; margin-bottom: 4px; }
.progress-fill { height: 100%; background: var(--uwi-gold); border-radius: 4px; transition: width .5s; }
.assign-list { display: flex; flex-direction: column; gap: 14px; }
.assign-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 10px; }
.assign-title { font-size: 16px; }
.assign-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
.meta-chip { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; background: var(--surface-2); border-radius: 20px; font-size: 12px; color: var(--text-muted); }
.grade-chip { background: #d4edda; color: #155724; }
.assign-actions { display: flex; align-items: center; gap: 10px; padding-top: 12px; border-top: 1px solid var(--border); }

/* Grade modal */
.grade-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); flex-wrap: wrap; }
.grade-row:last-child { border-bottom: none; }
.student-info { display: flex; align-items: center; gap: 8px; min-width: 140px; }
.student-avatar { width: 30px; height: 30px; border-radius: 50%; background: var(--uwi-green); color: white; font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.sub-content { flex: 1; }
.grade-input-wrap { display: flex; gap: 8px; align-items: center; }
.grade-input { width: 80px; }

/* Forums */
.forum-list { display: flex; flex-direction: column; gap: 10px; }
.forum-item { cursor: pointer; transition: box-shadow .15s; }
.forum-item:hover { box-shadow: var(--shadow); }
.forum-icon { font-size: 22px; }
.forum-name { font-weight: 500; font-size: 14px; }
.row-arrow { color: var(--text-muted); font-size: 22px; }

/* Members */
.members-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
.member-card { display: flex; flex-direction: column; align-items: center; gap: 6px; text-align: center; }
.member-avatar { width: 44px; height: 44px; border-radius: 50%; color: white; font-weight: 700; font-size: 14px; display: flex; align-items: center; justify-content: center; }
.member-name { font-size: 13px; font-weight: 500; }
.members-filters {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 20px; flex-wrap: wrap;
}
.filter-tabs { display: flex; gap: 6px; }
.filter-tab {
  padding: 6px 16px; border-radius: 20px; border: 1.5px solid var(--border);
  background: white; cursor: pointer; font-size: 13px; font-weight: 500;
  color: var(--text-muted); transition: all .15s; font-family: 'DM Sans', sans-serif;
}
.filter-tab:hover { border-color: var(--primary); color: var(--primary); }
.filter-tab.active { background: var(--primary); border-color: var(--primary); color: white; }
.member-search { max-width: 260px; }

/* Events */
.events-list { display: flex; flex-direction: column; gap: 10px; }
.event-date-box { min-width: 48px; text-align: center; background: var(--primary-light); border-radius: 8px; padding: 6px; flex-shrink: 0; }
.event-month { font-size: 10px; font-weight: 700; color: var(--primary); text-transform: uppercase; }
.event-day { font-size: 20px; font-weight: 700; color: var(--primary); line-height: 1; }

/* Admin */
.admin-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.admin-card-title { font-size: 16px; }

/* Modals */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 300; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal { background: white; border-radius: var(--radius-lg); width: 100%; max-width: 480px; box-shadow: var(--shadow-lg); max-height: 90vh; overflow-y: auto; }
.modal-lg { max-width: 640px; }
.modal-header { padding: 18px 24px 14px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }
.modal-header h3 { font-size: 17px; }
.close-btn { background: none; border: none; font-size: 18px; cursor: pointer; color: var(--text-muted); }
.modal-body { padding: 20px 24px; }
.modal-footer { padding: 14px 24px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 10px; }
.mt-1 { margin-top: 4px; }

/* Type selector */
.type-selector { display: flex; gap: 8px; }
.type-btn {
  flex: 1; padding: 8px 12px; border: 1.5px solid var(--border);
  border-radius: 8px; background: white; cursor: pointer;
  font-size: 13px; font-weight: 500; color: var(--text-muted);
  transition: all .15s; font-family: 'DM Sans', sans-serif;
}
.type-btn:hover { border-color: var(--primary); color: var(--primary); }
.type-btn.active { background: var(--primary-light); border-color: var(--primary); color: var(--primary); }

/* Drop zone */
.drop-zone {
  border: 2px dashed var(--border); border-radius: var(--radius);
  padding: 32px 20px; text-align: center; cursor: pointer;
  transition: all .2s; background: var(--surface);
}
.drop-zone:hover, .drop-zone.drag-over {
  border-color: var(--primary); background: var(--primary-light);
}
.drop-zone-inner { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.drop-icon { font-size: 32px; }
.drop-text { font-size: 14px; font-weight: 500; color: var(--text); }
.drop-link { color: var(--primary); text-decoration: underline; }
.drop-hint { font-size: 12px; color: var(--text-muted); }
.drop-zone-file { display: flex; align-items: center; gap: 10px; justify-content: center; }
.file-icon { font-size: 24px; }
.file-name { font-size: 14px; font-weight: 500; color: var(--text); }
.remove-file {
  background: none; border: none; cursor: pointer;
  color: var(--text-muted); font-size: 16px; padding: 2px 6px;
  border-radius: 4px; transition: background .12s;
}
.remove-file:hover { background: var(--surface-2); color: var(--danger); }
.spinner-sm { width: 20px; height: 20px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; margin: 8px 0; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>

