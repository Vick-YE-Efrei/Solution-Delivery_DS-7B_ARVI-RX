import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'
import App from './App.vue'
import HomeView from './views/HomeView.vue'
import LoginView from './views/LoginView.vue'
import AdminDashboardView from './views/AdminDashboardView.vue'
import UserHistoryView from './views/UserHistoryView.vue'
import AboutView from './views/AboutView.vue'
import GuideView from './views/GuideView.vue'
import { auth } from './store/auth.js'
import './assets/global.css'

// Appelle le backend directement — évite tout problème de proxy Vite
axios.defaults.baseURL = 'http://localhost:3000'

// Nettoie les données périmées du localStorage (sans token JWT)
const storedUser  = localStorage.getItem('arvi_user')
const storedToken = localStorage.getItem('arvi_token')
if (storedUser && !storedToken) {
  localStorage.removeItem('arvi_user')
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login',   component: LoginView,           meta: { public: true } },
    { path: '/',        component: HomeView,             meta: { requiresAuth: true } },
    { path: '/history', component: UserHistoryView,      meta: { requiresAuth: true } },
    { path: '/admin',   component: AdminDashboardView,   meta: { requiresAuth: true, requiresAdmin: true } },
    { path: '/about',   component: AboutView,            meta: { requiresAuth: true } },
    { path: '/guide',   component: GuideView,            meta: { requiresAuth: true } }
  ]
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !auth.isLoggedIn) return '/login'
  if (to.meta.requiresAdmin && !auth.isAdmin)   return '/'
  if (to.path === '/login' && auth.isLoggedIn)  return auth.isAdmin ? '/admin' : '/'
})

createApp(App).use(router).mount('#app')
