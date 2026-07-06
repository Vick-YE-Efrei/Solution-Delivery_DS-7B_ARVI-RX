<template>
  <div class="layout">

    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <img src="/ravi-logo.png" alt="Logo RaVI" class="brand-logo" />
        <span>RaVI Admin</span>
      </div>
      <nav class="sidebar-nav">
        <a href="#" class="slink" :class="{ active: section === 'overview' }" @click.prevent="section = 'overview'">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/><rect x="9" y="1" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/><rect x="1" y="9" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/><rect x="9" y="9" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/></svg>
          Vue d'ensemble
        </a>
        <a href="#" class="slink" :class="{ active: section === 'users' }" @click.prevent="section = 'users'">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="6" cy="5" r="3" stroke="currentColor" stroke-width="1.4"/><path d="M1 14c0-3 2-5 5-5s5 2 5 5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><path d="M12 7c1.7 0 3 1.3 3 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><circle cx="12" cy="4" r="2" stroke="currentColor" stroke-width="1.4"/></svg>
          Utilisateurs
        </a>
        <a href="#" class="slink" :class="{ active: section === 'analyses' }" @click.prevent="section = 'analyses'">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 12h2l2-5 3 8 2-6 1 3h2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
          Historique analyses
        </a>
        <a href="#" class="slink" :class="{ active: section === 'perf' }" @click.prevent="section = 'perf'">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.4"/><path d="M8 5v3.5l2.5 1.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
          Performances
        </a>
        <div style="height:1px;background:#1e293b;margin:8px 0"></div>
        <router-link to="/guide" class="slink" style="text-decoration:none">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="2" y="1" width="10" height="14" rx="1.5" stroke="currentColor" stroke-width="1.4"/><path d="M5 5h6M5 8h6M5 11h4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
          Guide d'utilisation
        </router-link>
        <router-link to="/about" class="slink" style="text-decoration:none">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.4"/><path d="M8 7v5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><circle cx="8" cy="4.5" r="0.8" fill="currentColor"/></svg>
          À propos
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="admin-info">
          <div class="admin-avatar">{{ auth.user?.name?.[0]?.toUpperCase() ?? 'A' }}</div>
          <div>
            <p class="admin-name">{{ auth.user?.name ?? 'Admin' }}</p>
            <p class="admin-role">Administrateur</p>
          </div>
        </div>
        <button class="logout-btn" @click="logout">
          <span class="material-symbols-outlined" style="font-size:15px;vertical-align:middle;margin-right:6px;">logout</span>
          Déconnexion
        </button>
      </div>
    </aside>

    <!-- Contenu -->
    <div class="content">

      <!-- ── LOADING ── -->
      <div v-if="isLoading" style="display:flex;align-items:center;justify-content:center;height:60vh;color:#9ca3af;font-size:14px;gap:10px;">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style="animation:spin 1s linear infinite">
          <circle cx="10" cy="10" r="8" stroke="#e5e7eb" stroke-width="2.5"/>
          <path d="M10 2a8 8 0 0 1 8 8" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        Chargement des données...
      </div>

      <!-- ── VUE D'ENSEMBLE ── -->
      <section v-else-if="section === 'overview'">
        <div class="page-head">
          <h1 class="page-title">Vue d'ensemble</h1>
          <p class="page-sub">Tableau de bord — {{ today }}</p>
        </div>
        <div class="stats-grid">
          <div class="stat-card">
            <p class="stat-label">Utilisateurs inscrits</p>
            <p class="stat-val">{{ stats.totalUsers }}</p>
            <p class="stat-note">{{ users.filter(u => u.role === 'user').length }} utilisateurs, {{ users.filter(u => u.role === 'admin').length }} admins</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">Analyses effectuées</p>
            <p class="stat-val">{{ stats.totalAnalyses }}</p>
            <p class="stat-note">Confiance moy. {{ stats.avgConfidence }}%</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">Confiance moyenne</p>
            <p class="stat-val">{{ stats.avgConfidence }}%</p>
            <p class="stat-note">Sur {{ stats.totalAnalyses }} analyses</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">Taux d'incertitude</p>
            <p class="stat-val">{{ stats.uncertainRate }}%</p>
            <p class="stat-note">Classe uncertain retournée</p>
          </div>
        </div>

        <div class="overview-row">
          <div class="card">
            <h2 class="card-title">Répartition des classes</h2>
            <div class="dist-bars">
              <div v-for="item in distribution" :key="item.label" class="dist-row">
                <span class="dist-label">{{ item.label }}</span>
                <div class="dist-track">
                  <div class="dist-fill" :style="{ width: item.pct + '%', background: item.color }"></div>
                </div>
                <span class="dist-pct">{{ item.pct }}%</span>
              </div>
            </div>
          </div>

          <div class="card">
            <h2 class="card-title">Activité récente</h2>
            <ul class="activity-list">
              <li v-for="act in recentActivity" :key="act.id" class="activity-item">
                <div class="act-avatar">{{ act.user[0].toUpperCase() }}</div>
                <div class="act-info">
                  <span class="act-user">{{ act.user }}</span>
                  <span class="act-action">a lancé une analyse</span>
                  <span :class="['act-badge', `badge--${act.result}`]">{{ classLabel(act.result) }}</span>
                </div>
                <span class="act-time">{{ act.time }}</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <!-- ── UTILISATEURS ── -->
      <section v-else-if="section === 'users'">
        <div class="page-head">
          <h1 class="page-title">Utilisateurs</h1>
          <p class="page-sub">{{ users.length }} comptes enregistrés</p>
        </div>
        <div class="card">
          <div class="table-toolbar">
            <input v-model="userSearch" class="search-input" placeholder="Rechercher un utilisateur…" />
          </div>
          <table class="data-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>E-mail</th>
                <th>Rôle</th>
                <th>Analyses</th>
                <th>Inscrit le</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in filteredUsers" :key="u.id">
                <td>
                  <div class="user-cell">
                    <div class="user-av">{{ u.name[0].toUpperCase() }}</div>
                    {{ u.name }}
                  </div>
                </td>
                <td class="text-soft">{{ u.email }}</td>
                <td>
                  <span class="role-badge" :class="u.role === 'admin' ? 'role-admin' : 'role-user'">
                    {{ u.role }}
                  </span>
                </td>
                <td class="text-center">{{ u.analysisCount }}</td>
                <td class="text-soft">{{ u.createdAt }}</td>
                <td>
                  <button class="action-btn" @click="viewUserHistory(u)">Historique</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ── HISTORIQUE ANALYSES ── -->
      <section v-else-if="section === 'analyses'">
        <div class="page-head">
          <h1 class="page-title">
            <span v-if="!selectedUser">Toutes les analyses</span>
            <span v-else>
              Analyses de {{ selectedUser.name }}
              <button class="back-btn" @click="selectedUser = null">← Retour</button>
            </span>
          </h1>
          <p class="page-sub">{{ filteredAnalyses.length }} analyses</p>
        </div>
        <div class="card">
          <div class="table-toolbar">
            <input v-model="analysisSearch" class="search-input" placeholder="Rechercher…" />
            <select v-model="analysisFilter" class="filter-select">
              <option value="">Toutes les classes</option>
              <option value="normal">Normal</option>
              <option value="suspected_opacity">Opacité suspectée</option>
              <option value="uncertain">Incertain</option>
            </select>
          </div>
          <table class="data-table">
            <thead>
              <tr>
                <th>Utilisateur</th>
                <th>Date</th>
                <th>Mode</th>
                <th>Résultat</th>
                <th>Confiance</th>
                <th>Seuil</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in filteredAnalyses" :key="a.id">
                <td>
                  <div class="user-cell">
                    <div class="user-av small">{{ a.userName[0].toUpperCase() }}</div>
                    {{ a.userName }}
                  </div>
                </td>
                <td class="text-soft">{{ a.date }}</td>
                <td>
                  <span class="mode-chip">{{ a.mode }}</span>
                </td>
                <td>
                  <span :class="['result-chip', `chip--${a.prediction}`]">
                    {{ classLabel(a.prediction) }}
                  </span>
                </td>
                <td>
                  <div class="conf-bar-wrap">
                    <div class="conf-bar" :style="{ width: (a.confidence * 100) + '%' }"></div>
                    <span class="conf-txt">{{ (a.confidence * 100).toFixed(0) }}%</span>
                  </div>
                </td>
                <td class="text-soft text-center">{{ (a.threshold * 100).toFixed(0) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ── PERFORMANCES ── -->
      <section v-else-if="section === 'perf'">
        <div class="page-head">
          <h1 class="page-title">Performances du modèle</h1>
          <p class="page-sub">Métriques calculées sur {{ perfData.total }} analyses réelles</p>
        </div>

        <div v-if="perfData.total === 0" style="text-align:center;padding:60px;color:#9ca3af;font-size:14px;">
          Aucune analyse enregistrée pour le moment. Lancez des analyses pour voir les métriques.
        </div>

        <div v-else class="perf-grid">
          <div class="card">
            <h2 class="card-title">Métriques globales</h2>
            <div class="metric-list">
              <div v-for="m in perfData.metrics" :key="m.name" class="metric-row">
                <div class="metric-info">
                  <span class="metric-name">{{ m.name }}</span>
                  <span class="metric-val">{{ m.value }}</span>
                </div>
                <div class="metric-track">
                  <div class="metric-fill" :style="{ width: m.pct + '%', background: m.color }"></div>
                </div>
              </div>
            </div>
          </div>

          <div class="card">
            <h2 class="card-title">Baseline vs Amélioré</h2>
            <table class="perf-table">
              <thead>
                <tr><th>Métrique</th><th>Baseline</th><th>Amélioré</th><th>Delta</th></tr>
              </thead>
              <tbody>
                <tr v-for="r in perfData.comparison" :key="r.metric">
                  <td>{{ r.metric }}</td>
                  <td class="text-center">{{ r.baseline }}</td>
                  <td class="text-center">{{ r.improved }}</td>
                  <td class="text-center">
                    <span :class="r.delta > 0 ? 'delta-pos' : r.delta < 0 ? 'delta-neg' : ''">
                      {{ r.delta > 0 ? '+' : '' }}{{ r.delta }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="card card--full">
            <h2 class="card-title">Répartition par modèle</h2>
            <table class="perf-table">
              <thead>
                <tr><th>Modèle</th><th>Analyses</th><th>Confiance moy.</th></tr>
              </thead>
              <tbody>
                <tr v-for="m in perfData.byModel" :key="m.model_name">
                  <td style="font-family:monospace;font-size:12px">{{ m.model_name }}</td>
                  <td class="text-center">{{ m.count }}</td>
                  <td class="text-center">{{ m.avg_conf }}%</td>
                </tr>
                <tr v-if="!perfData.byModel.length">
                  <td colspan="3" style="text-align:center;color:#9ca3af;padding:16px">Aucune donnée</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { auth } from '../store/auth.js'
const raviLogo = '/ravi-logo.png'

const router  = useRouter()
const section = ref('overview')
const today   = new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
const isLoading = ref(true)

function logout() { auth.logout(); router.push('/login') }
function classLabel(pred) {
  return { normal: 'Normal', suspected_opacity: 'Opacité', uncertain: 'Incertain' }[pred] ?? pred
}
function fmt(iso) {
  return new Date(iso).toLocaleString('fr-FR', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}
function timeAgo(iso) {
  const diff = Math.floor((Date.now() - new Date(iso)) / 1000)
  if (diff < 60)   return `il y a ${diff}s`
  if (diff < 3600) return `il y a ${Math.floor(diff/60)}min`
  if (diff < 86400) return `il y a ${Math.floor(diff/3600)}h`
  return `il y a ${Math.floor(diff/86400)}j`
}

// ── State ──
const stats         = ref({ totalUsers: 0, totalAnalyses: 0, uncertainRate: 0, avgConfidence: 0, avgLatency: 0 })
const distribution  = ref([])
const recentActivity = ref([])
const users         = ref([])
const allAnalyses   = ref([])
const byModel       = ref([])

// ── Chargement ──
onMounted(async () => {
  try {
    const [usersRes, analysesRes, statsRes] = await Promise.all([
      axios.get('/api/users'),
      axios.get('/api/analyses'),
      axios.get('/api/analyses/stats'),
    ])

    // Utilisateurs
    users.value = usersRes.data.map(u => ({
      id:            u.id,
      name:          u.name,
      email:         u.email,
      role:          u.role,
      analysisCount: u.analysis_count,
      createdAt:     new Date(u.created_at).toLocaleDateString('fr-FR'),
    }))

    // Analyses
    allAnalyses.value = analysesRes.data.map(a => ({
      id:         a.id,
      userId:     a.user_id,
      userName:   a.user_name,
      date:       fmt(a.created_at),
      mode:       a.mode,
      prediction: a.predicted_class,
      confidence: a.confidence,
      threshold:  a.threshold ?? 0.70,
      modelName:  a.model_name,
      latency:    a.latency_ms,
    }))

    // Stats globales
    const s = statsRes.data.analyses
    const u = statsRes.data.users
    const total = s.total || 0
    stats.value = {
      totalUsers:    u.total,
      totalAnalyses: total,
      uncertainRate: total ? +((s.uncertain_count / total) * 100).toFixed(1) : 0,
      avgConfidence: s.avg_confidence ?? 0,
      avgLatency:    Math.round(s.avg_latency_ms ?? 0),
    }

    // Distribution réelle
    if (total > 0) {
      distribution.value = [
        { label: 'Normal',            pct: +((s.normal_count  / total) * 100).toFixed(1), color: '#16a34a', count: s.normal_count },
        { label: 'Opacité suspectée', pct: +((s.opacity_count / total) * 100).toFixed(1), color: '#c2410c', count: s.opacity_count },
        { label: 'Incertain',         pct: +((s.uncertain_count / total) * 100).toFixed(1), color: '#d97706', count: s.uncertain_count },
      ]
    }

    // Par modèle
    byModel.value = statsRes.data.by_model ?? []

    // Activité récente (5 dernières analyses)
    recentActivity.value = analysesRes.data.slice(0, 5).map(a => ({
      id:     a.id,
      user:   a.user_name,
      result: a.predicted_class,
      time:   timeAgo(a.created_at),
    }))

  } catch (e) {
    console.error('Erreur chargement admin:', e.message)
  } finally {
    isLoading.value = false
  }
})

// ── Utilisateurs filtrés ──
const userSearch = ref('')
const filteredUsers = computed(() =>
  users.value.filter(u =>
    u.name.toLowerCase().includes(userSearch.value.toLowerCase()) ||
    u.email.toLowerCase().includes(userSearch.value.toLowerCase())
  )
)

// ── Analyses filtrées ──
const selectedUser   = ref(null)
const analysisSearch = ref('')
const analysisFilter = ref('')

function viewUserHistory(u) {
  selectedUser.value = u
  section.value = 'analyses'
}

const filteredAnalyses = computed(() => {
  let list = selectedUser.value
    ? allAnalyses.value.filter(a => a.userId === selectedUser.value.id)
    : allAnalyses.value
  if (analysisSearch.value)
    list = list.filter(a => (a.userName ?? '').toLowerCase().includes(analysisSearch.value.toLowerCase()))
  if (analysisFilter.value)
    list = list.filter(a => a.prediction === analysisFilter.value)
  return list
})

// ── Performances calculées depuis les vraies données ──
const perfData = computed(() => {
  const list = allAnalyses.value
  const total = list.length
  if (total === 0) return { total: 0, metrics: [], comparison: [], byModel: [] }

  const baseline = list.filter(a => a.mode === 'toy' || a.mode === 'baseline')
  const improved = list.filter(a => a.mode === 'improved')

  const avgConf = arr => arr.length ? +(arr.reduce((s, a) => s + a.confidence, 0) / arr.length * 100).toFixed(1) : 0
  const uncertainPct = arr => arr.length ? +((arr.filter(a => a.prediction === 'uncertain').length / arr.length) * 100).toFixed(1) : 0
  const avgLat = arr => arr.length ? Math.round(arr.reduce((s, a) => s + (a.latency ?? 0), 0) / arr.length) : 0

  const globalConf = avgConf(list)
  const globalUncert = uncertainPct(list)
  const globalLat = avgLat(list)

  return {
    total,
    metrics: [
      { name: 'Confiance moyenne',         value: globalConf + '%',  pct: globalConf,              color: '#2563eb' },
      { name: 'Taux normal',               value: distribution.value[0]?.pct + '%' ?? '–', pct: distribution.value[0]?.pct ?? 0, color: '#16a34a' },
      { name: 'Taux opacité suspectée',    value: distribution.value[1]?.pct + '%' ?? '–', pct: distribution.value[1]?.pct ?? 0, color: '#c2410c' },
      { name: 'Taux incertitude',          value: globalUncert + '%', pct: globalUncert,            color: '#d97706' },
      { name: 'Latence moyenne',           value: globalLat + ' ms',  pct: Math.min(globalLat / 50, 100), color: '#0ea5e9' },
    ],
    comparison: [
      {
        metric:   'Confiance moy.',
        baseline: avgConf(baseline) + '%',
        improved: avgConf(improved) + '%',
        delta:    +(avgConf(improved) - avgConf(baseline)).toFixed(1),
      },
      {
        metric:   'Taux incertitude',
        baseline: uncertainPct(baseline) + '%',
        improved: uncertainPct(improved) + '%',
        delta:    +(uncertainPct(improved) - uncertainPct(baseline)).toFixed(1),
      },
      {
        metric:   'Nb analyses',
        baseline: baseline.length,
        improved: improved.length,
        delta:    improved.length - baseline.length,
      },
    ],
    byModel: byModel.value,
  }
})
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  font-family: 'Inter', system-ui, sans-serif;
  background: #f1f5f9;
}

/* ── Sidebar ── */
.sidebar {
  width: 220px;
  background: #0f172a;
  color: #f9fafb;
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  gap: 8px;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 0 6px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  font-size: 13.5px;
  font-weight: 700;
  color: #e5e7eb;
  letter-spacing: -0.01em;
}
.brand-logo {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: #ffffff;
  object-fit: contain;
  padding: 3px;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.12);
  flex-shrink: 0;
}
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  padding-top: 8px;
}
.slink {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 7px;
  text-decoration: none;
  font-size: 13.5px;
  color: #9ca3af;
  transition: background 0.15s, color 0.15s;
}
.slink:hover  { background: rgba(255,255,255,0.06); color: #e5e7eb; }
.slink.active { background: rgba(59,130,246,0.18); color: #93c5fd; }

.sidebar-footer {
  border-top: 1px solid rgba(255,255,255,0.08);
  padding-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.admin-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.admin-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: #2563eb;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}
.admin-name { font-size: 13px; font-weight: 600; color: #e5e7eb; }
.admin-role { font-size: 11px; color: #6b7280; }
.logout-btn {
  width: 100%;
  padding: 8px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px;
  color: #9ca3af;
  font-size: 12.5px;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.logout-btn:hover { background: rgba(239,68,68,0.12); border-color: rgba(239,68,68,0.25); color: #f87171; }

/* ── Contenu ── */
.content {
  flex: 1;
  padding: 36px 40px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.page-head { display: flex; flex-direction: column; gap: 4px; }
.page-title {
  font-family: 'Manrope', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.02em;
  display: flex;
  align-items: center;
  gap: 12px;
}
.page-sub { font-size: 13px; color: #6b7280; }
.back-btn {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: #2563eb;
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: underline;
}

/* ── Stats ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.stat-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px 22px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stat-label { font-size: 11.5px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 8px; }
.stat-val   { font-size: 30px; font-weight: 700; color: #0f172a; font-family: 'Manrope', sans-serif; letter-spacing: -0.03em; line-height: 1; margin-bottom: 6px; }
.stat-note  { font-size: 12px; color: #9ca3af; }

/* ── Card ── */
.card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.card-title {
  font-family: 'Manrope', sans-serif;
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 18px;
}

/* ── Overview row ── */
.overview-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* ── Dist bars ── */
.dist-bars { display: flex; flex-direction: column; gap: 14px; }
.dist-row  { display: flex; align-items: center; gap: 12px; }
.dist-label { font-size: 13px; color: #374151; min-width: 120px; }
.dist-track { flex: 1; height: 8px; background: #f1f5f9; border-radius: 99px; overflow: hidden; }
.dist-fill  { height: 100%; border-radius: 99px; transition: width 0.6s ease; }
.dist-pct   { font-size: 12px; font-weight: 600; color: #6b7280; min-width: 32px; text-align: right; }

/* ── Activity ── */
.activity-list { display: flex; flex-direction: column; gap: 0; }
.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 0;
  border-bottom: 1px solid #f1f5f9;
}
.activity-item:last-child { border-bottom: none; }
.act-avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: #ede9fe;
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.act-info { flex: 1; font-size: 13px; color: #374151; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.act-user   { font-weight: 600; }
.act-action { color: #6b7280; }
.act-badge  { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 99px; }
.badge--normal            { background: #ecfdf5; color: #065f46; }
.badge--suspected_opacity { background: #fff7ed; color: #9a3412; }
.badge--uncertain         { background: #fffbeb; color: #78350f; }
.act-time { font-size: 11.5px; color: #9ca3af; white-space: nowrap; flex-shrink: 0; }

/* ── Table ── */
.table-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}
.search-input {
  flex: 1;
  padding: 9px 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13.5px;
  font-family: 'Inter', system-ui, sans-serif;
  color: #0f172a;
  background: #f8fafc;
  outline: none;
  transition: border-color 0.15s;
}
.search-input:focus { border-color: #2563eb; }
.filter-select {
  padding: 9px 12px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  font-family: 'Inter', system-ui, sans-serif;
  color: #0f172a;
  background: #f8fafc;
  outline: none;
  cursor: pointer;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
}
.data-table th {
  text-align: left;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #9ca3af;
  padding: 0 12px 10px;
  border-bottom: 1px solid #e2e8f0;
}
.data-table td {
  padding: 12px;
  border-bottom: 1px solid #f1f5f9;
  color: #374151;
  vertical-align: middle;
}
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #f8fafc; }
.text-soft { color: #6b7280; }
.text-center { text-align: center; }

.user-cell { display: flex; align-items: center; gap: 8px; font-weight: 500; }
.user-av {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: #ede9fe;
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.user-av.small { width: 24px; height: 24px; font-size: 10px; }

.role-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 9px;
  border-radius: 99px;
}
.role-admin { background: #ede9fe; color: #2563eb; }
.role-user  { background: #f1f5f9; color: #6b7280; }

.action-btn {
  font-size: 12.5px;
  color: #2563eb;
  background: #ede9fe;
  border: none;
  border-radius: 6px;
  padding: 5px 12px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.15s;
}
.action-btn:hover { background: #ddd6fe; }

.mode-chip {
  font-size: 11.5px;
  background: #f1f5f9;
  color: #6b7280;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}
.result-chip {
  font-size: 11.5px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 99px;
}
.chip--normal            { background: #ecfdf5; color: #065f46; }
.chip--suspected_opacity { background: #fff7ed; color: #9a3412; }
.chip--uncertain         { background: #fffbeb; color: #78350f; }

.conf-bar-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}
.conf-bar {
  height: 5px;
  background: #2563eb;
  border-radius: 99px;
  max-width: 80px;
  min-width: 4px;
  transition: width 0.3s;
}
.conf-txt { font-size: 12px; color: #6b7280; min-width: 30px; }

/* ── Perf ── */
.perf-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.card--full { grid-column: 1 / -1; }

.metric-list { display: flex; flex-direction: column; gap: 16px; }
.metric-row  { display: flex; flex-direction: column; gap: 6px; }
.metric-info { display: flex; justify-content: space-between; align-items: baseline; }
.metric-name { font-size: 13.5px; color: #374151; }
.metric-val  { font-size: 14px; font-weight: 700; color: #0f172a; }
.metric-track { height: 6px; background: #f1f5f9; border-radius: 99px; overflow: hidden; }
.metric-fill  { height: 100%; border-radius: 99px; transition: width 0.6s ease; }

.perf-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
}
.perf-table th {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #9ca3af;
  padding: 0 12px 10px;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
}
.perf-table td {
  padding: 11px 12px;
  border-bottom: 1px solid #f1f5f9;
  color: #374151;
}
.perf-table tr:last-child td { border-bottom: none; }
.delta-pos { color: #065f46; font-weight: 600; }
.delta-neg { color: #9a3412; font-weight: 600; }

/* ── Matrice de confusion ── */
.matrix-wrap { overflow-x: auto; }
.matrix-table {
  border-collapse: collapse;
  font-size: 13.5px;
  width: 100%;
}
.matrix-table th {
  padding: 10px 16px;
  font-size: 12px;
  font-weight: 700;
  color: #6b7280;
  text-align: center;
  border-bottom: 1px solid #e2e8f0;
}
.matrix-table th:first-child { text-align: left; }
.matrix-table tr th:first-child {
  text-align: left;
  font-size: 13px;
  color: #374151;
  padding: 12px 16px;
  border-bottom: none;
  border-right: 1px solid #e2e8f0;
}
.matrix-cell {
  padding: 14px 16px;
  text-align: center;
  color: #374151;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  font-size: 15px;
}
.matrix-correct {
  padding: 14px 16px;
  text-align: center;
  background: #ede9fe;
  color: #2563eb;
  font-weight: 700;
  font-size: 15px;
  border: 1px solid #ddd6fe;
}
</style>
