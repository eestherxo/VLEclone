<template>
  <div class="thread-page">
    <div class="container py-6">
      <button class="back-btn" @click="$router.back()">← Back to Forums</button>
      <div class="forum-header card card-body">
        <h1>{{ forum.title||forum.name||forum.forumName||'Forum' }}</h1>
        <p v-if="forum.description" class="text-muted text-sm mt-1">{{ forum.description }}</p>
      </div>

      <!-- New thread box -->
      <div class="new-thread card card-body">
        <h3 class="box-title">Start a Discussion</h3>
        <div class="form-group"><input v-model="newThread.title" class="form-control" placeholder="Thread title…" /></div>
        <div class="form-group"><textarea v-model="newThread.content" class="form-control" rows="3" placeholder="Share your thoughts, questions or resources…"></textarea></div>
        <div class="flex justify-between items-center">
          <span class="text-sm text-muted">Be respectful and on-topic.</span>
          <button class="btn btn-primary" @click="createThread" :disabled="creating||!newThread.title||!newThread.content">{{ creating ? 'Posting…':'Post Thread' }}</button>
        </div>
      </div>

      <div v-if="loading" class="spinner"></div>
      <div v-else-if="!threads.length" class="empty-state"><div class="empty-icon">🧵</div><h3>No threads yet</h3><p>Start the first discussion above!</p></div>

      <div v-else class="threads-list">
        <div v-for="t in threads" :key="t.id||t.threadID" class="thread-card card">
          <div class="card-body">
            <div class="post-header">
              <div class="user-badge">
                <div class="ua" :style="{background: ac(t.username)}">{{ (t.username||'?').slice(0,2).toUpperCase() }}</div>
                <div><span class="uname">{{ t.username || t.userID }}</span><span class="ptime">{{ timeAgo(t.created_at||t.createdAt) }}</span></div>
              </div>
              <button class="vote-btn" @click="t.votes=(t.votes||0)+1">▲ {{ t.votes||0 }}</button>
            </div>
            <h3 class="thread-title">{{ t.title }}</h3>
            <p class="thread-content">{{ t.content }}</p>
            <div class="thread-actions">
              <button class="action-btn" @click="toggleReply(t.id||t.threadID)">💬 Reply</button>
              <button class="action-btn" @click="t.showReplies=!t.showReplies">{{ t.showReplies?'▲ Hide':'▼ Show replies' }}</button>
            </div>
            <div v-if="replyingTo===(t.id||t.threadID)" class="reply-box">
              <textarea v-model="replyContent" class="form-control" rows="2" placeholder="Write a reply…"></textarea>
              <div class="flex gap-2 mt-2 justify-end">
                <button class="btn btn-outline btn-sm" @click="replyingTo=null;replyContent=''">Cancel</button>
                <button class="btn btn-primary btn-sm" @click="postReply(t)" :disabled="!replyContent">Post Reply</button>
              </div>
            </div>
            <div v-if="t.showReplies && t.replies?.length" class="replies-wrap">
              <ReplyItem v-for="r in t.replies" :key="r.id||r.replyID" :reply="r" :depth="0"
                @reply-posted="(nr,pid)=>addNested(t,nr,pid)" />
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
import { forumService } from '../services/api.js'
import ReplyItem from '../components/ReplyItem.vue'

const route   = useRoute()
const forumId = computed(() => route.params.forumId)
const courseId= computed(() => route.params.id)

const loading    = ref(true)
const forum      = ref({})
const threads    = ref([])
const newThread  = ref({ title:'', content:'' })
const creating   = ref(false)
const replyingTo = ref(null)
const replyContent = ref('')

const COLORS = ['#e74c3c','#3498db','#2ecc71','#9b59b6','#f39c12','#1abc9c','#006B3F']
const ac = name => COLORS[(name?.charCodeAt(0)||0) % COLORS.length]
const timeAgo = d => {
  if (!d) return ''
  const diff = Date.now() - new Date(d)
  if (diff < 60000)    return 'just now'
  if (diff < 3600000)  return `${Math.floor(diff/60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff/3600000)}h ago`
  return `${Math.floor(diff/86400000)}d ago`
}

const toggleReply = id => { replyingTo.value = replyingTo.value===id ? null : id; replyContent.value='' }

const createThread = async () => {
  creating.value = true
  try {
    const res = await forumService.createThread(forumId.value, newThread.value)
    threads.value.unshift({ ...res.data, showReplies:false, replies:[], votes:0 })
    newThread.value = { title:'', content:'' }
  } catch {
    const u = JSON.parse(localStorage.getItem('user')||'{}')
    threads.value.unshift({ id: Date.now(), title: newThread.value.title, content: newThread.value.content, username: u.username||String(u.id), created_at: new Date().toISOString(), showReplies:false, replies:[], votes:0 })
    newThread.value = { title:'', content:'' }
  } finally { creating.value = false }
}

const postReply = async t => {
  const u = JSON.parse(localStorage.getItem('user')||'{}')
  const nr = { id: Date.now(), content: replyContent.value, username: u.username||String(u.id), created_at: new Date().toISOString(), votes:0, replies:[] }
  try {
    const res = await forumService.reply(t.id||t.threadID, { content: replyContent.value })
    t.replies = t.replies||[]; t.replies.unshift({ ...res.data, replies:[], votes:0 })
  } catch { t.replies = t.replies||[]; t.replies.unshift(nr) }
  t.showReplies=true; replyingTo.value=null; replyContent.value=''
}

const addNested = (t, reply, parentId) => {
  const ins = (list) => { for (const r of list) { if ((r.id||r.replyID)===parentId) { r.replies=r.replies||[]; r.replies.unshift(reply); return true } if (r.replies&&ins(r.replies)) return true } return false }
  ins(t.replies)
}

onMounted(async () => {
  try {
    const [fRes, tRes] = await Promise.all([forumService.getByCourse(courseId.value), forumService.getThreads(forumId.value)])
    const list = fRes.data.forums||fRes.data
    forum.value = list.find(f=>(f.id||f.forumID)==forumId.value) || {}
    threads.value = (tRes.data.threads||tRes.data).map(t=>({...t,showReplies:false,replies:t.replies||[],votes:0}))
  } catch { forum.value = { title: 'Forum' } }
  finally { loading.value = false }
})
</script>

<style scoped>
.py-6 { padding: 32px 0 60px; }
.back-btn { background: none; border: none; color: var(--primary); cursor: pointer; font-size: 14px; font-family:'DM Sans',sans-serif; padding:0; margin-bottom:16px; display:block; }
.back-btn:hover { text-decoration: underline; }
.forum-header { margin-bottom: 20px; }
.forum-header h1 { font-size: 22px; }
.new-thread { margin-bottom: 24px; }
.box-title { font-size: 16px; margin-bottom: 14px; }
.threads-list { display: flex; flex-direction: column; gap: 14px; }
.thread-card { border-left: 4px solid var(--primary); }
.post-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.user-badge { display: flex; align-items: center; gap: 10px; }
.ua { width: 34px; height: 34px; border-radius: 50%; color: white; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.uname { font-weight: 600; font-size: 14px; display: block; }
.ptime { font-size: 12px; color: var(--text-muted); }
.thread-title { font-size: 17px; margin-bottom: 8px; }
.thread-content { font-size: 14px; line-height: 1.65; }
.vote-btn { background: none; border: 1.5px solid var(--border); border-radius: 20px; padding: 4px 12px; font-size: 13px; cursor: pointer; color: var(--text-muted); transition: all .15s; }
.vote-btn:hover { border-color: var(--primary); color: var(--primary); }
.thread-actions { display: flex; gap: 8px; margin-top: 14px; padding-top: 10px; border-top: 1px solid var(--border); }
.action-btn { background: none; border: none; color: var(--text-muted); font-size: 13px; cursor: pointer; font-family:'DM Sans',sans-serif; padding: 4px 8px; border-radius: 6px; transition: background .12s; }
.action-btn:hover { background: var(--surface-2); color: var(--text); }
.reply-box { margin-top: 14px; padding: 14px; background: var(--surface-2); border-radius: var(--radius); }
.replies-wrap { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border); }
.empty-state { text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state h3 { font-size: 18px; margin-bottom: 8px; }
</style>
