<template>
  <div class="flex min-h-screen">

    <!-- ═══════════════════ SIDEBAR ═══════════════════ -->
    <aside class="flex flex-col h-screen w-64 sticky left-0 top-0 bg-[#0f172a] py-6 z-50">
      <div class="flex flex-col items-center px-4 mb-6">
        <div class="w-16 h-16 rounded-2xl bg-white shadow-lg mb-3 flex items-center justify-center p-2">
          <img :src="raviLogo" alt="RAVI" class="w-full h-full object-contain" />
        </div>
        <h1 class="page-title-font text-xl text-white font-extrabold tracking-tight">RAVI</h1>
        <p class="text-[9px] uppercase tracking-[0.25em] text-slate-500 font-bold mt-0.5">{{ t('common.prototype') }}</p>
        <div class="w-full h-px bg-gradient-to-r from-transparent via-slate-700 to-transparent mt-4"></div>
      </div>

      <nav class="flex-1 px-4 space-y-1">
        <router-link to="/"
          class="text-slate-400 hover:text-white rounded-xl px-4 py-3 flex items-center gap-3.5 hover:bg-white/5 transition-colors">
          <span class="material-symbols-outlined text-xl">radiology</span>
          <span class="font-medium text-sm">{{ t('nav.analysis') }}</span>
        </router-link>
        <router-link to="/history"
          class="rounded-xl px-4 py-3 flex items-center gap-3.5 border border-blue-500/20 bg-blue-600/10 text-blue-400">
          <span class="material-symbols-outlined text-xl" style="font-variation-settings:'FILL' 1">history</span>
          <span class="font-semibold text-sm">{{ t('nav.history') }}</span>
        </router-link>
        <router-link to="/guide"
          class="text-slate-400 hover:text-white rounded-xl px-4 py-3 flex items-center gap-3.5 hover:bg-white/5 transition-colors">
          <span class="material-symbols-outlined text-xl">menu_book</span>
          <span class="font-medium text-sm">{{ t('nav.guide') }}</span>
        </router-link>
        <router-link to="/about"
          class="text-slate-400 hover:text-white rounded-xl px-4 py-3 flex items-center gap-3.5 hover:bg-white/5 transition-colors">
          <span class="material-symbols-outlined text-xl">info</span>
          <span class="font-medium text-sm">{{ t('nav.about') }}</span>
        </router-link>
      </nav>

      <div class="px-6 py-4 mt-auto border-t border-slate-800">
        <div class="flex items-center gap-3.5 p-3 rounded-2xl bg-slate-900/50 border border-slate-800 mb-3">
          <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
            {{ userInitials }}
          </div>
          <div class="overflow-hidden">
            <p class="font-bold text-xs text-white truncate">{{ auth.user?.name ?? 'Projet EFREI' }}</p>
            <p class="text-[9px] text-slate-500 font-semibold uppercase tracking-wider">{{ auth.isAdmin ? t('common.account_admin') : t('common.account_user') }}</p>
          </div>
        </div>
        <router-link v-if="auth.isAdmin" to="/admin"
          class="w-full flex items-center justify-center gap-2 mb-2 px-3 py-2 rounded-xl text-xs font-semibold text-violet-400 bg-violet-500/10 hover:bg-violet-500/20 border border-violet-500/20 hover:border-violet-500/40 transition-all no-underline">
          <span class="material-symbols-outlined text-base">admin_panel_settings</span>
          {{ t('nav.admin_interface') }}
        </router-link>
        <button @click="toggleLocale"
          class="w-full flex items-center justify-center gap-2 mb-1 px-3 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-white/5 transition-all">
          <span class="material-symbols-outlined text-base">translate</span>
          {{ locale === 'fr' ? 'English' : 'Français' }}
        </button>
        <button @click="logout"
          class="w-full flex items-center justify-center gap-2 mt-1 px-3 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all">
          <span class="material-symbols-outlined text-base">logout</span>
          {{ t('common.logout') }}
        </button>
      </div>
    </aside>

    <!-- ═══════════════════ MAIN ═══════════════════ -->
    <main class="flex-1 flex flex-col bg-surface overflow-auto">

      <!-- Top Bar -->
      <header class="flex justify-between items-center px-8 h-16 glass-header sticky top-0 z-40 border-b border-outline-variant">
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-on-surface-variant">history</span>
          <h2 class="page-title-font text-lg font-extrabold text-on-surface">{{ t('history.title') }}</h2>
        </div>
        <router-link to="/"
          class="flex items-center gap-2 btn-primary-gradient text-white text-xs font-bold px-4 py-2 rounded-full hover:scale-[1.02] transition-all no-underline">
          <span class="material-symbols-outlined text-sm">add</span>
          {{ t('history.new_analysis') }}
        </router-link>
      </header>

      <!-- Page Container -->
      <div class="px-8 py-6 space-y-6 flex-1">

        <!-- Résumé rapide -->
        <div class="grid grid-cols-4 gap-4">
          <div class="bg-white rounded-2xl border border-outline-variant premium-shadow p-5">
            <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">{{ t('history.total') }}</p>
            <p class="page-title-font text-3xl font-extrabold text-on-surface">{{ analyses.length }}</p>
          </div>
          <div class="bg-white rounded-2xl border border-outline-variant premium-shadow p-5">
            <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">{{ t('history.normal') }}</p>
            <p class="page-title-font text-3xl font-extrabold text-emerald-700">{{ countByClass('normal') }}</p>
          </div>
          <div class="bg-white rounded-2xl border border-outline-variant premium-shadow p-5">
            <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">{{ t('history.opacity') }}</p>
            <p class="page-title-font text-3xl font-extrabold text-orange-700">{{ countByClass('suspected_opacity') }}</p>
          </div>
          <div class="bg-white rounded-2xl border border-outline-variant premium-shadow p-5">
            <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">{{ t('history.uncertain') }}</p>
            <p class="page-title-font text-3xl font-extrabold text-amber-700">{{ countByClass('uncertain') }}</p>
          </div>
        </div>

        <!-- Filtres -->
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-sm text-on-surface-variant">filter_list</span>
          <select v-model="filter" class="filter-select">
            <option value="">{{ t('history.all_classes') }}</option>
            <option value="normal">{{ t('class.normal') }}</option>
            <option value="suspected_opacity">{{ t('class.suspected_opacity') }}</option>
            <option value="uncertain">{{ t('class.uncertain') }}</option>
          </select>
          <select v-model="modeFilter" class="filter-select">
            <option value="">{{ t('history.all_modes') }}</option>
            <option value="baseline">Baseline</option>
            <option value="improved">{{ t('home.mode_improved') }}</option>
          </select>
          <span class="text-xs text-on-surface-variant ml-auto">
            {{ filteredAnalyses.length }} {{ filteredAnalyses.length !== 1 ? t('history.results') : t('history.result') }}
          </span>
        </div>

        <!-- Liste des analyses -->
        <div class="bg-white rounded-2xl border border-outline-variant premium-shadow overflow-hidden">

          <div v-if="isLoading"
            class="flex flex-col items-center justify-center py-16 text-on-surface-variant gap-3">
            <span class="material-symbols-outlined text-4xl animate-spin">refresh</span>
            <p class="text-sm">Chargement de l'historique...</p>
          </div>
          <div v-else-if="filteredAnalyses.length === 0"
            class="flex flex-col items-center justify-center py-16 text-on-surface-variant gap-3">
            <span class="material-symbols-outlined text-4xl">search_off</span>
            <p class="text-sm">{{ analyses.length === 0 ? 'Aucune analyse effectuée pour le moment.' : 'Aucune analyse ne correspond aux filtres.' }}</p>
          </div>

          <div v-for="(a, idx) in filteredAnalyses" :key="a.id">

            <!-- Ligne -->
            <div
              class="flex items-center justify-between px-6 py-4 cursor-pointer hover:bg-slate-50 transition-colors border-b border-outline-variant last:border-b-0"
              @click="selected = selected?.id === a.id ? null : a"
            >
              <div class="flex items-center gap-4 flex-1 min-w-0">
                <!-- Numéro -->
                <span class="text-xs font-bold text-slate-300 w-6 flex-shrink-0">#{{ a.id }}</span>

                <!-- Icône -->
                <div class="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center flex-shrink-0">
                  <span class="material-symbols-outlined text-slate-400 text-lg">radiology</span>
                </div>

                <!-- Résultat + date -->
                <div class="flex flex-col gap-0.5 min-w-0">
                  <span :class="['text-sm font-bold', predClass(a.prediction)]">
                    {{ classLabel(a.prediction) }}
                  </span>
                  <span class="text-xs text-on-surface-variant">{{ a.date }}</span>
                </div>
              </div>

              <div class="flex items-center gap-5 flex-shrink-0">
                <!-- Mode -->
                <span class="text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-full"
                  :class="a.mode === 'improved'
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'bg-slate-100 text-slate-500'">
                  {{ a.mode }}
                </span>

                <!-- Barre de confiance -->
                <div class="flex items-center gap-2">
                  <div class="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div class="h-full rounded-full confidence-bar"
                      :style="{ width: (a.confidence * 100) + '%', background: confColor(a.confidence) }">
                    </div>
                  </div>
                  <span class="text-xs font-semibold text-on-surface-variant w-8">
                    {{ (a.confidence * 100).toFixed(0) }}%
                  </span>
                </div>

                <!-- Chevron -->
                <span class="material-symbols-outlined text-slate-400 text-xl transition-transform duration-200"
                  :style="selected?.id === a.id ? 'transform:rotate(180deg)' : ''">
                  expand_more
                </span>
              </div>
            </div>

            <!-- Détail expandable -->
            <transition name="slide">
              <div v-if="selected?.id === a.id"
                class="px-6 py-5 bg-slate-50 border-b border-outline-variant last:border-b-0">
                <div class="grid grid-cols-2 gap-4">

                  <div class="flex flex-col gap-1">
                    <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">{{ t('history.lim_quality') }}</p>
                    <p class="text-sm text-on-surface leading-relaxed">{{ a.imageQuality }}</p>
                  </div>

                  <div class="flex flex-col gap-1">
                    <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">{{ t('history.lim_just') }}</p>
                    <p class="text-sm text-on-surface leading-relaxed whitespace-pre-wrap">{{ tBackend(a.justification) }}</p>
                  </div>

                  <div class="col-span-2 flex flex-col gap-2">
                    <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">{{ t('history.lim_obs') }}</p>
                    <ul class="flex flex-col gap-1.5">
                      <li v-for="(o, i) in a.observations" :key="i"
                        class="flex items-start gap-2 text-sm text-on-surface">
                        <span class="material-symbols-outlined text-sm text-primary mt-0.5 flex-shrink-0">chevron_right</span>
                        {{ tBackend(o) }}
                      </li>
                    </ul>
                  </div>

                  <div class="col-span-2 flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
                    <span class="material-symbols-outlined text-amber-600 text-sm mt-0.5 flex-shrink-0">warning</span>
                    <div>
                      <p class="text-[10px] font-bold uppercase tracking-widest text-amber-700 mb-1">{{ t('history.lim_limits') }}</p>
                      <p class="text-sm text-amber-900 leading-relaxed">{{ tBackend(a.limitations) }}</p>
                    </div>
                  </div>

                </div>
              </div>
            </transition>

          </div>
        </div>

      </div>

      <!-- Footer -->
      <footer class="px-8 py-4 border-t border-outline-variant text-xs text-on-surface-variant text-center">
        Projet personnel · EFREI Paris · 2025-2026
      </footer>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { auth } from '../store/auth.js'
import { t, locale, toggleLocale, tBackend } from '../store/locale.js'
const raviLogo = '/ravi-logo.png'

const router     = useRouter()
const filter     = ref('')
const modeFilter = ref('')
const selected   = ref(null)
const isLoading  = ref(true)

const userInitials = computed(() => {
  const name = auth.user?.name ?? ''
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) || 'U'
})

function logout() { auth.logout(); router.push('/login') }

function classLabel(pred) {
  return { normal: t('class.normal'), suspected_opacity: t('class.suspected_opacity'), uncertain: t('class.uncertain') }[pred] ?? pred
}
function predClass(pred) {
  return { normal: 'text-emerald-700', suspected_opacity: 'text-orange-700', uncertain: 'text-amber-700' }[pred] ?? ''
}
function countByClass(cls) {
  return analyses.value.filter(a => a.prediction === cls).length
}
function confColor(c) {
  if (c >= 0.75) return '#10b981'
  if (c >= 0.55) return '#f59e0b'
  return '#ef4444'
}
function formatDate(iso) {
  return new Date(iso).toLocaleString('fr-FR', {
    day: '2-digit', month: 'long', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

const analyses = ref([])

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/analyses/me')
    analyses.value = data.map(a => ({
      id:           a.id,
      date:         formatDate(a.created_at),
      mode:         a.mode,
      prediction:   a.predicted_class,
      confidence:   a.confidence,
      threshold:    a.threshold ?? 0.70,
      imageQuality: a.image_quality ?? 'good',
      justification: a.justification ?? '',
      observations: [],
      limitations:  a.warning ?? '',
      model_name:   a.model_name,
    }))
  } catch (e) {
    console.error('Erreur chargement historique:', e.message)
  } finally {
    isLoading.value = false
  }
})

const filteredAnalyses = computed(() => {
  let list = analyses.value
  if (filter.value)     list = list.filter(a => a.prediction === filter.value)
  if (modeFilter.value) list = list.filter(a => a.mode === modeFilter.value)
  return list
})
</script>

<style scoped>
.filter-select {
  padding: 8px 12px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  font-family: system-ui, sans-serif;
  color: #0f172a;
  background: white;
  outline: none;
  cursor: pointer;
  transition: border-color 0.15s;
}
.filter-select:focus { border-color: #3b82f6; }

.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
