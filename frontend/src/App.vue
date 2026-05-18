<template>
  <div id="vle-app">
    <template v-if="isAuthenticated">
      <NavBar />
      <SideBar :collapsed="sidebarCollapsed" @toggle="sidebarCollapsed = !sidebarCollapsed" />
    </template>
    <div :class="[isAuthenticated ? 'page-content' : '', isAuthenticated && sidebarCollapsed ? 'sidebar-collapsed' : '']">
      <router-view v-slot="{ Component, route }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from './components/NavBar.vue'
import SideBar from './components/SideBar.vue'

const router = useRouter()
const isAuthenticated = ref(!!localStorage.getItem('token'))
const sidebarCollapsed = ref(false)

// re-check auth on every route change
router.afterEach(() => {
  isAuthenticated.value = !!localStorage.getItem('token')
})
</script>