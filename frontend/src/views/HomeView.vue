<template>
  <div class="flex min-h-screen">

    <!-- ═══════════════════ SIDEBAR ═══════════════════ -->
    <aside class="flex flex-col h-screen w-64 sticky left-0 top-0 bg-[#0f172a] py-6 z-50">
      <div class="flex flex-col items-center px-4 mb-6">
        <div class="w-16 h-16 rounded-2xl overflow-hidden ring-2 ring-white/10 shadow-lg mb-3">
          <img :src="raviLogo" alt="RAVI" class="w-full h-full object-cover" />
        </div>
        <h1 class="page-title-font text-xl text-white font-extrabold tracking-tight">RAVI</h1>
        <p class="text-[9px] uppercase tracking-[0.25em] text-slate-500 font-bold mt-0.5">Prototype Pédagogique</p>
        <div class="w-full h-px bg-gradient-to-r from-transparent via-slate-700 to-transparent mt-4"></div>
      </div>

      <nav class="flex-1 px-4 space-y-1">
        <router-link to="/"
          class="rounded-xl px-4 py-3 flex items-center gap-3.5 border border-blue-500/20 bg-blue-600/10 text-blue-400">
          <span class="material-symbols-outlined text-xl" style="font-variation-settings:'FILL' 1">radiology</span>
          <span class="font-semibold text-sm">Analyse RX Thorax</span>
        </router-link>
        <router-link to="/history"
          class="text-slate-400 hover:text-white rounded-xl px-4 py-3 flex items-center gap-3.5 hover:bg-white/5 transition-colors">
          <span class="material-symbols-outlined text-xl">history</span>
          <span class="font-medium text-sm">Historique</span>
        </router-link>
        <router-link v-if="auth.isAdmin" to="/admin"
          class="text-slate-400 hover:text-white rounded-xl px-4 py-3 flex items-center gap-3.5 hover:bg-white/5 transition-colors">
          <span class="material-symbols-outlined text-xl">assessment</span>
          <span class="font-medium text-sm">Métriques</span>
        </router-link>
        <router-link to="/guide"
          class="text-slate-400 hover:text-white rounded-xl px-4 py-3 flex items-center gap-3.5 hover:bg-white/5 transition-colors">
          <span class="material-symbols-outlined text-xl">menu_book</span>
          <span class="font-medium text-sm">Guide d'utilisation</span>
        </router-link>
        <router-link to="/about"
          class="text-slate-400 hover:text-white rounded-xl px-4 py-3 flex items-center gap-3.5 hover:bg-white/5 transition-colors">
          <span class="material-symbols-outlined text-xl">info</span>
          <span class="font-medium text-sm">À propos</span>
        </router-link>
      </nav>

      <div class="px-6 py-4 mt-auto border-t border-slate-800">
        <div class="flex items-center gap-3.5 p-3 rounded-2xl bg-slate-900/50 border border-slate-800 mb-3">
          <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
            {{ userInitials }}
          </div>
          <div class="overflow-hidden">
            <p class="font-bold text-xs text-white truncate">{{ auth.user?.name ?? 'Projet EFREI' }}</p>
            <p class="text-[9px] text-slate-500 font-semibold uppercase tracking-wider">Solution Delivery 2025-2026</p>
          </div>
        </div>
        <button @click="logout"
          class="w-full flex items-center justify-center gap-2 mt-1 px-3 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all">
          <span class="material-symbols-outlined text-base">logout</span>
          Déconnexion
        </button>
      </div>
    </aside>

    <!-- ═══════════════════ MAIN ═══════════════════ -->
    <main class="flex-1 flex flex-col relative overflow-hidden">

      <!-- Top Bar -->
      <header class="flex justify-between items-center px-[32px] h-16 w-full glass-header sticky top-0 z-40 border-b border-outline-variant">
        <div class="flex items-center gap-4">
          <h2 class="page-title-font text-lg font-extrabold text-on-surface">Analyse Thoracique</h2>
        </div>
        <div class="flex items-center gap-4">
          <!-- Mode Toggle -->
          <div class="flex items-center gap-2 bg-surface-container-low rounded-full p-1 border border-outline-variant">
            <button @click="setMode('baseline')"
              :class="currentMode === 'baseline'
                ? 'px-4 py-1.5 rounded-full text-[11px] font-bold transition-all bg-primary text-white'
                : 'px-4 py-1.5 rounded-full text-[11px] font-bold transition-all text-on-surface-variant hover:bg-white'">
              Baseline
            </button>
            <button @click="setMode('improved')"
              :class="currentMode === 'improved'
                ? 'px-4 py-1.5 rounded-full text-[11px] font-bold transition-all bg-primary text-white'
                : 'px-4 py-1.5 rounded-full text-[11px] font-bold transition-all text-on-surface-variant hover:bg-white'">
              Improved
            </button>
          </div>
          <!-- Sélecteur modèle -->
          <select v-model="currentModel"
            class="text-[11px] font-bold text-slate-600 border border-outline-variant rounded-full px-3 py-1.5 bg-white outline-none cursor-pointer">
            <option value="medgemma_4b_pt">MedGemma 4B PT</option>
            <option value="gemma_4_E4B">Gemma 4E4B</option>
          </select>
          <!-- API Status -->
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-100">
            <span class="w-2 h-2 rounded-full bg-emerald-500 status-pulse"></span>
            <span class="text-[10px] font-bold text-emerald-700 uppercase tracking-wider">API Connectée</span>
          </div>
        </div>
      </header>

      <!-- Warning Banner (obligatoire) -->
      <div class="mx-[32px] mt-4 mb-2">
        <div class="bg-[#fef3c7] text-[#92400e] px-6 py-3 flex items-center justify-center gap-3 w-full border border-[#fde68a] rounded-xl premium-shadow">
          <span class="material-symbols-outlined text-lg">warning</span>
          <span class="font-bold text-xs tracking-wide">ATTENTION : Ceci est un prototype à but pédagogique. Les résultats présentés n'équivalent pas à un diagnostic médical. Nous vous prions de faire valider tout résultat par un professionnel de la santé.</span>
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
            <h3 class="page-title-font text-xl font-extrabold text-on-surface mb-2">Déposer une radiographie thoracique frontale</h3>
            <p class="text-sm text-on-surface-variant mb-6">Formats acceptés : PNG, JPG, JPEG</p>
            <button class="btn-primary-gradient text-white font-bold px-8 py-3 rounded-full text-sm hover:scale-[1.02] active:scale-95 transition-all">
              Parcourir les fichiers
            </button>
          </div>
          <div class="mt-6 flex items-center gap-2 text-on-surface-variant">
            <span class="material-symbols-outlined text-sm">info</span>
            <p class="text-xs">Utilisez les images synthétiques du dossier
              <code class="bg-slate-100 px-1.5 py-0.5 rounded text-[11px] font-mono">data/sample_images</code>
              pour tester le flux.
            </p>
          </div>
        </div>

        <!-- STATE: ANALYZING -->
        <div v-else-if="isAnalyzing" class="flex flex-col items-center justify-center flex-1 min-h-[500px] gap-6">
          <div class="w-20 h-20 rounded-full bg-blue-50 flex items-center justify-center">
            <span class="material-symbols-outlined text-primary text-4xl animate-spin">refresh</span>
          </div>
          <div class="text-center">
            <p class="page-title-font text-lg font-extrabold text-on-surface">Analyse en cours...</p>
            <p class="text-sm text-on-surface-variant mt-1">Le modèle analyse la radiographie. Cela peut prendre quelques secondes.</p>
          </div>
          <div class="flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-100 rounded-full">
            <span class="w-2 h-2 rounded-full bg-blue-500 status-pulse"></span>
            <span class="text-[11px] font-bold text-blue-700 uppercase tracking-wider">{{ currentModel }} actif</span>
          </div>
        </div>

        <!-- STATE: ERROR -->
        <div v-else-if="analyzeError && !currentResult" class="flex flex-col items-center justify-center flex-1 min-h-[400px] gap-4">
          <div class="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center">
            <span class="material-symbols-outlined text-red-500 text-3xl">error</span>
          </div>
          <p class="page-title-font text-base font-extrabold text-on-surface">Analyse échouée</p>
          <p class="text-sm text-slate-600 max-w-md text-center">{{ analyzeError }}</p>
          <button @click="resetUpload" class="btn-primary-gradient text-white font-bold px-6 py-2.5 rounded-full text-sm hover:scale-[1.02] transition-all">
            Réessayer
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
                  Changer d'image
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
                Résultats de l'analyse
              </h3>

              <!-- Qualité -->
              <div>
                <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-[0.1em] mb-2">Qualité de l'image</p>
                <span :class="qualityBadgeClass" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold border" v-html="qualityBadgeHtml"></span>
              </div>

              <!-- Classe prédite -->
              <div :class="classBadgeClass" class="p-4 rounded-xl border-2 transition-all">
                <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-[0.1em] mb-2">Classe prédite</p>
                <div class="flex items-center gap-3">
                  <span :class="classIconClass" class="material-symbols-outlined text-2xl">{{ classIcon }}</span>
                  <span :class="classLabelClass" class="page-title-font text-xl font-extrabold">{{ classText }}</span>
                </div>
              </div>

              <!-- Confiance -->
              <div>
                <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-[0.1em] mb-2">Indice de confiance</p>
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
                  <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-[0.1em]">Observations visuelles</p>
                </div>
                <ul class="space-y-1 text-[13px] text-on-surface-variant">
                  <li v-for="(obs, i) in currentResult.visual_evidence" :key="i" class="flex items-start gap-2">
                    <span class="text-primary mt-0.5">•</span>{{ obs }}
                  </li>
                </ul>
              </div>

              <!-- Justification -->
              <div>
                <div class="flex items-center gap-2 mb-2">
                  <span class="material-symbols-outlined text-primary text-base">description</span>
                  <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-[0.1em]">Justification</p>
                </div>
                <div class="bg-blue-50 border border-blue-100 rounded-xl p-4">
                  <p class="text-[13px] text-slate-700 leading-relaxed">{{ currentResult.justification }}</p>
                </div>
              </div>

              <!-- Limites -->
              <div>
                <div class="flex items-center gap-2 mb-2">
                  <span class="material-symbols-outlined text-amber-500 text-base">report_problem</span>
                  <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-[0.1em]">Limites identifiées</p>
                </div>
                <div class="flex flex-wrap gap-2">
                  <span v-for="(lim, i) in currentResult.limitations" :key="i"
                    class="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-[11px] font-semibold border border-slate-200">
                    <span class="material-symbols-outlined text-amber-500 text-xs">bolt</span>{{ lim }}
                  </span>
                </div>
              </div>

              <!-- Informations techniques -->
              <details class="group border border-outline-variant rounded-xl overflow-hidden bg-white">
                <summary class="list-none px-4 py-3 cursor-pointer flex justify-between items-center hover:bg-slate-50 transition-colors">
                  <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-slate-400 text-base">terminal</span>
                    <span class="font-bold text-[10px] text-slate-500 uppercase tracking-widest">Informations techniques</span>
                  </div>
                  <span class="material-symbols-outlined transition-transform duration-300 group-open:rotate-180 text-slate-400 text-lg">expand_more</span>
                </summary>
                <div class="px-4 pb-4 pt-1 space-y-2">
                  <div class="flex justify-between border-b border-slate-100 py-2">
                    <span class="text-[10px] font-bold text-slate-400 uppercase">Modèle</span>
                    <span class="text-[10px] font-mono font-bold text-primary">{{ currentResult.model_name }}</span>
                  </div>
                  <div class="flex justify-between border-b border-slate-100 py-2">
                    <span class="text-[10px] font-bold text-slate-400 uppercase">Version prompt</span>
                    <span class="text-[10px] font-mono font-bold text-slate-600">{{ currentResult.prompt_version }}</span>
                  </div>
                  <div class="flex justify-between border-b border-slate-100 py-2">
                    <span class="text-[10px] font-bold text-slate-400 uppercase">Latence</span>
                    <span class="text-[10px] font-mono font-bold text-emerald-600">{{ currentResult.latency_ms }} ms</span>
                  </div>
                  <button @click="showJson = true"
                    class="mt-2 w-full bg-white border border-outline-variant text-[#475569] font-bold py-2 rounded-lg flex items-center justify-center gap-2 text-[11px] hover:bg-slate-50 transition-all" style="border-width:1.5px">
                    <span class="material-symbols-outlined text-base">code</span>
                    Voir le JSON brut
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
                Historique des analyses récentes
              </h3>
              <span class="text-[10px] text-on-surface-variant font-bold">{{ history.length }} analyse{{ history.length > 1 ? 's' : '' }}</span>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-left">
                <thead>
                  <tr class="border-b border-outline-variant bg-slate-50/50">
                    <th class="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Horodatage</th>
                    <th class="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Image</th>
                    <th class="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Classe</th>
                    <th class="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Confiance</th>
                    <th class="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Qualité</th>
                    <th class="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Modèle</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="history.length === 0">
                    <td colspan="6" class="px-6 py-8 text-center text-sm text-on-surface-variant">Aucune analyse effectuée pour le moment.</td>
                  </tr>
                  <tr v-for="h in history" :key="h.ts + h.filename"
                    class="border-b border-outline-variant hover:bg-slate-50/50 transition-colors">
                    <td class="px-6 py-3 text-[11px] text-slate-600 font-mono">{{ h.ts }}</td>
                    <td class="px-6 py-3 text-[11px] text-on-surface font-semibold truncate max-w-[180px]">{{ h.filename }}</td>
                    <td class="px-6 py-3">
                      <span v-if="h.predicted_class === 'normal'" class="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded-full text-[10px] font-bold border border-emerald-100">Normal</span>
                      <span v-else-if="h.predicted_class === 'suspected_opacity'" class="px-2 py-0.5 bg-amber-50 text-amber-700 rounded-full text-[10px] font-bold border border-amber-100">Opacité suspectée</span>
                      <span v-else class="px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full text-[10px] font-bold border border-slate-200">Incertain</span>
                    </td>
                    <td class="px-6 py-3 text-[11px] font-bold text-on-surface">{{ (h.confidence * 100).toFixed(1) }}%</td>
                    <td class="px-6 py-3">
                      <span v-if="h.image_quality === 'good'" class="text-emerald-600 text-[11px] font-semibold">Bonne</span>
                      <span v-else-if="h.image_quality === 'limited'" class="text-amber-600 text-[11px] font-semibold">Limitée</span>
                      <span v-else class="text-red-600 text-[11px] font-semibold">Insuffisante</span>
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
      <footer class="w-full py-4 mt-auto border-t border-outline-variant bg-white/50 flex flex-col md:flex-row justify-between items-center px-[32px] gap-3">
        <span class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">EFREI — Solution Delivery — Filière Data — 2025-2026</span>
        <div class="flex items-center gap-6">
          <a class="text-[9px] font-bold text-slate-400 hover:text-primary transition-all uppercase tracking-widest" href="#">Documentation</a>
          <a class="text-[9px] font-bold text-slate-400 hover:text-primary transition-all uppercase tracking-widest" href="#">Architecture</a>
          <a class="text-[9px] font-bold text-slate-400 hover:text-primary transition-all uppercase tracking-widest" href="#">Protocole d'évaluation</a>
        </div>
        <span class="text-[9px] text-slate-400 font-semibold">Ce prototype n'est pas un dispositif médical.</span>
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
          <h3 class="page-title-font font-extrabold text-base">Sortie JSON brute</h3>
          <button @click="showJson = false"
            class="w-8 h-8 rounded-full hover:bg-slate-100 flex items-center justify-center transition-all">
            <span class="material-symbols-outlined text-lg">close</span>
          </button>
        </div>
        <pre class="p-6 overflow-auto text-[12px] font-mono text-slate-700 leading-relaxed flex-1 bg-slate-50">{{ JSON.stringify(currentResult, null, 2) }}</pre>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { auth } from '../store/auth.js'
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
const currentMode   = ref('baseline')
const currentModel  = ref('medgemma_4b_pt')
const currentResult = ref(null)
const history       = ref([])
const showJson      = ref(false)

// ── Auth ──
const userInitials = computed(() => {
  const name = auth.user?.name ?? 'EF'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
})
function logout() { auth.logout(); router.push('/login') }

// ── Mode ──
function setMode(mode) { currentMode.value = mode }

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
    previewUrl.value = e.target.result
    hasResults.value = true
    runAnalysis(file)
  }
  reader.readAsDataURL(file)
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
async function runAnalysis(file) {
  isAnalyzing.value  = true
  analyzeError.value = ''
  currentResult.value = null

  try {
    const form = new FormData()
    form.append('image', file)
    form.append('mode', currentMode.value === 'baseline' ? 'toy' : 'improved')
    form.append('model_key', currentModel.value)

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
  if (q === 'good')    return '<span class="material-symbols-outlined text-sm">check_circle</span> Bonne'
  if (q === 'limited') return '<span class="material-symbols-outlined text-sm">warning</span> Limitée'
  return '<span class="material-symbols-outlined text-sm">error</span> Insuffisante'
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
  if (p === 'normal')            return 'Normal'
  if (p === 'suspected_opacity') return 'Opacité suspectée'
  return 'Incertain'
})
const classLabelClass = computed(() => {
  const p = currentResult.value?.predicted_class
  if (p === 'normal')            return 'page-title-font text-xl font-extrabold text-emerald-700'
  if (p === 'suspected_opacity') return 'page-title-font text-xl font-extrabold text-amber-700'
  return 'page-title-font text-xl font-extrabold text-slate-600'
})

function onKeydown(e) { if (e.key === 'Escape') showJson.value = false }
</script>
