<template>
  <div id="vle-app">
    <template v-if="isAuthenticated">
      <NavBar />
      <SideBar />
    </template>
    <div :class="isAuthenticated ? 'page-content' : ''">
      <router-view v-slot="{ Component, route }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import NavBar from './components/NavBar.vue'
import SideBar from './components/SideBar.vue'

const isAuthenticated = computed(() => !!localStorage.getItem('token'))
</script>
