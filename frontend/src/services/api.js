import axios from 'axios'

const api = axios.create({
  baseURL: 'https://vleclone-zny0.onrender.com',
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.clear()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────
export const authService = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  me: () => api.get('/auth/login'),
}

// ── Courses ───────────────────────────────────────────────────
export const courseService = {
  getMyCourses: () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const role = user.role?.toLowerCase()
    if (role === 'lecturer') return api.get(`/courses/lecturer/${user.id}`)
    if (role === 'admin') return api.get('/courses/all')
    return api.get(`/courses/student/${user.id}`)
  },
  getAll: () => api.get('/courses/all'),                    // was /courses/list
  getStudentCourses: (id) => api.get(`/courses/student/${id}`),          // was /student/${id}/courses
  getLecturerCourses: (id) => api.get(`/courses/lecturer/${id}`),         // was /courses/list/lecturer/${id}
  create: (data) => api.post('/courses/create', {
    courseCode: data.code || data.courseCode,
    courseName: data.name || data.courseName,
  }),
  enroll: (courseCode) => api.post('/courses/enroll-student', {
    studentID: JSON.parse(localStorage.getItem('user') || '{}').id,  // was studentId — backend expects studentID
    courseCode,
  }),
  assignLecturer: (lecturerId, courseCode) => api.post('/courses/assign-lecturer', { lecturerId, courseCode }),
  getMembers: (courseCode) => api.get(`/courses/members/${courseCode}`),
  getLecturers: () => api.get('/courses/lecturers'),
}

// ── Assignments ───────────────────────────────────────────────
// Backend: /assignments/course/<code>, /assignments/create
//          /assignments/<id>/submit, /assignments/<id>/grade/<studentId>
//          /assignments/<id>/submissions
export const assignmentService = {
  getByCourse: (courseCode) => api.get(`/assignments/course/${courseCode}`),
  create: (data) => api.post('/assignments/create', {
    courseCode: data.courseCode,
    assignmentName: data.title || data.assignmentName,
    dueDate: data.due_date || data.dueDate,
  }),
  submit: (assignmentId, data) => api.post('/events/assignment/submit', {
    assignmentID: assignmentId,
    studentID: JSON.parse(localStorage.getItem('user') || '{}').id,
    filePath: data.content || data.filePath,
  }),
  grade: (assignmentId, studentId, data) => api.post('/events/assignment/grade', {
    assignmentID: assignmentId,
    studentID: studentId,
    grade: data.grade,
  }),
  getSubmissions: (assignmentId) => api.get(`/assignments/${assignmentId}/submissions`),
}

// ── Course Content ────────────────────────────────────────────
// Backend: GET /content/course/<code>, POST /content/create
export const contentService = {
  getByCourse: (courseCode) => api.get(`/content/course/${courseCode}`),
  createSection: (data) => api.post('/content/section/create', {
    courseCode: data.courseCode,
    secName: data.section || data.secName,
  }),
  createItem: (data) => api.post('/content/section/item/create', {
    secID: data.secID,
    contentName: data.title || data.contentName,
    type: data.type,
    content: data.url || data.content,
  }),
}
// ── Forums ────────────────────────────────────────────────────
// Backend: GET  /forums/course/<code>
//          POST /forums/create
//          GET  /forums/<id>/threads
//          POST /forums/<id>/threads
//          POST /forums/threads/<id>/reply
export const forumService = {
  getByCourse: (courseCode) => api.get(`/forums/course/${courseCode}`),
  create: (data) => api.post('/forums/course', {        // was /forums/create
    courseCode: data.courseCode,
    forumName: data.title || data.forumName,
  }),
  getThreads: (forumId) => api.get(`/threads/forum/${forumId}`),     // was /forums/${forumId}/threads
  createThread: (forumId, data) => api.post('/threads/', {                   // was /forums/${forumId}/threads
    forumID: forumId,
    threadTitle: data.title,
    content: data.content,
  }),
  reply: (threadId, data) => api.post(`/threads/reply/${threadId}`, {  // was /forums/threads/${threadId}/reply
    content: data.content,
  }),
  getReplies: (threadId) => api.get(`/threads/reply/${threadId}`),    // new — was missing
}

// ── Calendar Events ───────────────────────────────────────────
// Backend: GET /events/course/<code>
//          GET /events/student/<id>?date=YYYY-MM-DD
//          POST /events/create
export const eventService = {
  getByCourse: (courseCode) => api.get(`/events/course/${courseCode}`),
  getByStudentDate: (studentId, date) => api.get(`/events/student/${studentId}/date/${date}`),
  create: (data) => api.post('/events/course', {
    courseCode: data.courseCode,
    eventName: data.eventName,
    createdDate: data.createdDate,
    dueDate: data.dueDate,
  }),
}

// ── Reports (admin only) ──────────────────────────────────────
export const reportService = {
  largeCourses: () => api.get('/reports/large-courses'),
  busyStudents: () => api.get('/reports/busy-students'),
  busyLecturers: () => api.get('/reports/busy-lecturers'),
  topEnrolled: () => api.get('/reports/top-enrolled'),
  topStudents: () => api.get('/reports/top-students'),
}

export default api