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

      <h2 class="form-heading">Create account</h2>
      <p class="form-desc">Join the Virtual Learning Environment</p>

      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="success" class="alert alert-success">
        Account created! <router-link to="/login">Sign in here</router-link>
      </div>

      <form @submit.prevent="register" v-if="!success">
        <div class="form-group">
          <label class="form-label">Student / Staff ID</label>
          <input v-model="form.userID" type="number" class="form-control" placeholder="e.g. 620152345" required />
        </div>
        <div class="form-group">
          <label class="form-label">Full Name <span class="hint">(first and last)</span></label>
          <input v-model="form.name" type="text" class="form-control" placeholder="e.g. Lamar Shaw" required />
        </div>
        <div class="form-group">
          <label class="form-label">Role</label>
          <select v-model="form.role" class="form-control" required>
            <option value="student">Student</option>
            <option value="lecturer">Lecturer</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Password</label>
          <input v-model="form.password" type="password" class="form-control" placeholder="Min. 8 characters" required minlength="8" />
        </div>
        <div class="form-group">
          <label class="form-label">Confirm Password</label>
          <input v-model="form.confirm" type="password" class="form-control" placeholder="Repeat your password" required />
        </div>

        <button type="submit" class="btn btn-primary w-full" :disabled="loading">
          {{ loading ? 'Creating account…' : 'Create account' }}
        </button>
      </form>

      <div class="auth-footer">
        Already have an account? <router-link to="/login">Sign in</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { authService } from '../services/api.js'

const form = ref({ userID: '', name: '', role: 'student', password: '', confirm: '' })
const error = ref('')
const success = ref(false)
const loading = ref(false)

const register = async () => {
  error.value = ''

  if (form.value.password !== form.value.confirm) {
    error.value = 'Passwords do not match.'
    return
  }

  const parts = form.value.name.trim().split(/\s+/)
  if (parts.length < 2) {
    error.value = 'Please enter both your first and last name.'
    return
  }

  loading.value = true
  try {
    await authService.register({
      userID: Number(form.value.userID),
      Name: form.value.name.trim(),
      role: form.value.role,
      password: form.value.password,
    })
    success.value = true
  } catch (e) {
    error.value =
      e.response?.data?.error ||
      e.response?.data?.message ||
      'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; background: var(--uwi-dark); overflow: hidden; }
.auth-bg { position: absolute; inset: 0; overflow: hidden; background: radial-gradient(ellipse at 70% 50%, rgba(0,107,63,.3) 0%, transparent 60%), radial-gradient(ellipse at 20% 80%, rgba(245,168,0,.15) 0%, transparent 50%); }
.hex-pattern { position: absolute; inset: 0; opacity: .06; background-image: url("data:image/svg+xml,%3Csvg width='56' height='100' viewBox='0 0 56 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M28 66L0 50V16L28 0l28 16v34z' fill='none' stroke='%23fff' stroke-width='1'/%3E%3C/svg%3E"); background-size: 56px 100px; }
.auth-card { background: white; border-radius: 20px; padding: 40px; width: 100%; max-width: 440px; position: relative; z-index: 1; box-shadow: 0 24px 80px rgba(0,0,0,.4); }
.auth-logo { display: flex; align-items: center; gap: 12px; margin-bottom: 28px; }
.logo-badge { background: var(--uwi-green); color: white; font-family: 'Fraunces', serif; font-size: 14px; font-weight: 700; width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.auth-title { font-size: 13px; font-weight: 700; color: var(--uwi-dark); }
.auth-sub { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; }
.form-heading { font-size: 22px; margin-bottom: 4px; }
.form-desc { color: var(--text-muted); font-size: 14px; margin-bottom: 20px; }
.hint { font-size: 11px; color: var(--text-muted); font-weight: 400; text-transform: none; letter-spacing: 0; }
.auth-footer { text-align: center; margin-top: 16px; font-size: 14px; color: var(--text-muted); }
.auth-footer a { color: var(--primary); font-weight: 500; }
</style>
