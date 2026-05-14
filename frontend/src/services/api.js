import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
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
  login:    (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  me:       ()     => api.get('/auth/login'),
}

// ── Courses ───────────────────────────────────────────────────
export const courseService = {
getMyCourses: () => api.get(`/courses/student/${JSON.parse(localStorage.getItem('user')||'{}').id}`),
  getAll:            ()                       => api.get('/courses/all'),                    // was /courses/list
  getStudentCourses: (id)                     => api.get(`/courses/student/${id}`),          // was /student/${id}/courses
  getLecturerCourses:(id)                     => api.get(`/courses/lecturer/${id}`),         // was /courses/list/lecturer/${id}
  create:            (data)                   => api.post('/courses/create', {
                                                   courseCode: data.code || data.courseCode,
                                                   courseName: data.name || data.courseName,
                                                 }),
  enroll:            (courseCode)             => api.post('/courses/enroll-student', {
                                                   studentID: JSON.parse(localStorage.getItem('user')||'{}').id,  // was studentId — backend expects studentID
                                                   courseCode,
                                                 }),
  assignLecturer:    (lecturerId, courseCode) => api.post('/courses/assign-lecturer', { lecturerId, courseCode }),
  getMembers:        (courseCode)             => api.get(`/courses/members/${courseCode}`),
}

// ── Assignments ───────────────────────────────────────────────
// Backend: /assignments/course/<code>, /assignments/create
//          /assignments/<id>/submit, /assignments/<id>/grade/<studentId>
//          /assignments/<id>/submissions
export const assignmentService = {
  getByCourse:    (courseCode)                     => api.get(`/assignments/course/${courseCode}`),
  create:         (data)                           => api.post('/assignments/create', {
                                                        courseCode:     data.courseCode,
                                                        assignmentName: data.title || data.assignmentName,
                                                        dueDate:        data.due_date || data.dueDate,
                                                      }),
  submit:         (assignmentId, data)             => api.post(`/assignments/${assignmentId}/submit`, data),
  grade:          (assignmentId, studentId, data)  => api.post(`/assignments/${assignmentId}/grade/${studentId}`, data),
  getSubmissions: (assignmentId)                   => api.get(`/assignments/${assignmentId}/submissions`),
}

// ── Course Content ────────────────────────────────────────────
// Backend: GET /content/course/<code>, POST /content/create
export const contentService = {
  getByCourse: (courseCode) => api.get(`/content/course/${courseCode}`),
  create:      (data)       => api.post('/content/create', data),
}

// ── Forums ────────────────────────────────────────────────────
// Backend: GET  /forums/course/<code>
//          POST /forums/create
//          GET  /forums/<id>/threads
//          POST /forums/<id>/threads
//          POST /forums/threads/<id>/reply
export const forumService = {
  getByCourse:  (courseCode)         => api.get(`/forums/course/${courseCode}`),
  create:       (data)               => api.post('/forums/create', {
                                          courseCode: data.courseCode,
                                          forumName:  data.title || data.forumName,
                                        }),
  getThreads:   (forumId)            => api.get(`/forums/${forumId}/threads`),
  createThread: (forumId, data)      => api.post(`/forums/${forumId}/threads`, {
                                          title:   data.title,
                                          content: data.content,
                                        }),
  reply:        (threadId, data)     => api.post(`/forums/threads/${threadId}/reply`, {
                                          content: data.content,
                                        }),
}

// ── Calendar Events ───────────────────────────────────────────
// Backend: GET /events/course/<code>
//          GET /events/student/<id>?date=YYYY-MM-DD
//          POST /events/create
export const eventService = {
  getByCourse:     (courseCode)          => api.get(`/events/course/${courseCode}`),
  getByStudentDate:(studentId, date)     => api.get(`/events/student/${studentId}?date=${date}`),
  create:          (data)                => api.post('/events/create', {
                                              courseCode: data.courseCode,
                                              eventName:  data.title || data.eventName,
                                              eventDate:  data.date  || data.eventDate,
                                            }),
}

// ── Reports (admin only) ──────────────────────────────────────
export const reportService = {
  largeCourses:  () => api.get('/reports/large-courses'),
  busyStudents:  () => api.get('/reports/busy-students'),
  busyLecturers: () => api.get('/reports/busy-lecturers'),
  topEnrolled:   () => api.get('/reports/top-enrolled'),
  topStudents:   () => api.get('/reports/top-students'),
}

export default api