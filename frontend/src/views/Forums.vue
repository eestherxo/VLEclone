<template>
  <div class="forums-page">
    <div class="container py-6">
      <div class="page-header">
        <div>
          <button class="back-btn" @click="$router.back()">← Back to Course</button>
          <h1>Forums</h1>
          <p class="text-muted">{{ course.code }} – {{ course.name }}</p>
        </div>
        <button class="btn btn-primary" @click="showCreate = true">+ New Forum</button>
      </div>

      <div v-if="loading" class="spinner"></div>
      <div v-else-if="forums.length === 0" class="empty-state">
        <div class="empty-icon">💬</div>
        <h3>No forums yet</h3>
        <p>Create the first forum for this course.</p>
      </div>
      <div v-else class="forums-grid">
        <div
          v-for="f in forums" :key="f.id"
          class="forum-card card"
          @click="$router.push(`/course/${courseId}/forums/${f.id}`)"
        >
          <div class="card-body">
            <div class="forum-icon">💬</div>
            <h3 class="forum-title">{{ f.name || f.title }}</h3>
            <p class="text-muted text-sm">{{ f.description || 'Click to view discussions' }}</p>
            <div class="forum-stats">
              <span class="stat">🧵 {{ f.thread_count || 0 }} threads</span>
              <span class="stat">👁 {{ f.post_count || 0 }} posts</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Forum Modal -->
    <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Create Forum</h3>
          <button class="close-btn" @click="showCreate = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="createError" class="alert alert-error">{{ createError }}</div>
          <div class="form-group">
            <label class="form-label">Forum Title</label>
            <input v-model="newForum.title" class="form-control" placeholder="e.g. Week 3 – SQL Queries Discussion" />
          </div>
          <div class="form-group">
            <label class="form-label">Description (optional)</label>
            <textarea v-model="newForum.description" class="form-control" rows="3" placeholder="What is this forum about?"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showCreate = false">Cancel</button>
          <button class="btn btn-primary" @click="createForum" :disabled="creating">
            {{ creating ? 'Creating…' : 'Create Forum' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { forumService, courseService } from '../services/api.js'

const route = useRoute()
const courseId = computed(() => route.params.id)
const loading = ref(true)
const course = ref({})
const forums = ref([])
const showCreate = ref(false)
const newForum = ref({ title: '', description: '' })
const creating = ref(false)
const createError = ref('')

const createForum = async () => {
  createError.value = ''
  creating.value = true
  try {
    const res = await forumService.create({ ...newForum.value, course_id: courseId.value })
    forums.value.push(res.data)
    showCreate.value = false
    newForum.value = { title: '', description: '' }
  } catch (e) {
    createError.value = e.response?.data?.message || 'Failed to create forum.'
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  try {
    const [cRes, fRes] = await Promise.all([
      courseService.getById(courseId.value),
      forumService.getByCourse(courseId.value)
    ])
    course.value = cRes.data
    forums.value = fRes.data
  } catch {
    course.value = { code: 'COMP3161', name: 'Intro to DBMS' }
    forums.value = [
      { id: 1, title: 'Week 1 – Introductions', description: 'Introduce yourself to the class', thread_count: 24, post_count: 87 },
      { id: 2, title: 'Assignment 1 Help', description: 'Discuss ERD design questions here', thread_count: 12, post_count: 45 },
      { id: 3, title: 'SQL Tips & Resources', description: 'Share useful SQL resources', thread_count: 8, post_count: 30 },
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
.back-btn { background: none; border: none; color: var(--primary); cursor: pointer; font-size: 14px; font-family: 'DM Sans', sans-serif; padding: 0; }
.back-btn:hover { text-decoration: underline; }

.forums-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.forum-card { cursor: pointer; transition: all .2s; }
.forum-card:hover { box-shadow: var(--shadow); transform: translateY(-2px); }
.forum-icon { font-size: 28px; margin-bottom: 10px; }
.forum-title { font-size: 16px; margin-bottom: 6px; }
.forum-stats { display: flex; gap: 14px; margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border); }
.stat { font-size: 13px; color: var(--text-muted); }

.empty-state { text-align: center; padding: 80px 20px; }
.empty-icon { font-size: 52px; margin-bottom: 16px; }
.empty-state h3 { font-size: 20px; margin-bottom: 8px; }

.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 300; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal { background: white; border-radius: var(--radius-lg); width: 100%; max-width: 480px; box-shadow: var(--shadow-lg); }
.modal-header { padding: 20px 24px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }
.modal-header h3 { font-size: 17px; }
.close-btn { background: none; border: none; font-size: 18px; cursor: pointer; color: var(--text-muted); }
.modal-body { padding: 20px 24px; }
.modal-footer { padding: 16px 24px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 10px; }
</style>
