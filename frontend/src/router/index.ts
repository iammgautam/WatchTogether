import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LandingPage from '../views/LandingPage.vue'
import Dashboard from '../views/Dashboard.vue'
import RoomView from '../views/RoomView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: LandingPage
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard,
      meta: { requiresAuth: true }
    },
    {
      path: '/room/:id',
      name: 'Room',
      component: RoomView,
      meta: { requiresAuth: true }
    }
  ]
})

// Global Navigation Guard
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Attempting to access protected route without auth
    next({ name: 'home' })
  } else if (to.name === 'home' && authStore.isAuthenticated) {
    // Already authenticated, shouldn't be on landing page
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
