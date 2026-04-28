<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAlerts } from './api.js'

const router = useRouter()
const alertCount = ref(0)

function goHome() {
  router.push('/')
}

async function loadAlerts() {
  try {
    const data = await getAlerts()
    alertCount.value = data.total_count
  } catch {
    // Silently ignore — alerts are non-critical
  }
}

// Check alerts on load and every 60 seconds
onMounted(() => {
  loadAlerts()
  setInterval(loadAlerts, 60000)
})
</script>

<template>
  <div class="app">
    <header class="app-header">
      <div class="header-content">
        <div class="header-brand" @click="goHome">
          <span class="header-logo">AI ERP</span>
          <span class="header-divider">|</span>
          <span class="header-module">Invoice Pipeline</span>
        </div>
        <nav class="header-nav">
          <router-link to="/" class="nav-link">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            Upload
          </router-link>
          <router-link to="/search" class="nav-link">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            Search
          </router-link>
          <router-link to="/matches" class="nav-link">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="16 3 21 3 21 8" />
              <line x1="4" y1="20" x2="21" y2="3" />
              <polyline points="21 16 21 21 16 21" />
              <line x1="15" y1="15" x2="21" y2="21" />
              <line x1="4" y1="4" x2="9" y2="9" />
            </svg>
            Match
          </router-link>
          <router-link to="/reports" class="nav-link">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="20" x2="18" y2="10" />
              <line x1="12" y1="20" x2="12" y2="4" />
              <line x1="6" y1="20" x2="6" y2="14" />
            </svg>
            Reports
          </router-link>
          <router-link to="/alerts" class="nav-link nav-link-alert">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
            Alerts
            <span v-if="alertCount > 0" class="alert-badge">{{ alertCount }}</span>
          </router-link>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: #ffffff;
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.header-logo {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
  letter-spacing: -0.5px;
}

.header-divider {
  color: var(--border-color);
  font-weight: 300;
}

.header-module {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary);
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.15s ease;
  position: relative;
}

.nav-link:hover {
  color: var(--primary);
  background: var(--primary-light);
}

.nav-link.router-link-exact-active {
  color: var(--primary);
  background: var(--primary-light);
}

.alert-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  background: var(--danger);
  border-radius: 100px;
  line-height: 1;
}

.app-main {
  flex: 1;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
</style>
