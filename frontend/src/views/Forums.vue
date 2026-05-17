<template>
  <div class="forums-page">
    <div class="container py-6">
      <button class="back-btn" @click="$router.back()">← Back to Course</button>
      <div class="page-header">
        <h1>Forums</h1>
        <button class="btn btn-primary" @click="showCreate = true">+ New Forum</button>
      </div>
      <div v-if="loading" class="spinner"></div>
      <div v-else-if="!forums.length" class="empty-state"><div class="empty-icon">💬</div><h3>No forums yet</h3><p>Start the first discussion.</p></div>
      <div v-else class="forums-grid">
        <div v-for="f in forums" :key="f.id||f.forumID" class="forum-card card"
          @click="$router.push(`/course/${courseId}/forums/${f.id||f.forumID}`)">
          <div class="card-body">
            <div class="forum-icon">💬</div>
            <h3 class="forum-title">{{ f.title||f.name||f.forumName }}</h3>
            <p class="text-muted text-sm">{{ f.description || 'Click to view discussions' }}</p>
            <div class="forum-stats">
              <span class="stat">🧵 {{ f.thread_count||0 }} threads</span>
              <span class="stat">📝 {{ f.post_count||0 }} posts</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate=false">
      <div class="modal">
        <div class="modal-header"><h3>Create Forum</h3><button class="close-btn" @click="showCreate=false">✕</button></div>
        <div class="modal-body">
          <div v-if="err" class="alert alert-error">{{ err }}</div>
          <div class="form-group"><label class="form-label">Title</label><input v-model="newForum.title" class="form-control" placeholder="e.g. Week 3 – SQL Queries" /></div>
          <div class="form-group"><label class="form-label">Description</label><textarea v-model="newForum.description" class="form-control" rows="2"></textarea></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showCreate=false">Cancel</button>
          <button class="btn btn-primary" @click="create" :disabled="creating">{{ creating ? 'Creating…':'Create' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { forumService } from '../services/api.js'

const route    = useRoute()
const courseId = computed(() => route.params.id)
const loading  = ref(true)
const forums   = ref([])
const showCreate = ref(false)
const newForum   = ref({ title:'', description:'' })
const creating   = ref(false)
const err        = ref('')

const create = async () => {
  err.value = ''; creating.value = true
  try {
    await forumService.create({ ...newForum.value, courseCode: courseId.value })
    // refetch instead of pushing res.data
    const r = await forumService.getByCourse(courseId.value)
    forums.value = r.data.forums || r.data
    showCreate.value = false
    newForum.value = { title: '', description: '' }
  } catch(e) { err.value = e.response?.data?.error || 'Failed.' }
  finally { creating.value = false }
}

onMounted(async () => {
  try { const r = await forumService.getByCourse(courseId.value); forums.value = r.data.forums||r.data }
  catch {} finally { loading.value = false }
})
</script>

<style scoped>
.py-6 { padding: 32px 0 60px; }
.back-btn { background: none; border: none; color: var(--primary); cursor: pointer; font-size: 14px; font-family: 'DM Sans', sans-serif; padding: 0; margin-bottom: 16px; display: block; }
.back-btn:hover { text-decoration: underline; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-header h1 { font-size: 26px; }
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
