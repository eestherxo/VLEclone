<template>
  <div class="assignments-page">
    <div class="container py-6">
      <div class="page-header">
        <div>
          <button class="back-btn" @click="$router.back()">← Back to Course</button>
          <h1>Assignments</h1>
          <p class="text-muted">{{ course.code }} – {{ course.name }}</p>
        </div>
        <button v-if="isLecturer" class="btn btn-primary" @click="showCreate = true">+ New Assignment</button>
      </div>

      <div v-if="loading" class="spinner"></div>
      <div v-else-if="error" class="alert alert-error">{{ error }}</div>
      <div v-else>
        <!-- Student Grade Summary -->
        <div v-if="isStudent && assignments.length" class="grade-summary card card-body">
          <div class="grade-stat">
            <div class="grade-val">{{ avgGrade }}%</div>
            <div class="grade-label">Current Average</div>
          </div>
          <div class="grade-stat">
            <div class="grade-val">{{ submitted }}/{{ assignments.length }}</div>
            <div class="grade-label">Submitted</div>
          </div>
          <div class="grade-stat">
            <div class="grade-val">{{ graded }}</div>
            <div class="grade-label">Graded</div>
          </div>
          <div class="grade-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: avgGrade + '%' }"></div>
            </div>
            <span class="text-sm text-muted">Overall progress</span>
          </div>
        </div>

        <!-- Empty -->
        <div v-if="assignments.length === 0" class="empty-state">
          <div class="empty-icon">📝</div>
          <h3>No assignments yet</h3>
          <p>Check back later or ask your lecturer.</p>
        </div>

        <!-- Assignment Cards -->
        <div v-else class="assignments-list">
          <div v-for="a in assignments" :key="a.id" class="assignment-card card">
            <div class="card-body">
              <div class="assign-top">
                <div>
                  <h3 class="assign-title">{{ a.title }}</h3>
                  <p class="text-muted text-sm mt-1">{{ a.description }}</p>
                </div>
                <span :class="['badge', statusBadge(a).class]">{{ statusBadge(a).label }}</span>
              </div>

              <div class="assign-meta">
                <span class="meta-chip">📅 Due: {{ formatDate(a.due_date) }}</span>
                <span class="meta-chip">🏆 Weight: {{ a.weight || 100 }}%</span>
                <span v-if="a.my_grade !== undefined" class="meta-chip grade-chip">
                  Grade: <strong>{{ a.my_grade }}%</strong>
                </span>
              </div>

              <div class="assign-actions">
                <template v-if="isStudent">
                  <button
                    class="btn btn-primary btn-sm"
                    @click="openSubmit(a)"
                    :disabled="a.my_submission"
                  >
                    {{ a.my_submission ? '✓ Submitted' : 'Submit' }}
                  </button>
                  <span v-if="a.my_submission" class="text-sm text-muted">
                    Submitted {{ formatDate(a.my_submission.submitted_at) }}
                  </span>
                </template>

                <template v-if="isLecturer">
                  <button class="btn btn-outline btn-sm" @click="viewSubmissions(a)">
                    View Submissions ({{ a.submission_count || 0 }})
                  </button>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Submit Modal -->
    <div v-if="showSubmit" class="modal-backdrop" @click.self="showSubmit = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Submit Assignment</h3>
          <button class="close-btn" @click="showSubmit = false">✕</button>
        </div>
        <div class="modal-body">
          <p class="text-muted mb-3">{{ selectedAssignment?.title }}</p>
          <div class="form-group">
            <label class="form-label">Submission URL or Notes</label>
            <textarea v-model="submission.content" class="form-control" rows="4"
              placeholder="Paste your GitHub link, Google Drive link, or submission notes…"></textarea>
          </div>
          <div v-if="submitError" class="alert alert-error">{{ submitError }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showSubmit = false">Cancel</button>
          <button class="btn btn-primary" @click="submitAssignment" :disabled="submitting">
            {{ submitting ? 'Submitting…' : 'Submit' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Create Assignment Modal (Lecturer) -->
    <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate = false">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h3>New Assignment</h3>
          <button class="close-btn" @click="showCreate = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="createError" class="alert alert-error">{{ createError }}</div>
          <div class="form-row">
            <div class="form-group flex-1">
              <label class="form-label">Title</label>
              <input v-model="newAssign.title" class="form-control" placeholder="Assignment title" />
            </div>
            <div class="form-group" style="width:120px">
              <label class="form-label">Weight (%)</label>
              <input v-model="newAssign.weight" type="number" class="form-control" placeholder="100" min="0" max="100" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Description</label>
            <textarea v-model="newAssign.description" class="form-control" rows="4"
              placeholder="Describe the assignment requirements…"></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Due Date</label>
            <input v-model="newAssign.due_date" type="datetime-local" class="form-control" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showCreate = false">Cancel</button>
          <button class="btn btn-primary" @click="createAssignment" :disabled="creating">
            {{ creating ? 'Creating…' : 'Create Assignment' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Grade Submissions Modal (Lecturer) -->
    <div v-if="showGrade" class="modal-backdrop" @click.self="showGrade = false">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h3>Grade: {{ selectedAssignment?.title }}</h3>
          <button class="close-btn" @click="showGrade = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="gradeSubmissions.length === 0" class="empty-tab">No submissions yet.</div>
          <div v-else>
            <div v-for="s in gradeSubmissions" :key="s.student_id" class="grade-row">
              <div class="student-info">
                <div class="student-avatar">{{ s.username?.slice(0,2).toUpperCase() }}</div>
                <span class="font-medium">{{ s.username }}</span>
              </div>
              <div class="sub-content text-sm text-muted">{{ s.content?.slice(0,60) }}…</div>
              <div class="grade-input-wrap">
                <input
                  v-model="s.inputGrade"
                  type="number" min="0" max="100"
                  class="form-control grade-input"
                  placeholder="0–100"
                />
                <button class="btn btn-primary btn-sm" @click="submitGrade(s)">Save</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { assignmentService, courseService } from '../services/api.js'

const route = useRoute()
const courseId = computed(() => route.params.id)

const loading = ref(true)
const error = ref('')
const course = ref({})
const assignments = ref([])

const user = computed(() => JSON.parse(localStorage.getItem('user') || 'null'))
const isStudent = computed(() => user.value?.role === 'student')
const isLecturer = computed(() => user.value?.role === 'lecturer')

// Stats
const submitted = computed(() => assignments.value.filter(a => a.my_submission).length)
const graded = computed(() => assignments.value.filter(a => a.my_grade !== undefined).length)
const avgGrade = computed(() => {
  const graded = assignments.value.filter(a => a.my_grade !== undefined)
  if (!graded.length) return 0
  return Math.round(graded.reduce((s, a) => s + a.my_grade, 0) / graded.length)
})

// Submit
const showSubmit = ref(false)
const selectedAssignment = ref(null)
const submission = ref({ content: '' })
const submitting = ref(false)
const submitError = ref('')

// Create
const showCreate = ref(false)
const newAssign = ref({ title: '', description: '', due_date: '', weight: 100 })
const creating = ref(false)
const createError = ref('')

// Grade
const showGrade = ref(false)
const gradeSubmissions = ref([])

const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-JM', { year:'numeric', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' }) : '—'

const statusBadge = (a) => {
  if (a.my_grade !== undefined) return { class: 'badge-green', label: `Graded: ${a.my_grade}%` }
  if (a.my_submission) return { class: 'badge-blue', label: 'Submitted' }
  if (a.due_date && new Date(a.due_date) < new Date()) return { class: 'badge-red', label: 'Overdue' }
  if (a.due_date && new Date(a.due_date) - new Date() < 86400000*3) return { class: 'badge-gold', label: 'Due Soon' }
  return { class: 'badge-grey', label: 'Open' }
}

const openSubmit = (a) => { selectedAssignment.value = a; submission.value = { content: '' }; submitError.value = ''; showSubmit.value = true }

const submitAssignment = async () => {
  submitError.value = ''
  submitting.value = true
  try {
    await assignmentService.submit(selectedAssignment.value.id, submission.value)
    const idx = assignments.value.findIndex(a => a.id === selectedAssignment.value.id)
    if (idx !== -1) assignments.value[idx].my_submission = { submitted_at: new Date().toISOString(), ...submission.value }
    showSubmit.value = false
  } catch (e) { submitError.value = e.response?.data?.message || 'Submission failed.' }
  finally { submitting.value = false }
}

const createAssignment = async () => {
  createError.value = ''
  creating.value = true
  try {
    const res = await assignmentService.create({ ...newAssign.value, course_id: courseId.value })
    assignments.value.unshift(res.data)
    showCreate.value = false
    newAssign.value = { title: '', description: '', due_date: '', weight: 100 }
  } catch (e) { createError.value = e.response?.data?.message || 'Failed to create.' }
  finally { creating.value = false }
}

const viewSubmissions = async (a) => {
  selectedAssignment.value = a
  gradeSubmissions.value = []
  showGrade.value = true
  // TODO: call submissions endpoint when available
}

const submitGrade = async (s) => {
  try {
    await assignmentService.grade(selectedAssignment.value.id, s.student_id, { grade: s.inputGrade })
    s.grade = s.inputGrade
    alert(`Grade saved for ${s.username}`)
  } catch { alert('Failed to save grade.') }
}

onMounted(async () => {
  try {
    const [cRes, aRes] = await Promise.all([
      courseService.getById(courseId.value),
      assignmentService.getByCourse(courseId.value)
    ])
    course.value = cRes.data
    assignments.value = aRes.data
  } catch (e) {
    course.value = { code: 'COMP3161', name: 'Intro to Database Management' }
    assignments.value = [
      { id: 1, title: 'ER Diagram Submission', description: 'Submit your ERD for the VLE project.', due_date: '2025-04-10T23:59', weight: 30 },
      { id: 2, title: 'SQL Queries Assignment', description: 'Write and test all SQL queries as described.', due_date: '2025-05-01T23:59', weight: 40 },
    ]
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.py-6 { padding: 32px 0 60px; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 28px; }
.page-header h1 { font-size: 26px; margin: 8px 0 4px; }
.back-btn { background: none; border: none; color: var(--primary); cursor: pointer; font-size: 14px; font-family: 'DM Sans', sans-serif; padding: 0; margin-bottom: 4px; }
.back-btn:hover { text-decoration: underline; }

/* Grade summary */
.grade-summary {
  display: flex; align-items: center; gap: 32px; margin-bottom: 24px;
  background: linear-gradient(135deg, var(--uwi-green), #004d2e);
  color: white; border: none;
}
.grade-stat { text-align: center; }
.grade-val { font-family: 'Fraunces', serif; font-size: 32px; font-weight: 700; line-height: 1; }
.grade-label { font-size: 12px; opacity: .8; text-transform: uppercase; letter-spacing: .5px; margin-top: 4px; }
.grade-progress { flex: 1; }
.progress-bar { height: 8px; background: rgba(255,255,255,.2); border-radius: 4px; overflow: hidden; margin-bottom: 6px; }
.progress-fill { height: 100%; background: var(--uwi-gold); border-radius: 4px; transition: width .5s ease; }

/* Cards */
.assignments-list { display: flex; flex-direction: column; gap: 14px; }
.assign-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
.assign-title { font-size: 17px; }
.assign-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.meta-chip { display: inline-flex; align-items: center; gap: 4px; padding: 4px 12px; background: var(--surface-2); border-radius: 20px; font-size: 13px; color: var(--text-muted); }
.grade-chip { background: #d4edda; color: #155724; }
.assign-actions { display: flex; align-items: center; gap: 12px; padding-top: 14px; border-top: 1px solid var(--border); }

/* Grade modal rows */
.grade-row { display: flex; align-items: center; gap: 14px; padding: 12px 0; border-bottom: 1px solid var(--border); }
.grade-row:last-child { border-bottom: none; }
.student-info { display: flex; align-items: center; gap: 8px; min-width: 160px; }
.student-avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--uwi-green); color: white; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.sub-content { flex: 1; }
.grade-input-wrap { display: flex; align-items: center; gap: 8px; }
.grade-input { width: 80px; }

/* Empty */
.empty-state { text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state h3 { font-size: 18px; margin-bottom: 8px; }
.mb-3 { margin-bottom: 12px; }

/* Modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 300; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal { background: white; border-radius: var(--radius-lg); width: 100%; max-width: 480px; box-shadow: var(--shadow-lg); max-height: 90vh; overflow-y: auto; }
.modal-lg { max-width: 640px; }
.modal-header { padding: 20px 24px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }
.modal-header h3 { font-size: 17px; }
.close-btn { background: none; border: none; font-size: 18px; cursor: pointer; color: var(--text-muted); }
.modal-body { padding: 20px 24px; }
.modal-footer { padding: 16px 24px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 10px; }
.form-row { display: flex; gap: 12px; }
.empty-tab { text-align: center; color: var(--text-muted); padding: 32px; }
</style>
