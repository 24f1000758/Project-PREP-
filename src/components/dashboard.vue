<template>
  <div class="dashboard" :class="{ 'sidebar-open': isSidebarOpen, 'sidebar-collapsed': !isSidebarOpen }">
    <header class="mobile-topbar" v-if="isMobile">
      <button class="hamburger-btn" @click="toggleSidebar" :aria-expanded="isSidebarOpen" aria-label="Toggle menu">
        <span class="bar" :class="{ open: isSidebarOpen }"></span>
        <span class="bar" :class="{ open: isSidebarOpen }"></span>
        <span class="bar" :class="{ open: isSidebarOpen }"></span>
      </button>
      <div class="logo">Navbar Gallery</div>
    </header>

    <div v-if="isSidebarOpen && isMobile" class="overlay" @click="toggleSidebar"></div>

    <div class="sidebar-container" :class="{ 'open': isSidebarOpen && isMobile }">
      <aside
        :class="['sidebar', { open: isSidebarOpen, collapsed: !isSidebarOpen && !isMobile }]"
      >
        <div class="logo-container">
          <span class="logo" v-show="isSidebarOpen">Navbar Gallery</span>
          <div v-if="!isMobile" class="desktop-toggle">
            <PanelLeftOpen 
              v-if="isSidebarOpen" 
              class="toggle-icon" 
              @click="toggleSidebar" 
              aria-label="Collapse sidebar" 
            />
            <PanelRightOpen 
              v-else 
              class="toggle-icon" 
              @click="toggleSidebar" 
              aria-label="Expand sidebar" 
            />
          </div>
        </div>

        <nav class="nav-links" role="menu">
          <router-link to="/dashboard" class="nav-link" active-class="active" exact-active-class="active" @click="handleNavClick">
            <span class="nav-icon"><House/></span>
            <span class="nav-label">Home</span>
          </router-link>
          <router-link to="/dashboard/ai" class="nav-link" active-class="active" exact-active-class="active" @click="handleNavClick">
            <span class="nav-icon"><BotMessageSquare/></span>
            <span class="nav-label">Prep Ai</span>
          </router-link>
          <router-link to="/dashboard/flashai" class="nav-link" active-class="active" exact-active-class="active" @click="handleNavClick">
            <span class="nav-icon"><SquareAsterisk/></span>
            <span class="nav-label">FLashCard</span>
          </router-link>
          <router-link to="/dashboard/current_affair" class="nav-link" active-class="active" exact-active-class="active" @click="handleNavClick">
            <span class="nav-icon"><Newspaper/></span>
            <span class="nav-label">Current Affair</span>
          </router-link>
          <router-link to="/dashboard/profile" class="nav-link" active-class="active" exact-active-class="active" @click="handleNavClick">
            <span class="nav-icon"><UserRoundPen/></span>
            <span class="nav-label">Profiler</span>
          </router-link>
          <a href="#" class="nav-link" role="menuitem" tabindex="0" @click.prevent="logout">
            <span class="nav-icon"><LogOut/></span>
            <span class="nav-label">Logout</span>
          </a>
        </nav>
      </aside>
    </div>

    <main class="content-area">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { House, BotMessageSquare, LogOut, UserRoundPen, Newspaper, SquareAsterisk, PanelLeftOpen, PanelRightOpen } from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();

const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024);
const MOBILE_BREAKPOINT = 767; // A common breakpoint for mobile
const isMobile = computed(() => windowWidth.value <= MOBILE_BREAKPOINT);

// Initialize based on the current screen size. On desktop, it's open. On mobile, it's closed.
const isSidebarOpen = ref(!isMobile.value);

function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value;
}

function updateWidth() {
  if (typeof window !== 'undefined') {
    windowWidth.value = window.innerWidth;
  }
}

// Watch for route changes to auto-collapse sidebar on mobile
watch(route, () => {
  if (isMobile.value && isSidebarOpen.value) {
    isSidebarOpen.value = false;
  }
});

// Watch for changes in isMobile. When it changes, we update the sidebar state
watch(isMobile, (newIsMobile) => {
  if (newIsMobile) {
    isSidebarOpen.value = false; // Collapse on mobile
  } else {
    isSidebarOpen.value = true; // Expand on desktop
  }
});

function logout() {
  if (typeof localStorage !== 'undefined') {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  }
  router.push({ name: 'Home' });
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', updateWidth);

    const token = route.query.token;
    if (token) {
      localStorage.setItem('auth_token', token);
      router.replace({ path: '/dashboard', query: {} });
    } else {
      const existingToken = localStorage.getItem('auth_token');
      if (!existingToken) {
        router.push({ name: 'Login' });
      }
    }
  }
});

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', updateWidth);
  }
});
</script>

<style scoped>
html {
  overflow-x: hidden;
}

body {
  overflow-x: hidden;
  font-display: swap;
}

.dashboard {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  background: #0d0d0d;
  color: #fff;
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  overflow: hidden;
  padding: 20px;
  gap: 20px;
  box-sizing: border-box;
}

.sidebar-container {
  width: 250px;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.dashboard.sidebar-collapsed .sidebar-container {
  width: 65px;
}

.content-area {
  background: #181818;
  min-height: 100%;
  padding: 25px;
  overflow-y: auto;
  overflow-x: hidden;
  border-radius: 10px;
  box-sizing: border-box;
  flex: 1;
  min-width: 0;
  position: relative;
}

.mobile-topbar {
  position: fixed;
  top: 0;
  left: 0;
  height: 50px;
  width: 100%;
  background: #111;
  display: flex;
  align-items: center;
  padding: 0 15px;
  z-index: 1200;
  box-shadow: 0 2px 5px rgba(0,0,0,0.7);
}

.desktop-toggle {
  margin-left: auto;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.toggle-icon {
  width: 26px;
  height: 26px;
  color: #fff;
  transition: transform 0.2s ease, color 0.2s ease;
}

.toggle-icon:hover {
  color: #ff5722;
  transform: scale(1.1);
}

.logo {
  color: #fff;
  font-weight: 700;
  font-size: 1.25rem;
  margin-left: 15px;
}

.hamburger-btn {
  position: fixed;
  z-index: 1200;
  top: 15px;
  left: 15px;
  width: 30px;
  height: 22px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.hamburger-btn .bar {
  height: 4px;
  width: 100%;
  background-color: #f5f5f5;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.hamburger-btn .bar.open:nth-child(1) {
  transform: translateY(9px) rotate(45deg);
}

.hamburger-btn .bar.open:nth-child(2) {
  opacity: 0;
}

.hamburger-btn .bar.open:nth-child(3) {
  transform: translateY(-9px) rotate(-45deg);
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(20, 20, 20, 0.85);
  backdrop-filter: blur(5px);
  z-index: 1100;
  opacity: 1;
  transition: opacity 0.3s ease;
}

.sidebar {
  background: #1a1a1a;
  padding-top: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 3px 0 15px rgba(0, 0, 0, 0.6);
  overflow: hidden;
  z-index: 1150;
  border-radius: 10px;
  height: 100%;
  width: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

.logo-container {
  display: flex;
  align-items: center;
  padding: 0 1.5rem 1.5rem;
}

.nav-links {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 1rem 10px;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.8rem 0.5rem;
  color: #bbb;
  font-weight: 500;
  font-size: 1rem;
  text-decoration: none;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.3s ease, color 0.3s ease;
  border-radius: 6px;
  margin-bottom: 8px;
}

.nav-link:hover,
.nav-link:focus {
  background-color: rgba(255, 255, 255, 0.05);
  color: #fff;
  outline: none;
}

.nav-link.active {
  background-color: rgba(255, 255, 255, 0.1);
  color: #ff5722;
}

.nav-link.active .nav-icon {
  color: #ff5722;
}

.nav-icon {
  font-size: 1.25rem;
  width: 30px;
  text-align: center;
  flex-shrink: 0;
  color: #888;
  margin-right: 15px;
  transition: color 0.3s ease;
}

.nav-label {
  flex: 1;
  opacity: 1;
  transition: opacity 0.2s ease, transform 0.2s ease;
  transition-delay: 0.1s;
  transform: translateX(0);
  min-width: 0;
  overflow: hidden;
}

.sidebar.collapsed .nav-label {
  opacity: 0;
  transform: translateX(-20px);
  width: 0;
  transition-delay: 0s;
}

@media (max-width: 767px) {
  .dashboard {
    position: relative;
    display: flex;
    flex-direction: column;
    padding: 0;
    overflow-y: auto;
    overflow-x: hidden;
    height: 100vh;
  }

  .sidebar-container {
    position: fixed;
    top: 0;
    left: -100%;
    height: 100vh;
    width: 65vw;
    transition: left 0.3s ease;
    z-index: 1150;
  }
  
  .sidebar-container .sidebar {
    border-radius: 0 !important;
    width: 100%;
    height: 100%;
    position: relative;
  }
  
  .sidebar-container.open {
    left: 0;
  }

  .content-area {
    width: 100%;
    margin-left: 0;
    padding: 20px;
    padding-top: 70px;
    border-radius: 0;
    overflow-y: auto;
    overflow-x: hidden;
    flex: 1;
    height: calc(100vh - 50px);
  }
}

* {
  box-sizing: border-box;
}

*:before,
*:after {
  box-sizing: border-box;
}
</style>
