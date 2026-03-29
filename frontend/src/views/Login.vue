<template>
  <div class="auth-page">
    <div class="auth-bg"><div class="hex-pattern"></div></div>
    <div class="auth-card">
      <div class="auth-logo">
        <div class="logo-badge">VLE</div>
        <div>
          <div class="auth-title">University of the West Indies</div>
          <div class="auth-sub">Virtual Learning Environment</div>
        </div>
      </div>

      <h2 class="form-heading">Welcome back</h2>
      <p class="form-desc">Sign in to continue to your courses</p>

      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <form @submit.prevent="login">
        <div class="form-group">
          <label class="form-label">Student / Staff ID</label>
          <input v-model="form.userID" type="number" class="form-control" placeholder="e.g. 620152345" required />
        </div>
        <div class="form-group">
          <label class="form-label">Password</label>
          <div class="password-wrap">
            <input :type="showPass ? 'text' : 'password'" v-model="form.password" class="form-control" placeholder="Enter your password" required />
            <button type="button" class="eye-btn" @click="showPass = !showPass">{{ showPass ? '🙈' : '👁️' }}</button>
          </div>
        </div>
        <button type="submit" class="btn btn-primary w-full" :disabled="loading">
          <span v-if="loading" class="btn-spinner"></span>
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <div class="auth-footer">
        Don't have an account? <router-link to="/register">Register here</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/api.js'
import api from '../services/api.js'

const router = useRouter()
const form = ref({ userID: '', password: '' })
const error = ref('')
const loading = ref(false)
const showPass = ref(false)

const login = async () => {
  error.value = ''
  loading.value = true
  try {
    // Step 1 — get token from backend
    const res = await authService.login({
      userID: Number(form.value.userID),
      password: form.value.password,
    })

    const token = res.data.access_token
    localStorage.setItem('token', token)

    // Step 2 — fetch real user details using the token
    // The interceptor in api.js will attach the token automatically
    try {
      const meRes = await api.get('/auth/me')
      localStorage.setItem('user', JSON.stringify(meRes.data))
    } catch {
      // /auth/me not yet implemented — decode JWT as fallback
      const payload = JSON.parse(atob(token.split('.')[1]))
      localStorage.setItem('user', JSON.stringify({
        id:       payload.sub,
        username: String(payload.sub),
        role:     payload.role || 'student',
      }))
    }

    router.push('/dashboard')
  } catch (e) {
    error.value =
      e.response?.data?.error ||
      e.response?.data?.message ||
      'Invalid credentials. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; background: var(--uwi-dark); overflow: hidden; }
.auth-bg { position: absolute; inset: 0; overflow: hidden; background: radial-gradient(ellipse at 30% 50%, rgba(0,107,63,.35) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(245,168,0,.2) 0%, transparent 50%); }
.hex-pattern { position: absolute; inset: 0; opacity: .06; background-image: url("data:image/svg+xml,%3Csvg width='56' height='100' viewBox='0 0 56 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M28 66L0 50V16L28 0l28 16v34z' fill='none' stroke='%23fff' stroke-width='1'/%3E%3C/svg%3E"); background-size: 56px 100px; }
.auth-card { background: white; border-radius: 20px; padding: 44px 40px; width: 100%; max-width: 440px; position: relative; z-index: 1; box-shadow: 0 24px 80px rgba(0,0,0,.4); }
.auth-logo { display: flex; align-items: center; gap: 12px; margin-bottom: 32px; }
.logo-badge { background: var(--uwi-green); color: white; font-family: 'Fraunces', serif; font-size: 14px; font-weight: 700; width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.auth-title { font-size: 13px; font-weight: 700; color: var(--uwi-dark); }
.auth-sub { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; }
.form-heading { font-size: 24px; margin-bottom: 4px; }
.form-desc { color: var(--text-muted); font-size: 14px; margin-bottom: 24px; }
.password-wrap { position: relative; }
.password-wrap .form-control { padding-right: 42px; }
.eye-btn { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; font-size: 16px; }
.btn-spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,.4); border-top-color: white; border-radius: 50%; animation: spin .7s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
.auth-footer { text-align: center; margin-top: 20px; font-size: 14px; color: var(--text-muted); }
.auth-footer a { color: var(--primary); font-weight: 500; }
</style>
