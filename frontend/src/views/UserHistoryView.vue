<template>
  <div class="layout">

    <!-- Header -->
    <header class="header">
      <div class="header-inner">
        <div class="header-brand">
          <div class="brand-dot"></div>
          <h1 class="brand-title">Assistant Radiologue Virtuel</h1>
        </div>
        <nav class="nav">
          <router-link to="/" class="nav-link">Nouvelle analyse</router-link>
          <router-link to="/history" class="nav-link active">Mon historique</router-link>
          <button class="nav-logout" @click="logout">Déconnexion</button>
        </nav>
      </div>
    </header>

    <main class="main">

      <div class="page-head">
        <div>
          <h2 class="page-title">Mes analyses</h2>
          <p class="page-sub">{{ userName }} — {{ analyses.length }} analyses effectuées</p>
        </div>
        <router-link to="/" class="btn-new">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M3 2.5l10 5.5-10 5.5V2.5z" fill="currentColor"/>
          </svg>
          Nouvelle analyse
        </router-link>
      </div>

      <!-- Résumé rapide -->
      <div class="summary-row">
        <div class="summary-card">
          <p class="s-label">Total</p>
          <p class="s-val">{{ analyses.length }}</p>
        </div>
        <div class="summary-card">
          <p class="s-label">Normal</p>
          <p class="s-val green">{{ countByClass('normal') }}</p>
        </div>
        <div class="summary-card">
          <p class="s-label">Opacité suspectée</p>
          <p class="s-val orange">{{ countByClass('suspected_opacity') }}</p>
        </div>
        <div class="summary-card">
          <p class="s-label">Incertain</p>
          <p class="s-val amber">{{ countByClass('uncertain') }}</p>
        </div>
      </div>

      <!-- Filtres -->
      <div class="filters">
        <select v-model="filter" class="filter-select">
          <option value="">Toutes les classes</option>
          <option value="normal">Normal</option>
          <option value="suspected_opacity">Opacité suspectée</option>
          <option value="uncertain">Incertain</option>
        </select>
        <select v-model="modeFilter" class="filter-select">
          <option value="">Tous les modes</option>
          <option value="baseline">Baseline</option>
          <option value="improved">Amélioré</option>
        </select>
      </div>

      <!-- Liste des analyses -->
      <div class="analyses-list">
        <div v-if="filteredAnalyses.length === 0" class="empty-state">
          Aucune analyse ne correspond aux filtres.
        </div>

        <div v-for="a in filteredAnalyses" :key="a.id" class="analysis-card" @click="selected = selected?.id === a.id ? null : a">

          <div class="ac-left">
            <div class="ac-index">#{{ a.id }}</div>
            <div class="ac-thumb">
              <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                <rect width="28" height="28" rx="6" fill="#f4f3ef"/>
                <path d="M5 14h5l3-6 4 12 3-7 2 4h1" stroke="#9ca3af" stroke-width="1.5"
                      stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="ac-meta">
              <span :class="['ac-result', `res--${a.prediction}`]">{{ classLabel(a.prediction) }}</span>
              <span class="ac-date">{{ a.date }}</span>
            </div>
          </div>

          <div class="ac-right">
            <span class="mode-chip">{{ a.mode }}</span>
            <div class="conf-wrap">
              <div class="conf-bar" :style="{ width: (a.confidence * 100) + '%' }"></div>
              <span class="conf-txt">{{ (a.confidence * 100).toFixed(0) }}%</span>
            </div>
            <svg class="chevron" :class="{ open: selected?.id === a.id }"
                 width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M3 5l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>

        </div>

        <!-- Détail -->
        <transition name="slide">
          <div v-if="selected" class="detail-panel">
            <div class="detail-grid">
              <div class="detail-block">
                <p class="detail-label">Qualité image</p>
                <p class="detail-val">{{ selected.imageQuality }}</p>
              </div>
              <div class="detail-block">
                <p class="detail-label">Justification</p>
                <p class="detail-val">{{ selected.justification }}</p>
              </div>
              <div class="detail-block detail-block--full">
                <p class="detail-label">Observations visuelles</p>
                <ul class="detail-obs">
                  <li v-for="(o, i) in selected.observations" :key="i">{{ o }}</li>
                </ul>
              </div>
              <div class="detail-block detail-block--full detail-block--warn">
                <p class="detail-label">Limites</p>
                <p class="detail-val">{{ selected.limitations }}</p>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </main>

    <footer class="footer">
      Projet personnel · EFREI Paris · 2025-2026
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../store/auth.js'

const router   = useRouter()
const filter   = ref('')
const modeFilter = ref('')
const selected = ref(null)
const userName = auth.user?.name ?? 'Utilisateur'

function logout() {
  auth.logout()
  router.push('/login')
}

function classLabel(pred) {
  return { normal: 'Normal', suspected_opacity: 'Opacité suspectée', uncertain: 'Incertain' }[pred] ?? pred
}
function countByClass(cls) {
  return analyses.value.filter(a => a.prediction === cls).length
}

const analyses = ref([
  {
    id: 7, date: '25 juin 2026 14:32', mode: 'improved',
    prediction: 'normal', confidence: 0.87, threshold: 0.70,
    imageQuality: 'Bonne qualité — exposition correcte, pas d\'artefact notable.',
    justification: 'Les champs pulmonaires apparaissent clairs, sans opacité focale identifiable.',
    observations: ['Champs pulmonaires symétriques', 'Silhouette cardiaque normale', 'Pas d\'épanchement pleural visible'],
    limitations: 'Analyse limitée à une vue frontale. Toute anomalie subtile peut être manquée sans vue de profil.'
  },
  {
    id: 6, date: '24 juin 2026 11:05', mode: 'baseline',
    prediction: 'suspected_opacity', confidence: 0.74, threshold: 0.70,
    imageQuality: 'Qualité satisfaisante — légère rotation du patient.',
    justification: 'Zone de densification au lobe inférieur droit compatible avec une consolidation.',
    observations: ['Opacité lobe inférieur droit', 'Bronchogramme aérique possible', 'Pas d\'épanchement majeur'],
    limitations: 'Prototype pédagogique. Un scanner CT et avis radiologique sont indispensables.'
  },
  {
    id: 5, date: '22 juin 2026 16:44', mode: 'improved',
    prediction: 'uncertain', confidence: 0.61, threshold: 0.70,
    imageQuality: 'Qualité limitée — sous-exposition partielle.',
    justification: 'Confiance inférieure au seuil défini. Résultat non concluant.',
    observations: ['Image partiellement sous-exposée', 'Structures médiastinales peu visibles', 'Champ droit difficile à évaluer'],
    limitations: 'Image de qualité insuffisante pour une analyse fiable. Une nouvelle acquisition est recommandée.'
  },
  {
    id: 4, date: '20 juin 2026 09:18', mode: 'baseline',
    prediction: 'normal', confidence: 0.92, threshold: 0.70,
    imageQuality: 'Excellente qualité — exposition optimale.',
    justification: 'Aucune anomalie décelable sur les champs pulmonaires.',
    observations: ['Poumons clairs', 'Index cardiothoracique dans les normes', 'Coupoles diaphragmatiques régulières'],
    limitations: 'Prototype pédagogique. Résultat expérimental non validé cliniquement.'
  }
])

const filteredAnalyses = computed(() => {
  let list = analyses.value
  if (filter.value)     list = list.filter(a => a.prediction === filter.value)
  if (modeFilter.value) list = list.filter(a => a.mode === modeFilter.value)
  return list
})
</script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f4f3ef;
  font-family: system-ui, sans-serif;
  color: #0d0d0d;
}

/* ── Header ── */
.header {
  background: #111111;
  position: sticky;
  top: 0;
  z-index: 10;
}
.header-inner {
  max-width: 1000px;
  margin: 0 auto;
  padding: 18px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.header-brand { display: flex; align-items: center; gap: 10px; }
.brand-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #7c3aed;
  box-shadow: 0 0 8px rgba(124,58,237,0.7);
}
.brand-title {
  font-family: 'Georgia', serif;
  font-size: 15px;
  font-weight: 700;
  color: #f9fafb;
}
.nav { display: flex; align-items: center; gap: 4px; }
.nav-link {
  text-decoration: none;
  font-size: 13.5px;
  color: #9ca3af;
  padding: 6px 12px;
  border-radius: 6px;
  transition: background 0.15s, color 0.15s;
}
.nav-link:hover, .nav-link.active {
  color: #f9fafb;
  background: rgba(255,255,255,0.08);
}
.nav-logout {
  background: none;
  border: none;
  font-size: 13.5px;
  color: #9ca3af;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 6px;
  transition: background 0.15s, color 0.15s;
}
.nav-logout:hover { color: #f9fafb; background: rgba(255,255,255,0.08); }

/* ── Main ── */
.main {
  flex: 1;
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
  padding: 36px 28px 48px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}
.page-title {
  font-family: 'Georgia', serif;
  font-size: 24px;
  font-weight: 700;
  color: #0d0d0d;
  letter-spacing: -0.02em;
}
.page-sub { font-size: 13px; color: #6b7280; margin-top: 4px; }

.btn-new {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: #111111;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  transition: background 0.15s, transform 0.1s;
  white-space: nowrap;
  flex-shrink: 0;
}
.btn-new:hover { background: #1f1f1f; transform: translateY(-1px); }

/* ── Summary ── */
.summary-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.summary-card {
  background: white;
  border: 1px solid #e5e2db;
  border-radius: 10px;
  padding: 16px 18px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.s-label { font-size: 11px; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 6px; }
.s-val   { font-size: 26px; font-weight: 700; font-family: 'Georgia', serif; letter-spacing: -0.02em; color: #0d0d0d; }
.s-val.green  { color: #065f46; }
.s-val.orange { color: #9a3412; }
.s-val.amber  { color: #78350f; }

/* ── Filtres ── */
.filters { display: flex; gap: 10px; }
.filter-select {
  padding: 9px 12px;
  border: 1.5px solid #e5e2db;
  border-radius: 8px;
  font-size: 13px;
  font-family: system-ui, sans-serif;
  color: #0d0d0d;
  background: white;
  outline: none;
  cursor: pointer;
  transition: border-color 0.15s;
}
.filter-select:focus { border-color: #5b21b6; }

/* ── Analyses list ── */
.analyses-list { display: flex; flex-direction: column; gap: 0; }
.empty-state {
  text-align: center;
  padding: 48px;
  color: #9ca3af;
  font-size: 14px;
  background: white;
  border: 1px solid #e5e2db;
  border-radius: 12px;
}

.analysis-card {
  background: white;
  border: 1px solid #e5e2db;
  border-bottom: none;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  cursor: pointer;
  transition: background 0.15s;
}
.analysis-card:first-child { border-radius: 12px 12px 0 0; }
.analysis-card:hover { background: #fafaf9; }

.ac-left  { display: flex; align-items: center; gap: 14px; flex: 1; }
.ac-right { display: flex; align-items: center; gap: 16px; flex-shrink: 0; }
.ac-index { font-size: 12px; color: #d1d5db; font-weight: 700; min-width: 24px; }
.ac-thumb { flex-shrink: 0; }
.ac-meta  { display: flex; flex-direction: column; gap: 3px; }

.ac-result {
  font-size: 13.5px;
  font-weight: 700;
}
.res--normal            { color: #065f46; }
.res--suspected_opacity { color: #9a3412; }
.res--uncertain         { color: #78350f; }
.ac-date { font-size: 12px; color: #9ca3af; }

.mode-chip {
  font-size: 11px;
  background: #f4f3ef;
  color: #6b7280;
  padding: 3px 9px;
  border-radius: 4px;
  font-weight: 600;
}
.conf-wrap { display: flex; align-items: center; gap: 8px; }
.conf-bar {
  height: 4px;
  background: #5b21b6;
  border-radius: 99px;
  max-width: 60px;
  min-width: 4px;
}
.conf-txt { font-size: 12px; color: #6b7280; min-width: 28px; }
.chevron { color: #9ca3af; transition: transform 0.2s; }
.chevron.open { transform: rotate(180deg); }

/* ── Détail ── */
.detail-panel {
  background: #fafaf9;
  border: 1px solid #e5e2db;
  border-top: none;
  border-radius: 0 0 12px 12px;
  padding: 20px 24px;
}
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.detail-block { display: flex; flex-direction: column; gap: 5px; }
.detail-block--full { grid-column: 1 / -1; }
.detail-block--warn {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 12px 14px;
}
.detail-label {
  font-size: 10.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #9ca3af;
}
.detail-val { font-size: 13.5px; color: #374151; line-height: 1.65; }
.detail-obs { list-style: none; display: flex; flex-direction: column; gap: 4px; }
.detail-obs li {
  font-size: 13.5px;
  color: #374151;
  padding-left: 14px;
  position: relative;
  line-height: 1.6;
}
.detail-obs li::before { content: '–'; position: absolute; left: 0; color: #9ca3af; }

/* ── Transition ── */
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-6px); }

/* ── Footer ── */
.footer {
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: #9ca3af;
  border-top: 1px solid #e5e2db;
}

@media (max-width: 700px) {
  .summary-row { grid-template-columns: 1fr 1fr; }
  .detail-grid  { grid-template-columns: 1fr; }
  .page-head { flex-direction: column; }
}
</style>
