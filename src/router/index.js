import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Dashboard from '../components/dashboard.vue'
import Profile from '../views/Profile.vue'
import GoogleAuthFinish from '../components/GoogleAuthFinish.vue'  // import your new component
import First from '../views/First.vue'
import Ai from '../views/ai.vue'
import Flashai from '../views/flashai.vue'
import Current_affair from '../views/current_affair.vue'
import Adashboard from '../components/adashboard.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { 
    path: '/dashboard', 
    component: Dashboard, 
    meta: { requiresAuth: true },
    children: [
      {
        path:'',
        name:'First',
        component: First,
      },
      {
        path: 'profile',             
        name: 'Profile',
        component: Profile,
      },
      {
        path: 'ai',             
        name: 'Ai',
        component: Ai,
      },
      {
        path: 'flashai',             
        name: 'Flashai',
        component: Flashai,
      },
      {
        path: 'current_affair',
        name: 'Current_affair',
        component: Current_affair,
      },
      // You can add more child routes here, e.g. settings, other pages
    ]
  },
  { path: '/adashboard', name: 'Adashboard', component: Adashboard},
  { path: '/google-auth-finish', name: 'GoogleAuthFinish', component: GoogleAuthFinish }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard to check for token on protected routes
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token')

  if (to.meta.requiresAuth && !token) {
    next({ name: 'Home', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
