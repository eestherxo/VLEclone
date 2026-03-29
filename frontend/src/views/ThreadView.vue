<template>
  <div class="thread-page">
    <div class="container py-6">
      <button class="back-btn" @click="$router.back()">← Back to Forums</button>

      <!-- Forum header -->
      <div class="forum-header card card-body">
        <h1>{{ forum.title || forum.name }}</h1>
        <p class="text-muted text-sm">{{ forum.description }}</p>
      </div>

      <!-- New Thread -->
      <div class="new-thread-box card card-body">
        <h3 class="box-title">Start a Discussion</h3>
        <div class="form-group">
          <input v-model="newThread.title" class="form-control" placeholder="Thread title…" />
        </div>
        <div class="form-group">
          <textarea v-model="newThread.content" class="form-control" rows="3" placeholder="What's on your mind? Share your thoughts, questions, or resources…"></textarea>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-sm text-muted">Be respectful and on-topic.</span>
          <button class="btn btn-primary" @click="createThread" :disabled="creating || !newThread.title || !newThread.content">
            {{ creating ? 'Posting…' : 'Post Thread' }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="spinner"></div>
      <div v-else-if="threads.length === 0" class="empty-state">
        <div class="empty-icon">🧵</div>
        <h3>No threads yet</h3>
        <p>Start the first discussion above!</p>
      </div>

      <!-- Thread list -->
      <div v-else class="threads-list">
        <div v-for="thread in threads" :key="thread.id" class="thread-card card">
          <div class="card-body">
            <!-- Thread OP -->
            <div class="post-header">
              <div class="user-badge">
                <div class="user-avatar" :style="{ background: avatarColor(thread.username) }">
                  {{ thread.username?.slice(0,2).toUpperCase() }}
                </div>
                <div>
                  <span class="username">{{ thread.username }}</span>
                  <span class="post-time">{{ timeAgo(thread.created_at) }}</span>
                </div>
              </div>
              <button class="vote-btn" @click="thread.votes = (thread.votes||0)+1">
                ▲ {{ thread.votes || 0 }}
              </button>
            </div>

            <h3 class="thread-title">{{ thread.title }}</h3>
            <p class="thread-content">{{ thread.content }}</p>

            <!-- Reply button -->
            <div class="thread-actions">
              <button class="action-btn" @click="toggleReply(thread.id)">
                💬 Reply ({{ countReplies(thread.replies) }})
              </button>
              <button class="action-btn" @click="thread.showReplies = !thread.showReplies">
                {{ thread.showReplies ? '▲ Hide' : '▼ Show' }} replies
              </button>
            </div>

            <!-- Inline reply box -->
            <div v-if="replyingTo === thread.id" class="reply-box">
              <textarea v-model="replyContent" class="form-control" rows="2" placeholder="Write your reply…"></textarea>
              <div class="flex gap-2 mt-2 justify-end">
                <button class="btn btn-outline btn-sm" @click="replyingTo = null">Cancel</button>
                <button class="btn btn-primary btn-sm" @click="postReply(thread)" :disabled="!replyContent">Post Reply</button>
              </div>
            </div>

            <!-- Replies (recursive) -->
            <div v-if="thread.showReplies && thread.replies?.length" class="replies-container">
              <ReplyItem
                v-for="reply in thread.replies"
                :key="reply.id"
                :reply="reply"
                :depth="0"
                @reply-posted="(r, parentId) => addNestedReply(thread, r, parentId)"
              />
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

const route = useRoute()
const courseId = computed(() => route.params.id)
const forumId = computed(() => route.params.forumId)

const loading = ref(true)
const forum = ref({})
const threads = ref([])
const newThread = ref({ title: '', content: '' })
const creating = ref(false)
const replyingTo = ref(null)
const replyContent = ref('')

const COLORS = ['#e74c3c','#3498db','#2ecc71','#9b59b6','#f39c12','#1abc9c','#006B3F']
const avatarColor = (name) => COLORS[(name?.charCodeAt(0) || 0) % COLORS.length]

const countReplies = (replies, acc = 0) => {
  if (!replies) return acc
  return replies.reduce((s, r) => countReplies(r.replies, s + 1), acc)
}

const toggleReply = (id) => {
  if (replyingTo.value === id) { replyingTo.value = null; replyContent.value = '' }
  else { replyingTo.value = id; replyContent.value = '' }
}

const timeAgo = (d) => {
  if (!d) return ''
  const diff = Date.now() - new Date(d)
  if (diff < 60000) return 'just now'
  if (diff < 3600000) return `${Math.floor(diff/60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff/3600000)}h ago`
  return `${Math.floor(diff/86400000)}d ago`
}

const createThread = async () => {
  creating.value = true
  try {
    const res = await forumService.createThread(forumId.value, newThread.value)
    threads.value.unshift({ ...res.data, showReplies: false, replies: [], votes: 0 })
    newThread.value = { title: '', content: '' }
  } catch {
    // Demo fallback
    threads.value.unshift({
      id: Date.now(), title: newThread.value.title, content: newThread.value.content,
      username: JSON.parse(localStorage.getItem('user')||'{}').username || 'You',
      created_at: new Date().toISOString(), showReplies: false, replies: [], votes: 0
    })
    newThread.value = { title: '', content: '' }
  } finally {
    creating.value = false
  }
}

const postReply = async (thread) => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const reply = {
    id: Date.now(), content: replyContent.value,
    username: user.username || 'You', created_at: new Date().toISOString(),
    replies: [], votes: 0
  }
  try {
    const res = await forumService.reply(thread.id, { content: replyContent.value })
    thread.replies = thread.replies || []
    thread.replies.unshift({ ...res.data, replies: [], votes: 0 })
  } catch {
    thread.replies = thread.replies || []
    thread.replies.unshift(reply)
  }
  thread.showReplies = true
  replyingTo.value = null
  replyContent.value = ''
}

const addNestedReply = (thread, reply, parentId) => {
  const insert = (replies) => {
    for (const r of replies) {
      if (r.id === parentId) { r.replies = r.replies || []; r.replies.unshift(reply); return true }
      if (r.replies && insert(r.replies)) return true
    }
    return false
  }
  insert(thread.replies)
}

onMounted(async () => {
  try {
    const [fRes, tRes] = await Promise.all([
      forumService.getByCourse(courseId.value),
      forumService.getThreads(forumId.value)
    ])
    const forumList = fRes.data
    forum.value = forumList.find(f => f.id == forumId.value) || {}
    threads.value = tRes.data.map(t => ({ ...t, showReplies: false, replies: t.replies || [] }))
  } catch {
    forum.value = { title: 'Assignment 1 Help', description: 'Discuss ERD design questions here' }
    threads.value = [
      {
        id: 1, title: 'How should we handle the many-to-many relationship?',
        content: 'I\'m confused about the student-course enrollment table. Should it have extra attributes?',
        username: 'john_doe', created_at: new Date(Date.now() - 3600000*5).toISOString(),
        showReplies: true, votes: 4,
        replies: [
          { id: 2, content: 'Yes! Add enrolled_at and status columns.', username: 'jane_smith', created_at: new Date(Date.now() - 3600000*3).toISOString(), votes: 2, replies: [
            { id: 3, content: 'Great point — also consider adding a grade field.', username: 'prof_brown', created_at: new Date(Date.now() - 3600000).toISOString(), votes: 1, replies: [] }
          ]},
        ]
      },
      {
        id: 4, title: 'Useful resources for ERD design',
        content: 'Found this great tutorial: https://dbdiagram.io — super helpful for drawing ERDs quickly.',
        username: 'lisa_m', created_at: new Date(Date.now() - 86400000).toISOString(),
        showReplies: false, votes: 7, replies: []
      }
    ]
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.py-6 { padding: 32px 0 60px; }
.back-btn { background: none; border: none; color: var(--primary); cursor: pointer; font-size: 14px; font-family: 'DM Sans', sans-serif; padding: 0; margin-bottom: 16px; display: block; }
.back-btn:hover { text-decoration: underline; }

.forum-header { margin-bottom: 20px; }
.forum-header h1 { font-size: 22px; margin-bottom: 4px; }

.new-thread-box { margin-bottom: 24px; }
.box-title { font-size: 16px; margin-bottom: 14px; }

.threads-list { display: flex; flex-direction: column; gap: 14px; }
.thread-card { border-left: 4px solid var(--primary); }

.post-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.user-badge { display: flex; align-items: center; gap: 10px; }
.user-avatar { width: 34px; height: 34px; border-radius: 50%; color: white; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.username { font-weight: 600; font-size: 14px; display: block; }
.post-time { font-size: 12px; color: var(--text-muted); }

.thread-title { font-size: 17px; margin-bottom: 8px; }
.thread-content { color: var(--text); font-size: 14px; line-height: 1.65; }

.vote-btn { background: none; border: 1.5px solid var(--border); border-radius: 20px; padding: 4px 12px; font-size: 13px; cursor: pointer; color: var(--text-muted); transition: all .15s; }
.vote-btn:hover { border-color: var(--primary); color: var(--primary); }

.thread-actions { display: flex; gap: 8px; margin-top: 14px; padding-top: 10px; border-top: 1px solid var(--border); }
.action-btn { background: none; border: none; color: var(--text-muted); font-size: 13px; cursor: pointer; font-family: 'DM Sans', sans-serif; padding: 4px 8px; border-radius: 6px; transition: background .12s; }
.action-btn:hover { background: var(--surface-2); color: var(--text); }

.reply-box { margin-top: 14px; padding: 14px; background: var(--surface-2); border-radius: var(--radius); }
.replies-container { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border); }

.empty-state { text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state h3 { font-size: 18px; margin-bottom: 8px; }
</style>
