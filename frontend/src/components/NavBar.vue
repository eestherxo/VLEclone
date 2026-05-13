<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <div class="logo-wrap">
        <div class="logo-icon">VLE</div>
        <div class="logo-text">
          <span class="uni-name">University of the West Indies</span>
          <span class="vle-label">Virtual Learning Environment</span>
        </div>
      </div>
    </div>

    <div class="navbar-links">
      <router-link to="/dashboard" class="nav-link">Home</router-link>
      <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
      <router-link to="/dashboard" class="nav-link active">My courses</router-link>
      <div class="nav-dropdown">
        <button class="nav-link dropdown-btn">Other ≡ ▾</button>
      </div>
    </div>

    <div class="navbar-right">
      <button class="icon-btn" title="Notifications">
        <span class="notif-icon">🔔</span>
        <span v-if="notifCount > 0" class="notif-badge">{{ notifCount }}</span>
      </button>
      <button class="icon-btn" title="Messages">💬</button>

      <div class="user-menu" @click="toggleMenu" ref="menuRef">
        <div class="avatar">{{ initials }}</div>
        <span class="username-label">{{ user?.username || 'User' }}</span>
        <div v-if="menuOpen" class="dropdown-menu">
          <router-link to="/dashboard" class="dropdown-item">Dashboard</router-link>
          <router-link v-if="user?.role === 'admin'" to="/admin" class="dropdown-item">Admin Panel</router-link>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item danger" @click="logout">Sign out</button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const menuOpen = ref(false)
const menuRef = ref(null)
const notifCount = ref(3)
const user = computed(() => JSON.parse(localStorage.getItem('user') || 'null'))
const initials = computed(() => {
  const u = user.value?.username || ''
  return u.slice(0, 2).toUpperCase() || 'LS'
})

const toggleMenu = () => menuOpen.value = !menuOpen.value

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

const handleClick = (e) => {
  if (menuRef.value && !menuRef.value.contains(e.target)) menuOpen.value = false
}
onMounted(() => document.addEventListener('click', handleClick))
onUnmounted(() => document.removeEventListener('click', handleClick))
</script>

<style scoped>
.navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  height: var(--nav-height); background: var(--uwi-dark);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 20px; box-shadow: 0 2px 12px rgba(0,0,0,.3);
  border-bottom: 3px solid var(--uwi-green);
}

.logo-wrap { display: flex; align-items: center; gap: 10px; }
.logo-icon {
  background: var(--uwi-green); color: white;
  font-family: 'Fraunces', serif; font-size: 13px; font-weight: 700;
  width: 42px; height: 42px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  letter-spacing: .5px;
}
.logo-text { display: flex; flex-direction: column; }
.uni-name { color: white; font-size: 12px; font-weight: 600; line-height: 1.2; }
.vle-label { color: rgba(255,255,255,.5); font-size: 10px; text-transform: uppercase; letter-spacing: .6px; }

.navbar-links { display: flex; gap: 4px; }
.nav-link {
  color: rgba(255,255,255,.75); padding: 6px 14px;
  border-radius: 6px; font-size: 14px; font-weight: 500;
  transition: all .15s; text-decoration: none; border: none;
  background: transparent; cursor: pointer; font-family: 'DM Sans', sans-serif;
}
.nav-link:hover, .nav-link.router-link-active { color: white; background: rgba(255,255,255,.1); text-decoration: none; }
.nav-link.active { color: var(--uwi-gold); border-bottom: 2px solid var(--uwi-gold); border-radius: 0; }

.navbar-right { display: flex; align-items: center; gap: 6px; }
.icon-btn {
  position: relative; background: transparent; border: none; cursor: pointer;
  color: rgba(255,255,255,.75); font-size: 18px;
  width: 38px; height: 38px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s;
}
.icon-btn:hover { background: rgba(255,255,255,.1); }
.notif-badge {
  position: absolute; top: 4px; right: 4px;
  background: var(--uwi-red); color: white; font-size: 9px;
  width: 16px; height: 16px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-weight: 700;
}

.user-menu { position: relative; display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 8px; border-radius: 8px; transition: background .15s; }
.user-menu:hover { background: rgba(255,255,255,.1); }
.avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: var(--uwi-gold); color: #1a1a1a;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 13px;
}
.username-label { color: rgba(255,255,255,.85); font-size: 13px; font-weight: 500; }

.dropdown-menu {
  position: absolute; top: calc(100% + 8px); right: 0;
  background: white; border-radius: var(--radius); box-shadow: var(--shadow-lg);
  min-width: 180px; overflow: hidden; z-index: 200;
  border: 1px solid var(--border); animation: dropIn .15s ease;
}
@keyframes dropIn { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: none; } }
.dropdown-item {
  display: block; width: 100%; text-align: left;
  padding: 10px 16px; font-size: 14px; color: var(--text);
  border: none; background: transparent; cursor: pointer;
  transition: background .12s; text-decoration: none;
}
.dropdown-item:hover { background: var(--surface-2); text-decoration: none; }
.dropdown-item.danger { color: var(--danger); }
.dropdown-divider { height: 1px; background: var(--border); }
</style>
