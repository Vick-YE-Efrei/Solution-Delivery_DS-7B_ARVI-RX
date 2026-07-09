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
          class="rounded-xl px-4 py-3 flex items-center gap-3.5 border border-blue-500/20 bg-blue-600/10 text-blue-400">
          <span class="material-symbols-outlined text-xl" style="font-variation-settings:'FILL' 1">radiology</span>
          <span class="font-semibold text-sm">{{ t('nav.analysis') }}</span>
        </router-link>
        <router-link to="/history"
          class="text-slate-400 hover:text-white rounded-xl px-4 py-3 flex items-center gap-3.5 hover:bg-white/5 transition-colors">
          <span class="material-symbols-outlined text-xl">history</span>
          <span class="font-medium text-sm">{{ t('nav.history') }}</span>
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
    <main class="flex-1 flex flex-col relative overflow-hidden">

      <!-- Top Bar -->
      <header class="flex justify-between items-center px-[32px] h-16 w-full glass-header sticky top-0 z-40 border-b border-outline-variant">
        <div class="flex items-center gap-4">
          <h2 class="page-title-font text-lg font-extrabold text-on-surface">{{ t('home.title') }}</h2>
        </div>
        <div class="flex items-center gap-4">
          <!-- API Status -->
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-100">
            <span class="w-2 h-2 rounded-full bg-emerald-500 status-pulse"></span>
            <span class="text-[10px] font-bold text-emerald-700 uppercase tracking-wider">{{ t('home.api_connected') }}</span>
          </div>
        </div>
      </header>

      <!-- Warning Banner (obligatoire) -->
      <div class="mx-[32px] mt-4 mb-2">
        <div class="bg-[#fef3c7] text-[#92400e] px-6 py-3 flex items-center justify-center gap-3 w-full border border-[#fde68a] rounded-xl premium-shadow">
          <span class="material-symbols-outlined text-lg">warning</span>
          <span class="font-bold text-xs tracking-wide">{{ t('common.warning') }}</span>
        </div>
      </div>

      <!-- Page Container -->
      <div class="px-[32px] py-4 space-y-4 flex-1">

        <!-- STATE: EMPTY -->
        <div v-if="!hasResults" class="flex flex-col items-center justify-center flex-1 min-h-[500px]">
          <div
            class="drop-zone-border rounded-2xl p-16 flex flex-col items-center justify-center w-full max-w-2xl cursor-pointer bg-white premium-shadow"
            :class="{ 'drag-over': isDragging }"
            @click="$refs.fileInput.click()"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="onDrop"
          >
            <input ref="fileInput" type="file" accept=".png,.jpg,.jpeg" class="hidden" @change="onFileChange" />
            <div class="w-20 h-20 rounded-full bg-blue-50 flex items-center justify-center mb-6">
              <span class="material-symbols-outlined text-primary text-4xl">upload_file</span>
            </div>
            <h3 class="page-title-font text-xl font-extrabold text-on-surface mb-2">{{ t('home.drop_title') }}</h3>
            <p class="text-sm text-on-surface-variant mb-6">{{ t('home.drop_formats') }}</p>
            <button class="btn-primary-gradient text-white font-bold px-8 py-3 rounded-full text-sm hover:scale-[1.02] active:scale-95 transition-all">
              {{ t('home.browse') }}
            </button>
          </div>
          <div class="mt-6 flex items-center gap-2 text-on-surface-variant">
            <span class="material-symbols-outlined text-sm">lock</span>
            <p class="text-xs">{{ t('home.privacy_hint') }}</p>
          </div>
        </div>

        <!-- STATE: ANALYZING -->
        <div v-else-if="isAnalyzing" class="flex flex-col items-center justify-center flex-1 min-h-[500px] gap-6">
          <div class="w-20 h-20 rounded-full bg-blue-50 flex items-center justify-center">
            <span class="material-symbols-outlined text-primary text-4xl animate-spin">refresh</span>
          </div>
          <div class="text-center">
            <p class="page-title-font text-lg font-extrabold text-on-surface">{{ t('home.analyzing') }}</p>
            <p class="text-sm text-on-surface-variant mt-1">{{ t('home.analyzing_hint') }}</p>
          </div>
        </div>

        <!-- STATE: ERROR -->
        <div v-else-if="analyzeError && !currentResult" class="flex flex-col items-center justify-center flex-1 min-h-[400px] gap-4">
          <div class="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center">
            <span class="material-symbols-outlined text-red-500 text-3xl">error</span>
          </div>
          <p class="page-title-font text-base font-extrabold text-on-surface">{{ t('home.error_title') }}</p>
          <p class="text-sm text-slate-600 max-w-md text-center">{{ analyzeError }}</p>
          <button @click="resetUpload" class="btn-primary-gradient text-white font-bold px-6 py-2.5 rounded-full text-sm hover:scale-[1.02] transition-all">
            {{ t('home.retry') }}
          </button>
        </div>

        <!-- STATE: RESULTS -->
        <div v-else class="flex-col gap-4 fade-in">

          <!-- Main Card -->
          <div class="bg-white rounded-2xl premium-shadow border border-outline-variant flex overflow-hidden min-h-[480px]">

            <!-- Gauche : Image -->
            <div class="w-[58%] border-r border-outline-variant flex flex-col p-6">
              <div class="flex items-center justify-between mb-3">
                <p class="text-xs font-semibold text-on-surface-variant tracking-wide">{{ fileName }}</p>
                <button @click="resetUpload" class="text-xs text-primary font-bold hover:underline flex items-center gap-1">
                  <span class="material-symbols-outlined text-sm">swap_horiz</span>
                  {{ t('home.change_image') }}
                </button>
              </div>
              <div class="flex-1 rounded-xl media-frame-inner relative overflow-hidden flex items-center justify-center border border-slate-800">
                <img :src="previewUrl" class="max-w-full max-h-full object-contain p-4" alt="Radiographie uploadée" />
              </div>
            </div>

            <!-- Droite : Résultats -->
            <div class="w-[42%] p-6 flex flex-col gap-5 bg-slate-50/30">
              <h3 class="page-title-font text-base font-extrabold flex items-center gap-2">
                <span class="material-symbols-outlined text-primary text-lg">analytics</span>
                {{ t('home.results_title') }}
              </h3>

              <!-- Qualité -->
              <div>
                <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-[0.1em] mb-2">{{ t('home.image_quality') }}</p>
                <span :class="qualityBadgeClass" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold border" v-html="qualityBadgeHtml"></span>
              </div>

              <!-- Classe prédite -->
              <div :class="classBadgeClass" class="p-4 rounded-xl border-2 transition-all">
                <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-[0.1em] mb-2">{{ t('home.predicted_class') }}</p>
                <div class="flex items-center gap-3">
                  <span :class="classIconClass" class="material-symbols-outlined text-2xl">{{ classIcon }}</span>
                  <span :class="classLabelClass" class="page-title-font text-xl font-extrabold">{{ classText }}</span>
                </div>
              </div>

              <!-- Confiance -->
              <div>
                <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-[0.1em] mb-2">{{ t('home.confidence') }}</p>
                <div class="flex items-center gap-3 mb-2">
                  <span class="page-title-font text-2xl font-black text-primary">{{ confidencePct }}%</span>
                </div>
                <div class="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden">
                  <div :class="confBarColor" class="h-full rounded-full confidence-bar" :style="{ width: confidencePct + '%' }"></div>
                </div>
              </div>

              <!-- Observations -->
              <div>
                <div class="flex items-center gap-2 mb-2">
                  <span class="material-symbols-outlined text-primary text-base">visibility</span>
                  <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-[0.1em]">{{ t('home.observations') }}</p>
                </div>
                <ul class="space-y-1 text-[13px] text-on-surface-variant">
                  <li v-for="(obs, i) in currentResult.visual_evidence" :key="i" class="flex items-start gap-2">
                    <span class="text-primary mt-0.5">•</span>{{ tBackend(obs) }}
                  </li>
                </ul>
              </div>

              <!-- Justification -->
              <div>
                <div class="flex items-center gap-2 mb-2">
                  <span class="material-symbols-outlined text-primary text-base">description</span>
                  <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-[0.1em]">{{ t('home.justification') }}</p>
                </div>
                <div class="bg-blue-50 border border-blue-100 rounded-xl p-4 max-h-64 overflow-y-auto">
                  <p class="text-[13px] text-slate-700 leading-relaxed whitespace-pre-wrap">{{ currentResult.justification }}</p>
                </div>
              </div>

              <div class="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
                <span class="material-symbols-outlined text-amber-600 text-lg mt-0.5 flex-shrink-0">health_and_safety</span>
                <div>
                  <p class="text-[10px] font-bold text-amber-700 uppercase tracking-[0.1em] mb-1">{{ t('home.safety_title') }}</p>
                  <p class="text-[13px] text-amber-900 leading-relaxed">{{ t('home.safety_text') }}</p>
                </div>
              </div>

              <!-- Informations techniques -->
              <details class="group border border-outline-variant rounded-xl overflow-hidden bg-white">
                <summary class="list-none px-4 py-3 cursor-pointer flex justify-between items-center hover:bg-slate-50 transition-colors">
                  <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-slate-400 text-base">terminal</span>
                    <span class="font-bold text-[10px] text-slate-500 uppercase tracking-widest">{{ t('home.tech_info') }}</span>
                  </div>
                  <span class="material-symbols-outlined transition-transform duration-300 group-open:rotate-180 text-slate-400 text-lg">expand_more</span>
                </summary>
                <div class="px-4 pb-4 pt-1 space-y-2">
                  <div class="flex justify-between border-b border-slate-100 py-2">
                    <span class="text-[10px] font-bold text-slate-400 uppercase">{{ t('home.model') }}</span>
                    <span class="text-[10px] font-mono font-bold text-primary">{{ currentResult.model_name }}</span>
                  </div>
                  <div class="flex justify-between border-b border-slate-100 py-2">
                    <span class="text-[10px] font-bold text-slate-400 uppercase">{{ t('home.prompt_version') }}</span>
                    <span class="text-[10px] font-mono font-bold text-slate-600">{{ currentResult.prompt_version }}</span>
                  </div>
                  <div class="flex justify-between border-b border-slate-100 py-2">
                    <span class="text-[10px] font-bold text-slate-400 uppercase">{{ t('home.latency') }}</span>
                    <span class="text-[10px] font-mono font-bold text-emerald-600">{{ currentResult.latency_ms }} ms</span>
                  </div>
                  <div v-if="currentResult.limitations?.length" class="flex justify-between gap-4 border-b border-slate-100 py-2">
                    <span class="text-[10px] font-bold text-slate-400 uppercase flex-shrink-0">{{ t('home.limits') }}</span>
                    <span class="text-[10px] text-slate-600 text-right leading-relaxed">{{ currentResult.limitations.map(tBackend).join(' - ') }}</span>
                  </div>
                  <button @click="showJson = true"
                    class="mt-2 w-full bg-white border border-outline-variant text-[#475569] font-bold py-2 rounded-lg flex items-center justify-center gap-2 text-[11px] hover:bg-slate-50 transition-all" style="border-width:1.5px">
                    <span class="material-symbols-outlined text-base">code</span>
                    {{ t('home.view_json') }}
                  </button>
                </div>
              </details>
            </div>
          </div>

          <!-- Tableau historique -->
          <div class="bg-white rounded-2xl premium-shadow border border-outline-variant overflow-hidden mt-4">
            <div class="px-6 py-3 border-b border-outline-variant bg-slate-50/80 flex items-center justify-between">
              <h3 class="page-title-font text-sm font-extrabold flex items-center gap-2">
                <span class="material-symbols-outlined text-primary text-lg">history</span>
                {{ t('home.recent_history') }}
              </h3>
              <span class="text-[10px] text-on-surface-variant font-bold">{{ history.length }} analyse{{ history.length > 1 ? 's' : '' }}</span>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-left">
                <thead>
                  <tr class="border-b border-outline-variant bg-slate-50/50">
                    <th class="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ t('home.col_timestamp') }}</th>
                    <th class="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ t('home.col_image') }}</th>
                    <th class="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ t('home.col_class') }}</th>
                    <th class="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ t('home.col_confidence') }}</th>
                    <th class="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ t('home.col_quality') }}</th>
                    <th class="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ t('home.col_model') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="history.length === 0">
                    <td colspan="6" class="px-6 py-8 text-center text-sm text-on-surface-variant">{{ t('home.no_analysis') }}</td>
                  </tr>
                  <tr v-for="h in history" :key="h.ts + h.filename"
                    class="border-b border-outline-variant hover:bg-slate-50/50 transition-colors">
                    <td class="px-6 py-3 text-[11px] text-slate-600 font-mono">{{ h.ts }}</td>
                    <td class="px-6 py-3 text-[11px] text-on-surface font-semibold truncate max-w-[180px]">{{ h.filename }}</td>
                    <td class="px-6 py-3">
                      <span v-if="h.predicted_class === 'normal'" class="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded-full text-[10px] font-bold border border-emerald-100">{{ t('class.normal') }}</span>
                      <span v-else-if="h.predicted_class === 'suspected_opacity'" class="px-2 py-0.5 bg-amber-50 text-amber-700 rounded-full text-[10px] font-bold border border-amber-100">{{ t('class.suspected_opacity') }}</span>
                      <span v-else class="px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full text-[10px] font-bold border border-slate-200">{{ t('class.uncertain') }}</span>
                    </td>
                    <td class="px-6 py-3 text-[11px] font-bold text-on-surface">{{ (h.confidence * 100).toFixed(1) }}%</td>
                    <td class="px-6 py-3">
                      <span v-if="h.image_quality === 'good'" class="text-emerald-600 text-[11px] font-semibold">{{ t('quality.good') }}</span>
                      <span v-else-if="h.image_quality === 'limited'" class="text-amber-600 text-[11px] font-semibold">{{ t('quality.limited') }}</span>
                      <span v-else class="text-red-600 text-[11px] font-semibold">{{ t('quality.poor') }}</span>
                    </td>
                    <td class="px-6 py-3 text-[10px] font-mono text-slate-500">{{ h.model_name }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <footer class="w-full py-4 mt-auto border-t border-outline-variant bg-white/50 flex items-center justify-center px-[32px]">
        <span class="text-[9px] text-slate-400 font-semibold">{{ t('common.not_medical') }}</span>
      </footer>
    </main>
  </div>

  <!-- JSON Modal -->
  <Teleport to="body">
    <div v-if="showJson"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center"
      @click.self="showJson = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-outline-variant">
          <h3 class="page-title-font font-extrabold text-base">{{ t('home.json_title') }}</h3>
          <button @click="showJson = false"
            class="w-8 h-8 rounded-full hover:bg-slate-100 flex items-center justify-center transition-all">
            <span class="material-symbols-outlined text-lg">close</span>
          </button>
        </div>
        <pre class="p-6 overflow-auto text-[12px] font-mono text-slate-700 leading-relaxed flex-1 bg-slate-50">{{ JSON.stringify(currentResult, null, 2) }}</pre>
      </div>
    </div>
  </Teleport>

  <!-- Terms of Use Modal -->
  <Teleport to="body">
    <div v-if="showTerms"
      class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[110] flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl flex flex-col max-h-[90vh]">

        <!-- Header -->
        <div class="flex items-center gap-3 px-6 py-5 border-b border-outline-variant">
          <div class="w-9 h-9 rounded-xl bg-amber-100 flex items-center justify-center flex-shrink-0">
            <span class="material-symbols-outlined text-amber-600 text-xl">gavel</span>
          </div>
          <div>
            <h3 class="page-title-font font-extrabold text-base text-on-surface">{{ t('terms.title') }}</h3>
            <p class="text-[11px] text-on-surface-variant mt-0.5">{{ t('terms.subtitle') }}</p>
          </div>
        </div>

        <!-- Content scrollable -->
        <div class="overflow-y-auto flex-1 px-6 py-5 space-y-5">
          <div v-for="n in ['s1','s2','s3','s4','s5','s6','s7','s8','s9']" :key="n">
            <p class="text-[12px] font-bold text-on-surface mb-1">{{ t('terms.' + n + '_title') }}</p>
            <p class="text-[12px] text-on-surface-variant leading-relaxed whitespace-pre-line">{{ t('terms.' + n + '_body') }}</p>
          </div>
          <div class="border-t border-slate-200 pt-4">
            <p class="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">{{ t('terms.refs_title') }}</p>
            <p class="text-[11px] text-slate-400 leading-relaxed whitespace-pre-line">{{ t('terms.refs_body') }}</p>
          </div>
        </div>

        <!-- Checkbox + buttons -->
        <div class="px-6 py-5 border-t border-outline-variant space-y-4 bg-slate-50 rounded-b-2xl">
          <label class="flex items-start gap-3 cursor-pointer group">
            <input type="checkbox" v-model="termsChecked"
              class="mt-0.5 w-4 h-4 accent-primary flex-shrink-0 cursor-pointer" />
            <span class="text-[12px] font-semibold text-on-surface leading-relaxed group-hover:text-primary transition-colors">
              {{ t('terms.checkbox') }}
            </span>
          </label>
          <div class="flex gap-3">
            <button @click="cancelTerms"
              class="flex-1 px-4 py-2.5 rounded-xl text-[12px] font-semibold text-slate-500 bg-white border border-slate-200 hover:bg-slate-100 transition-all">
              {{ t('terms.cancel') }}
            </button>
            <button @click="confirmTerms" :disabled="!termsChecked"
              class="flex-1 px-4 py-2.5 rounded-xl text-[12px] font-semibold transition-all"
              :class="termsChecked
                ? 'bg-primary text-white hover:opacity-90 cursor-pointer'
                : 'bg-slate-100 text-slate-400 cursor-not-allowed'">
              {{ t('terms.confirm') }}
            </button>
          </div>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { auth } from '../store/auth.js'
import { t, locale, toggleLocale, tBackend } from '../store/locale.js'
const raviLogo = '/ravi-logo.png'

const router = useRouter()

// ── State ──
const fileInput     = ref(null)
const currentFile   = ref(null)
const hasResults    = ref(false)
const isDragging    = ref(false)
const isAnalyzing   = ref(false)
const analyzeError  = ref('')
const fileName      = ref('')
const previewUrl    = ref('')
const currentResult = ref(null)
const history       = ref([])
const showJson      = ref(false)
const showTerms     = ref(false)
const termsChecked  = ref(false)
const pendingFile   = ref(null)

function shouldUseMockAnalysis() {
  const params = new URLSearchParams(window.location.search)
  return import.meta.env.VITE_USE_MOCK_ANALYSIS === 'true' || params.get('mock') === '1' || localStorage.getItem('arvi_mock_analysis') === 'true'
}

// ── Auth ──
const userInitials = computed(() => {
  const name = auth.user?.name ?? 'EF'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
})
function logout() { auth.logout(); router.push('/login') }


// ── Upload ──
function onFileChange(e) {
  const file = e.target.files[0]
  if (file) processFile(file)
}
function onDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) processFile(file)
}
function processFile(file) {
  const ext = file.name.split('.').pop().toLowerCase()
  if (!['png', 'jpg', 'jpeg'].includes(ext)) {
    alert('Format non supporté. Utilisez PNG, JPG ou JPEG.')
    return
  }
  currentFile.value = file
  fileName.value    = file.name
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value   = e.target.result
    pendingFile.value  = file
    termsChecked.value = false
    showTerms.value    = true
  }
  reader.readAsDataURL(file)
}

function confirmTerms() {
  if (!termsChecked.value) return
  showTerms.value  = false
  hasResults.value = true
  runAnalysis(pendingFile.value)
  pendingFile.value = null
}

function cancelTerms() {
  showTerms.value    = false
  termsChecked.value = false
  pendingFile.value  = null
  resetUpload()
}

function resetUpload() {
  hasResults.value    = false
  previewUrl.value    = ''
  fileName.value      = ''
  currentResult.value = null
  currentFile.value   = null
  analyzeError.value  = ''
  if (fileInput.value) fileInput.value.value = ''
}

// ── Analyse via API → FastAPI → MedGemma ──
function mockAnalysisResult(file) {
  const lowerName = file.name.toLowerCase()
  const forcedUncertain = lowerName.includes('incertain') || lowerName.includes('uncertain') || lowerName.includes('flou')
  const forcedOpacity = lowerName.includes('pneumonie') || lowerName.includes('pneumonia') || lowerName.includes('opacity') || lowerName.includes('opacite')
  const predictedClass = forcedUncertain ? 'uncertain' : forcedOpacity ? 'suspected_opacity' : 'normal'
  const isFr = locale.value === 'fr'

  const contentByClass = {
    normal: {
      confidence: 0.86,
      image_quality: 'good',
      visual_evidence: isFr
        ? ['Champs pulmonaires globalement symetriques.', 'Aucune opacite focale evidente sur cette simulation.', 'Silhouette cardiaque sans elargissement marque.']
        : ['Lung fields appear globally symmetric.', 'No obvious focal opacity in this simulation.', 'Cardiac silhouette shows no marked enlargement.'],
      justification: isFr
        ? "La lecture proposée ne met pas en évidence d'opacité focale. Les champs pulmonaires paraissent globalement symétriques, avec une qualité d'image suffisante pour une analyse structurée."
        : 'The assisted reading does not highlight an obvious focal opacity. The lung fields appear globally symmetric, with sufficient image quality for a structured analysis.',
    },
    suspected_opacity: {
      confidence: 0.78,
      image_quality: 'good',
      visual_evidence: isFr
        ? ['Opacite pulmonaire focale suspectee dans un champ pulmonaire.', 'Asymetrie visuelle entre les deux cotes.', 'Qualite suffisante pour produire une reponse structuree.']
        : ['Focal pulmonary opacity suspected in one lung field.', 'Visual asymmetry between both sides.', 'Image quality is sufficient for a structured response.'],
      justification: isFr
        ? "La lecture proposée signale une opacité focale suspecte. Ce résultat doit être interprété comme une aide à la lecture et confirmé par un professionnel de santé."
        : 'The assisted reading highlights a suspected focal opacity. This result should be treated as reading support and confirmed by a healthcare professional.',
    },
    uncertain: {
      confidence: 0.48,
      image_quality: 'limited',
      visual_evidence: isFr
        ? ['Qualite ou contraste limite dans cette simulation.', 'Signes visuels insuffisants pour conclure.', 'Classe incertaine activee comme garde-fou.']
        : ['Limited quality or contrast in this simulation.', 'Visual signs are insufficient to conclude.', 'Uncertain class is activated as a safety guardrail.'],
      justification: isFr
        ? "La lecture proposée reste incertaine car les signes visibles ou la qualité d'image ne permettent pas une conclusion fiable. Une validation humaine est nécessaire."
        : 'The assisted reading remains uncertain because visible signs or image quality do not support a reliable conclusion. Human review is required.',
    },
  }

  const selected = contentByClass[predictedClass]

  return {
    image_quality: selected.image_quality,
    predicted_class: predictedClass,
    confidence: selected.confidence,
    threshold: 0.7,
    visual_evidence: selected.visual_evidence,
    justification: selected.justification,
    limitations: isFr
      ? ['Analyse assistée, non diagnostique.', 'Validation humaine requise.']
      : ['Assisted analysis, non-diagnostic.', 'Human review required.'],
    warning: isFr
      ? 'Prototype pedagogique, sans valeur diagnostique.'
      : 'Educational prototype, not a diagnostic output.',
    model_name: 'MedGemma - simulation locale',
    prompt_version: 'local-ui-preview',
    latency_ms: 820,
    mode: 'improved',
  }
}

async function runAnalysis(file) {
  isAnalyzing.value  = true
  analyzeError.value = ''
  currentResult.value = null

  try {
    if (shouldUseMockAnalysis()) {
      await new Promise(resolve => setTimeout(resolve, 700))
      const data = mockAnalysisResult(file)
      currentResult.value = data
      addToHistory(file.name, data)
      return
    }

    const form = new FormData()
    form.append('image', file)
    form.append('mode', 'improved')
    form.append('model_key', 'medgemma_4b_pt')
    form.append('lang', locale.value)

    const { data } = await axios.post('/api/analyses/predict', form, {
      timeout: 300_000,
    })

    currentResult.value = data
    addToHistory(file.name, data)
  } catch (err) {
    const msg = err.response?.data?.message ?? err.message
    analyzeError.value = msg
  } finally {
    isAnalyzing.value = false
  }
}

function addToHistory(name, r) {
  const ts = new Date().toLocaleString('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  })
  history.value.unshift({ ts, filename: name, ...r })
  if (history.value.length > 10) history.value.pop()
}

// Charger l'historique réel depuis MySQL au démarrage
onMounted(async () => {
  document.addEventListener('keydown', onKeydown)
  try {
    const { data } = await axios.get('/api/analyses/me')
    history.value = data.map(a => ({
      ts:              new Date(a.created_at).toLocaleString('fr-FR'),
      filename:        a.filename,
      predicted_class: a.predicted_class,
      confidence:      a.confidence,
      image_quality:   a.image_quality,
      model_name:      a.model_name,
    }))
  } catch (_) {}
})
onUnmounted(() => document.removeEventListener('keydown', onKeydown))

// ── Computed display ──
const confidencePct = computed(() =>
  currentResult.value ? (currentResult.value.confidence * 100).toFixed(1) : '0'
)
const confBarColor = computed(() => {
  const c = currentResult.value?.confidence ?? 0
  return c > 0.7 ? 'bg-emerald-500' : c > 0.5 ? 'bg-amber-500' : 'bg-red-500'
})
const qualityBadgeClass = computed(() => {
  const q = currentResult.value?.image_quality
  if (q === 'good')    return 'bg-emerald-50 border-emerald-200 text-emerald-700'
  if (q === 'limited') return 'bg-amber-50 border-amber-200 text-amber-700'
  return 'bg-red-50 border-red-200 text-red-700'
})
const qualityBadgeHtml = computed(() => {
  const q = currentResult.value?.image_quality
  if (q === 'good')    return `<span class="material-symbols-outlined text-sm">check_circle</span> ${t('quality.good')}`
  if (q === 'limited') return `<span class="material-symbols-outlined text-sm">warning</span> ${t('quality.limited')}`
  return `<span class="material-symbols-outlined text-sm">error</span> ${t('quality.poor')}`
})
const classBadgeClass = computed(() => {
  const p = currentResult.value?.predicted_class
  if (p === 'normal')            return 'class-badge-normal'
  if (p === 'suspected_opacity') return 'class-badge-opacity'
  return 'class-badge-uncertain'
})
const classIcon = computed(() => {
  const p = currentResult.value?.predicted_class
  if (p === 'normal')            return 'check_circle'
  if (p === 'suspected_opacity') return 'warning'
  return 'help'
})
const classIconClass = computed(() => {
  const p = currentResult.value?.predicted_class
  if (p === 'normal')            return 'text-emerald-600'
  if (p === 'suspected_opacity') return 'text-amber-600'
  return 'text-slate-500'
})
const classText = computed(() => {
  const p = currentResult.value?.predicted_class
  if (p === 'normal')            return t('class.normal')
  if (p === 'suspected_opacity') return t('class.suspected_opacity')
  return t('class.uncertain')
})
const classLabelClass = computed(() => {
  const p = currentResult.value?.predicted_class
  if (p === 'normal')            return 'page-title-font text-xl font-extrabold text-emerald-700'
  if (p === 'suspected_opacity') return 'page-title-font text-xl font-extrabold text-amber-700'
  return 'page-title-font text-xl font-extrabold text-slate-600'
})

function onKeydown(e) { if (e.key === 'Escape') showJson.value = false }
</script>
