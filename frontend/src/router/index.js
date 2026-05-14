import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import CoursePage from '../views/CoursePage.vue'
import Assignments from '../views/Assignments.vue'
import Forums from '../views/Forums.vue'
import ThreadView from '../views/ThreadView.vue'
import AdminPanel from '../views/AdminPanel.vue'
import Home from '../views/Home.vue'
import MyCourses from '../views/MyCourses.vue'

const routes = [
  { path: '/',          redirect: '/home' },
  { path: '/login',     component: Login,      meta: { guest: true } },
  { path: '/register',  component: Register,   meta: { guest: true } },
  { path: '/home',      component: Home,       meta: { auth: true } },   // calendar
  { path: '/dashboard', component: Dashboard,  meta: { auth: true } },   // browse courses
  { path: '/course/:id',                   component: CoursePage,   meta: { auth: true } },
  { path: '/course/:id/assignments',       component: Assignments,  meta: { auth: true } },
  { path: '/course/:id/forums',            component: Forums,       meta: { auth: true } },
  { path: '/course/:id/forums/:forumId',   component: ThreadView,   meta: { auth: true } },
  { path: '/admin',     component: AdminPanel, meta: { auth: true, role: 'admin' } },
  { path: '/my-courses', component: MyCourses, meta: { auth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')

 if (to.meta.guest && token) return next('/home')
if (to.meta.role && user?.role !== to.meta.role) return next('/home')
  next()
})

export default router