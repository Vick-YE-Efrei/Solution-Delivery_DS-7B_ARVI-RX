import { reactive } from 'vue'
import axios from 'axios'

export const auth = reactive({
  user:  JSON.parse(localStorage.getItem('arvi_user')  || 'null'),
  token: localStorage.getItem('arvi_token') || null,

  login(userData, token) {
    this.user  = userData
    this.token = token
    localStorage.setItem('arvi_user',  JSON.stringify(userData))
    localStorage.setItem('arvi_token', token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  },

  logout() {
    this.user  = null
    this.token = null
    localStorage.removeItem('arvi_user')
    localStorage.removeItem('arvi_token')
    delete axios.defaults.headers.common['Authorization']
  },

  restore() {
    if (this.token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
    }
  },

  get isLoggedIn() { return !!this.user && !!this.token },
  get isAdmin()    { return this.user?.role === 'admin' }
})

// Restaure le token au démarrage
auth.restore()
