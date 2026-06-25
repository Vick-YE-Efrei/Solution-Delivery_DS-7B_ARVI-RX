<template>
  <div class="layout">

    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-dot"></div>
        <span>ARV Admin</span>
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
      </nav>
      <div class="sidebar-footer">
        <div class="admin-info">
          <div class="admin-avatar">{{ auth.user?.name?.[0]?.toUpperCase() ?? 'A' }}</div>
          <div>
            <p class="admin-name">{{ auth.user?.name ?? 'Admin' }}</p>
            <p class="admin-role">Administrateur</p>
          </div>
        </div>
        <button class="logout-btn" @click="logout">Déconnexion</button>
      </div>
    </aside>

    <!-- Contenu -->
    <div class="content">

      <!-- ── VUE D'ENSEMBLE ── -->
      <section v-if="section === 'overview'">
        <div class="page-head">
          <h1 class="page-title">Vue d'ensemble</h1>
          <p class="page-sub">Tableau de bord — {{ today }}</p>
        </div>
        <div class="stats-grid">
          <div class="stat-card">
            <p class="stat-label">Utilisateurs inscrits</p>
            <p class="stat-val">{{ stats.totalUsers }}</p>
            <p class="stat-note">+{{ stats.newUsersThisWeek }} cette semaine</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">Analyses effectuées</p>
            <p class="stat-val">{{ stats.totalAnalyses }}</p>
            <p class="stat-note">{{ stats.analysesToday }} aujourd'hui</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">Précision globale</p>
            <p class="stat-val">{{ stats.accuracy }}%</p>
            <p class="stat-note">Sur {{ stats.evaluated }} cas évalués</p>
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
      <section v-if="section === 'users'">
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
      <section v-if="section === 'analyses'">
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
      <section v-if="section === 'perf'">
        <div class="page-head">
          <h1 class="page-title">Performances du modèle</h1>
          <p class="page-sub">Métriques sur {{ perfData.total }} cas évalués</p>
        </div>

        <div class="perf-grid">
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
            <h2 class="card-title">Comparaison Baseline / Amélioré</h2>
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
                    <span :class="r.delta > 0 ? 'delta-pos' : 'delta-neg'">
                      {{ r.delta > 0 ? '+' : '' }}{{ r.delta }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="card card--full">
            <h2 class="card-title">Matrice de confusion (baseline)</h2>
            <div class="matrix-wrap">
              <table class="matrix-table">
                <thead>
                  <tr>
                    <th></th>
                    <th>Prédit : Normal</th>
                    <th>Prédit : Opacité</th>
                    <th>Prédit : Incertain</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in confusionMatrix" :key="row.label">
                    <th>Réel : {{ row.label }}</th>
                    <td v-for="(val, i) in row.vals" :key="i"
                        :class="i === row.correctIdx ? 'matrix-correct' : 'matrix-cell'">
                      {{ val }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../store/auth.js'

const router  = useRouter()
const section = ref('overview')
const today   = new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })

function logout() {
  auth.logout()
  router.push('/login')
}

function classLabel(pred) {
  return { normal: 'Normal', suspected_opacity: 'Opacité', uncertain: 'Incertain' }[pred] ?? pred
}

// ── Données mock ──
const stats = {
  totalUsers: 24, newUsersThisWeek: 3,
  totalAnalyses: 187, analysesToday: 12,
  accuracy: 81.4, evaluated: 120,
  uncertainRate: 14.2
}

const distribution = [
  { label: 'Normal',            pct: 52, color: '#16a34a' },
  { label: 'Opacité suspectée', pct: 34, color: '#c2410c' },
  { label: 'Incertain',         pct: 14, color: '#d97706' }
]

const recentActivity = [
  { id: 1, user: 'Marie Dupont',    result: 'normal',            time: 'il y a 3 min' },
  { id: 2, user: 'Thomas Leroy',    result: 'suspected_opacity', time: 'il y a 11 min' },
  { id: 3, user: 'Aisha Kone',      result: 'uncertain',         time: 'il y a 28 min' },
  { id: 4, user: 'Julien Bernard',  result: 'normal',            time: 'il y a 42 min' },
  { id: 5, user: 'Sara Morin',      result: 'suspected_opacity', time: 'il y a 1h' }
]

const users = ref([
  { id: 1, name: 'Marie Dupont',   email: 'marie@efrei.fr',   role: 'user',  analysisCount: 14, createdAt: '12 juin 2026' },
  { id: 2, name: 'Thomas Leroy',   email: 'thomas@efrei.fr',  role: 'user',  analysisCount: 9,  createdAt: '14 juin 2026' },
  { id: 3, name: 'Aisha Kone',     email: 'aisha@efrei.fr',   role: 'user',  analysisCount: 21, createdAt: '10 juin 2026' },
  { id: 4, name: 'Admin Système',  email: 'admin@efrei.fr',   role: 'admin', analysisCount: 0,  createdAt: '1 juin 2026' },
  { id: 5, name: 'Julien Bernard', email: 'julien@efrei.fr',  role: 'user',  analysisCount: 7,  createdAt: '18 juin 2026' },
  { id: 6, name: 'Sara Morin',     email: 'sara@efrei.fr',    role: 'user',  analysisCount: 31, createdAt: '8 juin 2026' }
])

const userSearch  = ref('')
const filteredUsers = computed(() =>
  users.value.filter(u =>
    u.name.toLowerCase().includes(userSearch.value.toLowerCase()) ||
    u.email.toLowerCase().includes(userSearch.value.toLowerCase())
  )
)

const selectedUser = ref(null)
function viewUserHistory(u) {
  selectedUser.value = u
  section.value = 'analyses'
}

const allAnalyses = [
  { id: 1,  userName: 'Marie Dupont',   date: '25 juin 2026 14:32', mode: 'baseline',  prediction: 'normal',            confidence: 0.87, threshold: 0.70 },
  { id: 2,  userName: 'Thomas Leroy',   date: '25 juin 2026 13:18', mode: 'improved',  prediction: 'suspected_opacity', confidence: 0.76, threshold: 0.70 },
  { id: 3,  userName: 'Aisha Kone',     date: '25 juin 2026 11:05', mode: 'baseline',  prediction: 'uncertain',         confidence: 0.58, threshold: 0.70 },
  { id: 4,  userName: 'Marie Dupont',   date: '24 juin 2026 16:44', mode: 'improved',  prediction: 'normal',            confidence: 0.92, threshold: 0.70 },
  { id: 5,  userName: 'Sara Morin',     date: '24 juin 2026 10:21', mode: 'baseline',  prediction: 'suspected_opacity', confidence: 0.81, threshold: 0.65 },
  { id: 6,  userName: 'Julien Bernard', date: '23 juin 2026 09:55', mode: 'improved',  prediction: 'normal',            confidence: 0.89, threshold: 0.70 },
  { id: 7,  userName: 'Aisha Kone',     date: '22 juin 2026 15:30', mode: 'improved',  prediction: 'suspected_opacity', confidence: 0.74, threshold: 0.70 },
  { id: 8,  userName: 'Thomas Leroy',   date: '21 juin 2026 11:12', mode: 'baseline',  prediction: 'uncertain',         confidence: 0.61, threshold: 0.70 },
]

const analysisSearch = ref('')
const analysisFilter = ref('')

const filteredAnalyses = computed(() => {
  let list = selectedUser.value
    ? allAnalyses.filter(a => a.userName === selectedUser.value.name)
    : allAnalyses
  if (analysisSearch.value)
    list = list.filter(a => a.userName.toLowerCase().includes(analysisSearch.value.toLowerCase()))
  if (analysisFilter.value)
    list = list.filter(a => a.prediction === analysisFilter.value)
  return list
})

const perfData = {
  total: 120,
  metrics: [
    { name: 'Précision (accuracy)', value: '81.4%', pct: 81, color: '#5b21b6' },
    { name: 'F1-score macro',       value: '0.78',  pct: 78, color: '#7c3aed' },
    { name: 'Rappel (recall)',       value: '0.80',  pct: 80, color: '#8b5cf6' },
    { name: 'Précision (precision)', value: '0.77',  pct: 77, color: '#a78bfa' }
  ],
  comparison: [
    { metric: 'Accuracy',     baseline: '74.2%', improved: '81.4%', delta: +7.2 },
    { metric: 'F1 macro',     baseline: '0.71',  improved: '0.78',  delta: +0.07 },
    { metric: 'Taux uncertain', baseline: '22%',  improved: '14%',   delta: -8 }
  ]
}

const confusionMatrix = [
  { label: 'Normal',   vals: [38, 3, 2], correctIdx: 0 },
  { label: 'Opacité',  vals: [4, 31, 6], correctIdx: 1 },
  { label: 'Incertain',vals: [1, 2, 33], correctIdx: 2 }
]
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  font-family: system-ui, sans-serif;
  background: #f4f3ef;
}

/* ── Sidebar ── */
.sidebar {
  width: 220px;
  background: #111111;
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
.brand-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #7c3aed;
  box-shadow: 0 0 8px rgba(124,58,237,0.7);
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
.slink.active { background: rgba(124,58,237,0.18); color: #c4b5fd; }

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
  background: #5b21b6;
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
.logout-btn:hover { background: rgba(255,255,255,0.10); color: #e5e7eb; }

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
  font-family: 'Georgia', serif;
  font-size: 24px;
  font-weight: 700;
  color: #0d0d0d;
  letter-spacing: -0.02em;
  display: flex;
  align-items: center;
  gap: 12px;
}
.page-sub { font-size: 13px; color: #6b7280; }
.back-btn {
  font-family: system-ui, sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: #5b21b6;
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
  border: 1px solid #e5e2db;
  border-radius: 12px;
  padding: 20px 22px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stat-label { font-size: 11.5px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 8px; }
.stat-val   { font-size: 30px; font-weight: 700; color: #0d0d0d; font-family: 'Georgia', serif; letter-spacing: -0.03em; line-height: 1; margin-bottom: 6px; }
.stat-note  { font-size: 12px; color: #9ca3af; }

/* ── Card ── */
.card {
  background: white;
  border: 1px solid #e5e2db;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.card-title {
  font-family: 'Georgia', serif;
  font-size: 15px;
  font-weight: 700;
  color: #0d0d0d;
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
.dist-track { flex: 1; height: 8px; background: #f4f3ef; border-radius: 99px; overflow: hidden; }
.dist-fill  { height: 100%; border-radius: 99px; transition: width 0.6s ease; }
.dist-pct   { font-size: 12px; font-weight: 600; color: #6b7280; min-width: 32px; text-align: right; }

/* ── Activity ── */
.activity-list { display: flex; flex-direction: column; gap: 0; }
.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 0;
  border-bottom: 1px solid #f4f3ef;
}
.activity-item:last-child { border-bottom: none; }
.act-avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: #ede9fe;
  color: #5b21b6;
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
  border: 1.5px solid #e5e2db;
  border-radius: 8px;
  font-size: 13.5px;
  font-family: system-ui, sans-serif;
  color: #0d0d0d;
  background: #fafaf9;
  outline: none;
  transition: border-color 0.15s;
}
.search-input:focus { border-color: #5b21b6; }
.filter-select {
  padding: 9px 12px;
  border: 1.5px solid #e5e2db;
  border-radius: 8px;
  font-size: 13px;
  font-family: system-ui, sans-serif;
  color: #0d0d0d;
  background: #fafaf9;
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
  border-bottom: 1px solid #e5e2db;
}
.data-table td {
  padding: 12px;
  border-bottom: 1px solid #f4f3ef;
  color: #374151;
  vertical-align: middle;
}
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #fafaf9; }
.text-soft { color: #6b7280; }
.text-center { text-align: center; }

.user-cell { display: flex; align-items: center; gap: 8px; font-weight: 500; }
.user-av {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: #ede9fe;
  color: #5b21b6;
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
.role-admin { background: #ede9fe; color: #5b21b6; }
.role-user  { background: #f4f3ef; color: #6b7280; }

.action-btn {
  font-size: 12.5px;
  color: #5b21b6;
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
  background: #f4f3ef;
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
  background: #5b21b6;
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
.metric-val  { font-size: 14px; font-weight: 700; color: #0d0d0d; }
.metric-track { height: 6px; background: #f4f3ef; border-radius: 99px; overflow: hidden; }
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
  border-bottom: 1px solid #e5e2db;
  text-align: left;
}
.perf-table td {
  padding: 11px 12px;
  border-bottom: 1px solid #f4f3ef;
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
  border-bottom: 1px solid #e5e2db;
}
.matrix-table th:first-child { text-align: left; }
.matrix-table tr th:first-child {
  text-align: left;
  font-size: 13px;
  color: #374151;
  padding: 12px 16px;
  border-bottom: none;
  border-right: 1px solid #e5e2db;
}
.matrix-cell {
  padding: 14px 16px;
  text-align: center;
  color: #374151;
  background: #fafaf9;
  border: 1px solid #e5e2db;
  font-size: 15px;
}
.matrix-correct {
  padding: 14px 16px;
  text-align: center;
  background: #ede9fe;
  color: #5b21b6;
  font-weight: 700;
  font-size: 15px;
  border: 1px solid #ddd6fe;
}
</style>
