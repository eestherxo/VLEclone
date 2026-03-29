import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  headers: { 'Content-Type': 'application/json' }
})

// Attach JWT token to every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto logout on 401
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────
export const authService = {
  login: (credentials) => api.post('/auth/login', {userID: credentials.userID, password: credentials.password}),
  register: (data) => api.post('/auth/register', data),
}

// ── Courses ───────────────────────────────────────────
export const courseService = {
  getAll: () => api.get('/courses/list'),
  getStudentCourses: (studentId) => api.get(`/courses/list/${studentId}`),
  getLecturerCourses: (lecturerId) => api.get(`/courses/list/${lecturerId}`),
  create: (data) => api.post('/courses/create', data),
  assignLecturer: (data) => api.post('/courses/assign-lecturer', data),
  enrollStudent: (data) => api.post('/courses/enroll-student', data),
  getMembers: (courseCode) => api.get(`/courses/members/${courseCode}`),
}

// ── Assignments ───────────────────────────────────────
export const assignmentService = {
  getByCourse: (courseId) => api.get(`/assignments/course/${courseId}`),
  submit: (assignmentId, data) => api.post(`/assignments/${assignmentId}/submit`, data),
  grade: (assignmentId, studentId, data) => api.post(`/assignments/${assignmentId}/grade/${studentId}`, data),
  create: (data) => api.post('/assignments', data),
}

// ── Content ───────────────────────────────────────────
export const contentService = {
  getByCourse: (courseId) => api.get(`/content/course/${courseId}`),
  create: (data) => api.post('/content', data),
}

// ── Forums ────────────────────────────────────────────
export const forumService = {
  getByCourse: (courseId) => api.get(`/forums/course/${courseId}`),
  create: (data) => api.post('/forums', data),
  getThreads: (forumId) => api.get(`/forums/${forumId}/threads`),
  createThread: (forumId, data) => api.post(`/forums/${forumId}/threads`, data),
  reply: (threadId, data) => api.post(`/forums/threads/${threadId}/reply`, data),
}

// ── Events ────────────────────────────────────────────
export const eventService = {
  getByCourse: (courseId) => api.get(`/events/course/${courseId}`),
  create: (data) => api.post('/events', data),
}

export default api
