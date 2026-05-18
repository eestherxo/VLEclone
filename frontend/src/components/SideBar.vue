<template>
  <aside :class="['sidebar', collapsed && 'collapsed']">
    <nav class="sidebar-nav">

      <button class="collapse-btn" @click="emit('toggle')">
        {{ collapsed ? '»' : '«' }}
      </button>

      <div class="nav-section">
        <router-link to="/home" class="sidebar-link" active-class="active">
          <span class="icon">🏠</span>
          <span v-if="!collapsed">Home</span>
        </router-link>
        <router-link to="/dashboard" class="sidebar-link" active-class="active">
          <span class="icon">📊</span>
          <span v-if="!collapsed">Dashboard</span>
        </router-link>
        <router-link to="/my-courses" class="sidebar-link" active-class="active">
          <span class="icon">📚</span>
          <span v-if="!collapsed">My Courses</span>
        </router-link>
        <router-link v-if="isAdmin" to="/admin" class="sidebar-link" active-class="active">
          <span class="icon">⚙️</span>
          <span v-if="!collapsed">Admin</span>
        </router-link>
      </div>

      <div class="nav-section" v-if="recentCourses.length">
        <div v-if="!collapsed" class="section-label">Recent Courses</div>
        <div
          v-for="c in recentCourses" :key="c.code"
          class="recent-course"
          @click="$router.push(`/course/${c.code}`)"
        >
          <div class="course-dot" :style="{ background: c.color }"></div>
          <span v-if="!collapsed">{{ c.code }}</span>
        </div>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="user-info">
        <div class="avatar-sm">{{ initials }}</div>
        <div v-if="!collapsed">
          <div class="user-name">{{ user?.firstName ? `${user.firstName} ${user.lastName}` : user?.username }}</div>
          <div class="user-role">{{ user?.role }}</div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'

const props = defineProps({ collapsed: Boolean })
const emit  = defineEmits(['toggle'])

const user = computed(() => JSON.parse(localStorage.getItem('user') || 'null'))
const initials = computed(() => {
  const u = user.value
  if (u?.firstName) return (u.firstName[0] + (u.lastName?.[0] || '')).toUpperCase()
  return (u?.username || 'LS').slice(0, 2).toUpperCase()
})
const isAdmin = computed(() => user.value?.role === 'admin')

const courseColors = ['#3498db','#2ecc71','#e74c3c','#9b59b6','#f39c12','#1abc9c']
const recentCourses = ref([])

const loadRecent = () => {
  const stored = JSON.parse(localStorage.getItem('recentCourses') || '[]')
  recentCourses.value = stored.map((code, i) => ({
    code,
    color: courseColors[i % courseColors.length]
  }))
}

onMounted(loadRecent)
</script>

<style scoped>
.sidebar {
  position: fixed; top: var(--nav-height); left: 0; bottom: 0;
  width: var(--sidebar-width); background: var(--surface);
  border-right: 1px solid var(--border); z-index: 50;
  display: flex; flex-direction: column; overflow-y: auto;
  transition: width .2s ease;
}
.sidebar.collapsed { width: 56px; overflow: hidden; }

.sidebar-nav { flex: 1; padding: 16px 12px; }
.nav-section { margin-bottom: 24px; }
.section-label { font-size: 11px; text-transform: uppercase; letter-spacing: .6px; color: var(--text-muted); font-weight: 600; padding: 0 8px; margin-bottom: 6px; }

.collapse-btn {
  width: 100%; background: none; border: none; cursor: pointer;
  text-align: right; padding: 4px 8px 8px; font-size: 18px;
  color: var(--text-muted); margin-bottom: 4px;
  transition: color .15s;
}
.collapse-btn:hover { color: var(--text); }

.sidebar-link {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 12px; border-radius: 8px; color: var(--text);
  font-size: 14px; font-weight: 500; text-decoration: none;
  transition: all .15s; margin-bottom: 2px; white-space: nowrap;
}
.sidebar-link:hover { background: var(--surface-2); text-decoration: none; }
.sidebar-link.active { background: var(--primary-light); color: var(--primary); }
.icon { font-size: 16px; flex-shrink: 0; }

.recent-course {
  display: flex; align-items: center; gap: 8px; padding: 7px 12px;
  border-radius: 8px; cursor: pointer; font-size: 13px;
  color: var(--text-muted); transition: background .15s; white-space: nowrap;
}
.recent-course:hover { background: var(--surface-2); color: var(--text); }
.course-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

.sidebar-footer { padding: 16px; border-top: 1px solid var(--border); }
.user-info { display: flex; align-items: center; gap: 10px; }
.avatar-sm {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--uwi-gold); color: #1a1a1a;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 12px; flex-shrink: 0;
}
.user-name { font-size: 13px; font-weight: 600; white-space: nowrap; }
.user-role { font-size: 11px; color: var(--text-muted); text-transform: capitalize; }

@media (max-width: 768px) { .sidebar { display: none; } }
</style>