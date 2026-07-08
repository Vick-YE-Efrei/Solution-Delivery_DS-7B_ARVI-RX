<template>
  <div class="auth-layout">

    <!-- Colonne gauche : branding -->
    <div class="auth-left">
      <div class="auth-left-inner">
        <div class="brand">
          <div class="brand-dot"></div>
          <span class="brand-name">{{ t('login.brand') }}</span>
        </div>
        <div class="auth-pitch">
          <h1 v-html="t('login.tagline').replace('\n', '<br />')"></h1>
          <p>{{ t('login.description') }}</p>
        </div>
        <div class="auth-meta">EFREI Paris · Filière Data &amp; IA · 2025-2026</div>
      </div>
    </div>

    <!-- Colonne droite : formulaire -->
    <div class="auth-right">
      <div class="auth-card">

        <!-- Lang toggle -->
        <button @click="toggleLocale" style="position:absolute;top:16px;right:16px;display:flex;align-items:center;gap:6px;font-size:11px;font-weight:600;color:#64748b;background:transparent;border:1px solid #e2e8f0;border-radius:8px;padding:5px 10px;cursor:pointer;">
          <span class="material-symbols-outlined" style="font-size:14px;">translate</span>
          {{ locale === 'fr' ? 'English' : 'Français' }}
        </button>

        <!-- Toggle login / register -->
        <div class="auth-tabs">
          <button class="auth-tab" :class="{ active: tab === 'login' }" @click="tab = 'login'">
            {{ t('login.tab_login') }}
          </button>
          <button class="auth-tab" :class="{ active: tab === 'register' }" @click="tab = 'register'">
            {{ t('login.tab_register') }}
          </button>
        </div>

        <!-- LOGIN -->
        <form v-if="tab === 'login'" class="auth-form" @submit.prevent="handleLogin">
          <div class="form-group">
            <label class="form-label">{{ t('login.email') }}</label>
            <input
              v-model="loginForm.email"
              type="email"
              class="form-input"
              :placeholder="t('login.email_ph')"
              required
              autocomplete="email"
            />
          </div>
          <div class="form-group">
            <label class="form-label">{{ t('login.password') }}</label>
            <div class="input-wrap">
              <input
                v-model="loginForm.password"
                :type="showPwd ? 'text' : 'password'"
                class="form-input"
                placeholder="••••••••"
                required
                autocomplete="current-password"
              />
              <button type="button" class="eye-btn" @click="showPwd = !showPwd">
                <svg v-if="!showPwd" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z" stroke="currentColor" stroke-width="1.4"/>
                  <circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.4"/>
                </svg>
                <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M2 2l12 12M6.5 6.6A2 2 0 0010.4 10M4.2 4.3C2.7 5.3 1.5 7 1.5 7S4 12 8 12c1.2 0 2.3-.4 3.2-1M6 3.2C6.6 3.1 7.3 3 8 3c4 0 6.5 4 6.5 4s-.5 1-1.5 2.1" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </div>

          <div v-if="error" class="form-error">{{ error }}</div>

          <button type="submit" class="btn-submit" :disabled="isLoading">
            <span v-if="isLoading" class="btn-spinner"></span>
            <span v-else>{{ t('login.btn_login') }}</span>
          </button>
        </form>

        <!-- REGISTER -->
        <form v-if="tab === 'register'" class="auth-form" @submit.prevent="handleRegister">
          <div class="form-group">
            <label class="form-label">{{ t('login.fullname') }}</label>
            <input
              v-model="registerForm.name"
              type="text"
              class="form-input"
              :placeholder="t('login.fullname_ph')"
              required
              autocomplete="name"
            />
          </div>
          <div class="form-group">
            <label class="form-label">{{ t('login.email') }}</label>
            <input
              v-model="registerForm.email"
              type="email"
              class="form-input"
              :placeholder="t('login.email_ph')"
              required
              autocomplete="email"
            />
          </div>
          <div class="form-group">
            <label class="form-label">{{ t('login.password') }}</label>
            <div class="input-wrap">
              <input
                v-model="registerForm.password"
                :type="showPwd ? 'text' : 'password'"
                class="form-input"
                placeholder="••••••••"
                required
                autocomplete="new-password"
              />
              <button type="button" class="eye-btn" @click="showPwd = !showPwd">
                <svg v-if="!showPwd" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z" stroke="currentColor" stroke-width="1.4"/>
                  <circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.4"/>
                </svg>
                <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M2 2l12 12M6.5 6.6A2 2 0 0010.4 10M4.2 4.3C2.7 5.3 1.5 7 1.5 7S4 12 12c1.2 0 2.3-.4 3.2-1M6 3.2C6.6 3.1 7.3 3 8 3c4 0 6.5 4 6.5 4s-.5 1-1.5 2.1" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">{{ t('login.confirm_pwd') }}</label>
            <input
              v-model="registerForm.confirm"
              type="password"
              class="form-input"
              placeholder="••••••••"
              required
              autocomplete="new-password"
            />
          </div>

          <div v-if="error" class="form-error">{{ error }}</div>
          <div v-if="success" class="form-success">{{ success }}</div>

          <button type="submit" class="btn-submit" :disabled="isLoading">
            <span v-if="isLoading" class="btn-spinner"></span>
            <span v-else>{{ t('login.btn_register') }}</span>
          </button>
        </form>

        <p class="auth-note">
          {{ t('login.note') }}
        </p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { auth } from '../store/auth.js'
import { t, locale, toggleLocale } from '../store/locale.js'

const router   = useRouter()
const tab      = ref('login')
const showPwd  = ref(false)
const isLoading = ref(false)
const error    = ref('')
const success  = ref('')

const loginForm = ref({ email: '', password: '' })
const registerForm = ref({ name: '', email: '', password: '', confirm: '' })

async function handleLogin() {
  error.value = ''
  isLoading.value = true
  try {
    const { data } = await axios.post('/api/auth/login', loginForm.value)
    auth.login(data.user, data.token)
    router.push(data.user.role === 'admin' ? '/admin' : '/')
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Identifiants incorrects.'
  } finally {
    isLoading.value = false
  }
}

async function handleRegister() {
  error.value = ''
  success.value = ''
  if (registerForm.value.password !== registerForm.value.confirm) {
    error.value = 'Les mots de passe ne correspondent pas.'
    return
  }
  isLoading.value = true
  try {
    await axios.post('/api/auth/register', {
      name:     registerForm.value.name,
      email:    registerForm.value.email,
      password: registerForm.value.password
    })
    success.value = 'Compte créé. Vous pouvez maintenant vous connecter.'
    tab.value = 'login'
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Erreur lors de la création du compte.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.auth-layout {
  display: flex;
  min-height: 100vh;
  font-family: system-ui, sans-serif;
}

/* ── Gauche ── */
.auth-left {
  width: 45%;
  background: #111111;
  color: #f9fafb;
  display: flex;
  align-items: stretch;
  position: relative;
  overflow: hidden;
}
.auth-left::before {
  content: '';
  position: absolute;
  top: -120px; left: -120px;
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(124,58,237,0.18) 0%, transparent 70%);
  pointer-events: none;
}
.auth-left::after {
  content: '';
  position: absolute;
  bottom: -80px; right: -80px;
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(91,33,182,0.12) 0%, transparent 70%);
  pointer-events: none;
}
.auth-left-inner {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 40px 48px;
  width: 100%;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}
.brand-dot {
  width: 9px; height: 9px;
  border-radius: 50%;
  background: #7c3aed;
  box-shadow: 0 0 10px rgba(124,58,237,0.7);
  flex-shrink: 0;
}
.brand-name {
  font-size: 14px;
  font-weight: 600;
  color: #e5e7eb;
  letter-spacing: -0.01em;
}
.auth-pitch {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px 0;
}
.auth-pitch h1 {
  font-family: 'Georgia', serif;
  font-size: 34px;
  font-weight: 700;
  color: #f9fafb;
  line-height: 1.25;
  letter-spacing: -0.02em;
  margin-bottom: 20px;
}
.auth-pitch p {
  font-size: 15px;
  color: #9ca3af;
  line-height: 1.8;
  max-width: 340px;
}
.auth-meta {
  font-size: 12px;
  color: #4b5563;
}

/* ── Droite ── */
.auth-right {
  flex: 1;
  background: #f4f3ef;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
}
.auth-card {
  position: relative;
  background: #ffffff;
  border: 1px solid #e5e2db;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.07);
  padding: 36px 40px;
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── Tabs ── */
.auth-tabs {
  display: flex;
  background: #f4f3ef;
  border-radius: 8px;
  padding: 4px;
  gap: 2px;
}
.auth-tab {
  flex: 1;
  padding: 9px 12px;
  border: none;
  border-radius: 6px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  background: transparent;
  color: #6b7280;
  transition: all 0.15s;
}
.auth-tab.active {
  background: #ffffff;
  color: #111111;
  box-shadow: 0 1px 4px rgba(0,0,0,0.10);
}

/* ── Formulaire ── */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-label {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #6b7280;
}
.form-input {
  width: 100%;
  padding: 11px 14px;
  border: 1.5px solid #e5e2db;
  border-radius: 8px;
  font-size: 14px;
  color: #111111;
  background: #fafaf9;
  font-family: system-ui, sans-serif;
  transition: border-color 0.15s, box-shadow 0.15s;
  outline: none;
}
.form-input:focus {
  border-color: #5b21b6;
  box-shadow: 0 0 0 3px rgba(91,33,182,0.10);
  background: #ffffff;
}
.form-input::placeholder { color: #d1d5db; }

.input-wrap { position: relative; }
.input-wrap .form-input { padding-right: 40px; }
.eye-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #9ca3af;
  display: flex;
  align-items: center;
  padding: 0;
  transition: color 0.15s;
}
.eye-btn:hover { color: #5b21b6; }

.form-error {
  font-size: 13px;
  color: #991b1b;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 10px 12px;
  line-height: 1.5;
}
.form-success {
  font-size: 13px;
  color: #065f46;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  border-radius: 6px;
  padding: 10px 12px;
}

.btn-submit {
  width: 100%;
  padding: 13px;
  background: #111111;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.15s, transform 0.1s, box-shadow 0.15s;
  margin-top: 4px;
}
.btn-submit:hover:not(:disabled) {
  background: #1f1f1f;
  box-shadow: 0 4px 14px rgba(0,0,0,0.2);
  transform: translateY(-1px);
}
.btn-submit:disabled {
  background: #e5e2db;
  color: #9ca3af;
  cursor: not-allowed;
}
.btn-spinner {
  width: 15px; height: 15px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.auth-note {
  font-size: 11.5px;
  color: #9ca3af;
  text-align: center;
  line-height: 1.5;
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 700px) {
  .auth-layout { flex-direction: column; }
  .auth-left { width: 100%; min-height: 220px; }
  .auth-left-inner { padding: 28px 24px; }
  .auth-pitch h1 { font-size: 24px; }
  .auth-pitch p { display: none; }
  .auth-card { padding: 28px 20px; }
}
</style>
