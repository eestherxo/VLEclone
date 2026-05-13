<template>
  <div class="reply-item" :style="{ marginLeft: depth * 24 + 'px' }">
    <div class="reply-line"></div>
    <div class="reply-body">
      <div class="reply-header">
        <div class="user-badge">
          <div class="user-avatar" :style="{ background: avatarColor(reply.username) }">
            {{ reply.username?.slice(0,2).toUpperCase() }}
          </div>
          <div>
            <span class="username">{{ reply.username }}</span>
            <span class="post-time">{{ timeAgo(reply.created_at) }}</span>
          </div>
        </div>
        <button class="vote-btn" @click="reply.votes = (reply.votes||0)+1">
          ▲ {{ reply.votes || 0 }}
        </button>
      </div>

      <p class="reply-content">{{ reply.content }}</p>

      <div class="reply-actions">
        <button class="action-btn" @click="showBox = !showBox">
          💬 Reply
        </button>
        <button v-if="reply.replies?.length" class="action-btn" @click="showReplies = !showReplies">
          {{ showReplies ? '▲ Hide' : `▼ ${reply.replies.length} replies` }}
        </button>
      </div>

      <div v-if="showBox" class="reply-box">
        <textarea v-model="replyContent" class="form-control" rows="2" placeholder="Reply to this…"></textarea>
        <div class="flex gap-2 mt-2 justify-end">
          <button class="btn btn-outline btn-sm" @click="showBox = false; replyContent = ''">Cancel</button>
          <button class="btn btn-primary btn-sm" @click="postReply" :disabled="!replyContent">Reply</button>
        </div>
      </div>

      <div v-if="showReplies && reply.replies?.length" class="nested-replies">
        <ReplyItem
          v-for="r in reply.replies"
          :key="r.id"
          :reply="r"
          :depth="depth + 1"
          @reply-posted="(nr, pid) => $emit('reply-posted', nr, pid)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { forumService } from '../services/api.js'

const props = defineProps({ reply: Object, depth: { type: Number, default: 0 } })
const emit = defineEmits(['reply-posted'])

const showBox = ref(false)
const showReplies = ref(true)
const replyContent = ref('')

const COLORS = ['#e74c3c','#3498db','#2ecc71','#9b59b6','#f39c12','#1abc9c','#006B3F']
const avatarColor = (name) => COLORS[(name?.charCodeAt(0) || 0) % COLORS.length]
const timeAgo = (d) => {
  if (!d) return ''
  const diff = Date.now() - new Date(d)
  if (diff < 60000) return 'just now'
  if (diff < 3600000) return `${Math.floor(diff/60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff/3600000)}h ago`
  return `${Math.floor(diff/86400000)}d ago`
}

const postReply = async () => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const nr = {
    id: Date.now(), content: replyContent.value,
    username: user.username || 'You',
    created_at: new Date().toISOString(), votes: 0, replies: []
  }
  try {
    const res = await forumService.reply(props.reply.id, { content: replyContent.value })
    emit('reply-posted', { ...res.data, replies: [], votes: 0 }, props.reply.id)
  } catch {
    emit('reply-posted', nr, props.reply.id)
  }
  props.reply.replies = props.reply.replies || []
  props.reply.replies.unshift(nr)
  showBox.value = false
  replyContent.value = ''
  showReplies.value = true
}
</script>

<style scoped>
.reply-item { position: relative; display: flex; gap: 0; margin-top: 10px; }
.reply-line { width: 2px; background: var(--border); flex-shrink: 0; border-radius: 2px; margin-right: 12px; margin-top: 4px; }
.reply-body { flex: 1; }
.reply-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.user-badge { display: flex; align-items: center; gap: 8px; }
.user-avatar { width: 28px; height: 28px; border-radius: 50%; color: white; font-size: 10px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.username { font-weight: 600; font-size: 13px; display: block; }
.post-time { font-size: 11px; color: var(--text-muted); }
.vote-btn { background: none; border: 1px solid var(--border); border-radius: 20px; padding: 2px 10px; font-size: 12px; cursor: pointer; color: var(--text-muted); transition: all .15s; }
.vote-btn:hover { border-color: var(--primary); color: var(--primary); }
.reply-content { font-size: 14px; color: var(--text); line-height: 1.6; }
.reply-actions { display: flex; gap: 6px; margin-top: 8px; }
.action-btn { background: none; border: none; color: var(--text-muted); font-size: 12px; cursor: pointer; font-family: 'DM Sans', sans-serif; padding: 3px 7px; border-radius: 5px; transition: background .12s; }
.action-btn:hover { background: var(--surface-2); color: var(--text); }
.reply-box { margin-top: 10px; padding: 12px; background: var(--surface-2); border-radius: var(--radius); }
.nested-replies { margin-top: 8px; }
</style>
