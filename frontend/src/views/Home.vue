<template>
  <div class="home-page">
    <div class="container">

      <!-- Welcome header -->
      <div class="welcome-header">
        <div>
          <h1>Welcome back, {{ user?.firstName || user?.username || 'Student' }} 👋</h1>
          <p class="text-muted">Here's what's coming up for you.</p>
        </div>
        <div class="today-badge">
          <div class="today-day">{{ todayDay }}</div>
          <div class="today-month">{{ todayMonth }}</div>
        </div>
      </div>

      <div class="home-grid">

        <!-- My Courses -->
        <div class="home-section">
          <div class="section-header">
            <h2>My Courses</h2>
            <router-link to="/dashboard" class="see-all">Browse all →</router-link>
          </div>
          <div v-if="coursesLoading" class="spinner"></div>
          <div v-else-if="!courses.length" class="empty-box">
            <div class="empty-icon">📚</div>
            <p>No courses yet. <router-link to="/dashboard">Browse courses</router-link> to enrol.</p>
          </div>
          <div v-else class="mini-course-list">
            <div
              v-for="c in courses" :key="c.courseCode"
              class="mini-course-card"
              @click="$router.push(`/course/${c.courseCode}`)"
            >
              <div class="mini-banner" :style="{ background: courseColor(c.courseCode) }">
                <span class="mini-code">{{ c.courseCode }}</span>
              </div>
              <div class="mini-info">
                <div class="mini-name">{{ c.courseName }}</div>
                <span class="badge badge-green">Enrolled</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Events -->
        <div class="home-section">
          <div class="section-header">
            <h2>Upcoming Events</h2>
          </div>
          <div v-if="eventsLoading" class="spinner"></div>
          <div v-else-if="!upcomingEvents.length" class="empty-box">
            <div class="empty-icon">📅</div>
            <p>No upcoming events.</p>
          </div>
          <div v-else class="events-feed">
            <div v-for="e in upcomingEvents" :key="e.eventID || e.id" class="event-card">
              <div class="event-date-col">
                <div class="event-month-label">{{ eventMonth(e.eventDate || e.date) }}</div>
                <div class="event-day-label">{{ eventDay(e.eventDate || e.date) }}</div>
              </div>
              <div class="event-details">
                <div class="event-title">{{ e.eventName || e.title }}</div>
                <div class="event-course text-muted text-sm">{{ e.courseCode }}</div>
              </div>
              <div class="event-dot" :style="{ background: courseColor(e.courseCode) }"></div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { courseService, eventService } from '../services/api.js'

const user = computed(() => JSON.parse(localStorage.getItem('user') || 'null'))

const courses       = ref([])
const coursesLoading= ref(true)
const eventsLoading = ref(true)
const allEvents     = ref([])

const COLORS = ['#3a6186','#89216b','#1c6c3a','#7b4397','#c0392b','#16a085','#2c3e50','#e67e22']
const courseColor = code => COLORS[(code?.charCodeAt(0) || 0) % COLORS.length]

const now = new Date()
const todayDay   = now.getDate()
const todayMonth = now.toLocaleString('default', { month: 'short' }).toUpperCase()

const eventMonth = d => d ? new Date(d).toLocaleString('default', { month: 'short' }).toUpperCase() : ''
const eventDay   = d => d ? new Date(d).getDate() : ''

const upcomingEvents = computed(() =>
  allEvents.value
    .filter(e => new Date(e.eventDate || e.date) >= now)
    .sort((a, b) => new Date(a.eventDate || a.date) - new Date(b.eventDate || b.date))
    .slice(0, 8)
)

onMounted(async () => {
  // load enrolled courses
  try {
    const res = await courseService.getMyCourses()
    courses.value = res.data.courses || res.data
  } catch {}
  coursesLoading.value = false

  // load events for each course
  try {
    const eventPromises = courses.value.map(c =>
      eventService.getByCourse(c.courseCode)
        .then(r => (r.data.events || r.data).map(e => ({ ...e, courseCode: c.courseCode })))
        .catch(() => [])
    )
    const results = await Promise.all(eventPromises)
    allEvents.value = results.flat()
  } catch {}
  eventsLoading.value = false
})
</script>

<style scoped>
.home-page { padding: calc(var(--nav-height) + 32px) 0 60px; }

.welcome-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 32px;
}
.welcome-header h1 { font-size: 26px; margin-bottom: 4px; }

.today-badge {
  text-align: center; background: var(--uwi-green); color: white;
  border-radius: 12px; padding: 10px 20px; min-width: 70px;
}
.today-day   { font-size: 28px; font-weight: 700; line-height: 1; }
.today-month { font-size: 12px; font-weight: 600; letter-spacing: 1px; opacity: .85; }

.home-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
}
@media (max-width: 768px) { .home-grid { grid-template-columns: 1fr; } }

.home-section { display: flex; flex-direction: column; gap: 14px; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
.section-header h2 { font-size: 18px; }
.see-all { font-size: 13px; color: var(--primary); text-decoration: none; font-weight: 500; }
.see-all:hover { text-decoration: underline; }

.empty-box {
  text-align: center; padding: 32px 16px;
  background: var(--surface); border-radius: var(--radius);
  border: 1px dashed var(--border); color: var(--text-muted);
}
.empty-icon { font-size: 32px; margin-bottom: 8px; }

/* Mini course cards */
.mini-course-list { display: flex; flex-direction: column; gap: 10px; }
.mini-course-card {
  display: flex; align-items: center; gap: 12px;
  background: white; border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden; cursor: pointer;
  transition: box-shadow .15s;
}
.mini-course-card:hover { box-shadow: var(--shadow); }
.mini-banner {
  width: 56px; height: 56px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.mini-code { color: white; font-size: 9px; font-weight: 700; text-align: center; padding: 4px; line-height: 1.2; }
.mini-info { flex: 1; padding: 10px 12px 10px 0; }
.mini-name { font-size: 13px; font-weight: 500; margin-bottom: 4px; }

/* Events feed */
.events-feed { display: flex; flex-direction: column; gap: 10px; }
.event-card {
  display: flex; align-items: center; gap: 14px;
  background: white; border: 1px solid var(--border);
  border-radius: var(--radius); padding: 12px 14px;
}
.event-date-col { text-align: center; min-width: 40px; }
.event-month-label { font-size: 10px; font-weight: 700; color: var(--primary); text-transform: uppercase; }
.event-day-label   { font-size: 22px; font-weight: 700; color: var(--primary); line-height: 1; }
.event-details { flex: 1; }
.event-title  { font-size: 14px; font-weight: 500; }
.event-course { margin-top: 2px; }
.event-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
</style>