import { computed } from 'vue'

export function useRole() {
  const user         = computed(() => JSON.parse(localStorage.getItem('user') || 'null'))
  const role         = computed(() => user.value?.role?.toLowerCase() || '')
  const isAdmin      = computed(() => role.value === 'admin')
  const isStudent    = computed(() => role.value === 'student')
  const isLecturer   = computed(() => role.value === 'lecturer')                    // removed admin
  const canManageCourse = computed(() => role.value === 'lecturer' || role.value === 'admin')
  const canAdmin     = computed(() => isAdmin.value)
  const userId       = computed(() => user.value?.id || null)
  const username     = computed(() => user.value?.username || String(user.value?.id || ''))
  return { user, role, isAdmin, isStudent, isLecturer, canManageCourse, canAdmin, userId, username }
}