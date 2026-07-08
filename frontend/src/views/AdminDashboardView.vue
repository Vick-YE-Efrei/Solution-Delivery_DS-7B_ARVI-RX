<template>
  <div class="layout">

    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <img :src="raviLogo" alt="RAVI" style="width:32px;height:32px;border-radius:8px;object-fit:contain;background:white;padding:3px;flex-shrink:0;" />
        <span>RAVI Admin</span>
      </div>
      <nav class="sidebar-nav">
        <a href="#" class="slink" :class="{ active: section === 'overview' }" @click.prevent="section = 'overview'">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/><rect x="9" y="1" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/><rect x="1" y="9" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/><rect x="9" y="9" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/></svg>
          {{ t('admin.overview') }}
        </a>
        <a href="#" class="slink" :class="{ active: section === 'users' }" @click.prevent="section = 'users'">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="6" cy="5" r="3" stroke="currentColor" stroke-width="1.4"/><path d="M1 14c0-3 2-5 5-5s5 2 5 5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><path d="M12 7c1.7 0 3 1.3 3 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><circle cx="12" cy="4" r="2" stroke="currentColor" stroke-width="1.4"/></svg>
          {{ t('admin.users') }}
        </a>
        <a href="#" class="slink" :class="{ active: section === 'analyses' }" @click.prevent="section = 'analyses'">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 12h2l2-5 3 8 2-6 1 3h2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
          {{ t('admin.analyses') }}
        </a>
        <a href="#" class="slink" :class="{ active: section === 'perf' }" @click.prevent="section = 'perf'">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.4"/><path d="M8 5v3.5l2.5 1.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
          {{ t('admin.performance') }}
        </a>
        <div style="height:1px;background:#1e293b;margin:8px 0"></div>
        <router-link to="/" class="slink" style="text-decoration:none;color:#a78bfa;background:rgba(124,58,237,0.12);">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="6" cy="5" r="2.5" stroke="currentColor" stroke-width="1.4"/><path d="M1 14c0-2.8 2-4.5 5-4.5s5 1.7 5 4.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><path d="M11 8l3 3m0 0l-3 3m3-3H9" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
          {{ t('nav.user_interface') }}
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="admin-info">
          <div class="admin-avatar">{{ auth.user?.name?.[0]?.toUpperCase() ?? 'A' }}</div>
          <div>
            <p class="admin-name">{{ auth.user?.name ?? 'Admin' }}</p>
            <p class="admin-role">{{ t('admin.role_admin') }}</p>
          </div>
        </div>
        <button class="logout-btn" style="margin-bottom:4px;background:transparent;border-color:#1e293b;color:#64748b;" @click="toggleLocale">
          <span class="material-symbols-outlined" style="font-size:15px;vertical-align:middle;margin-right:6px;">translate</span>
          {{ locale === 'fr' ? 'English' : 'Français' }}
        </button>
        <button class="logout-btn" @click="logout">
          <span class="material-symbols-outlined" style="font-size:15px;vertical-align:middle;margin-right:6px;">logout</span>
          {{ t('common.logout') }}
        </button>
      </div>
    </aside>

    <!-- Contenu -->
    <div class="content">

      <!-- ── LOADING ── -->
      <div v-if="isLoading" style="display:flex;align-items:center;justify-content:center;height:60vh;color:#9ca3af;font-size:14px;gap:10px;">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style="animation:spin 1s linear infinite">
          <circle cx="10" cy="10" r="8" stroke="#e5e7eb" stroke-width="2.5"/>
          <path d="M10 2a8 8 0 0 1 8 8" stroke="#5b21b6" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        {{ t('admin.loading') }}
      </div>

      <!-- ── VUE D'ENSEMBLE ── -->
      <section v-else-if="section === 'overview'">
        <div class="page-head">
          <h1 class="page-title">{{ t('admin.overview') }}</h1>
          <p class="page-sub">{{ t('admin.dashboard') }} — {{ today }}</p>
        </div>
        <div class="stats-grid">
          <div class="stat-card">
            <p class="stat-label">{{ t('admin.stat_users') }}</p>
            <p class="stat-val">{{ stats.totalUsers }}</p>
            <p class="stat-note">{{ users.filter(u => u.role === 'user').length }} {{ t('admin.stat_users_note_u') }}, {{ users.filter(u => u.role === 'admin').length }} {{ t('admin.stat_users_note_a') }}</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">{{ t('admin.stat_analyses') }}</p>
            <p class="stat-val">{{ stats.totalAnalyses }}</p>
            <p class="stat-note">{{ t('admin.stat_conf_note') }} {{ stats.avgConfidence }}%</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">{{ t('admin.stat_avg_conf') }}</p>
            <p class="stat-val">{{ stats.avgConfidence }}%</p>
            <p class="stat-note">{{ t('admin.stat_on') }} {{ stats.totalAnalyses }} {{ t('admin.stat_on_analyses') }}</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">{{ t('admin.stat_uncertainty') }}</p>
            <p class="stat-val">{{ stats.uncertainRate }}%</p>
            <p class="stat-note">{{ t('admin.stat_uncertainty_note') }}</p>
          </div>
        </div>

        <div class="overview-row">
          <div class="card">
            <h2 class="card-title">{{ t('admin.dist_title') }}</h2>
            <div class="dist-bars">
              <div v-for="item in distribution" :key="item.key" class="dist-row">
                <span class="dist-label">{{ t('class.' + item.key) }}</span>
                <div class="dist-track">
                  <div class="dist-fill" :style="{ width: item.pct + '%', background: item.color }"></div>
                </div>
                <span class="dist-pct">{{ item.pct }}%</span>
              </div>
            </div>
          </div>

          <div class="card">
            <h2 class="card-title">{{ t('admin.activity_title') }}</h2>
            <ul class="activity-list">
              <li v-for="act in recentActivity" :key="act.id" class="activity-item">
                <div class="act-avatar">{{ act.user[0].toUpperCase() }}</div>
                <div class="act-info">
                  <span class="act-user">{{ act.user }}</span>
                  <span class="act-action">{{ t('admin.activity_action') }}</span>
                  <span :class="['act-badge', `badge--${act.result}`]">{{ classLabel(act.result) }}</span>
                </div>
                <span class="act-time">{{ timeAgo(act.createdAt) }}</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <!-- ── UTILISATEURS ── -->
      <section v-else-if="section === 'users'">
        <div class="page-head">
          <h1 class="page-title">{{ t('admin.users') }}</h1>
          <p class="page-sub">{{ users.length }} {{ t('admin.accounts_count') }}</p>
        </div>
        <div class="card">
          <div class="table-toolbar">
            <input v-model="userSearch" class="search-input" :placeholder="t('admin.search_user')" />
          </div>
          <table class="data-table">
            <thead>
              <tr>
                <th>{{ t('admin.col_name') }}</th>
                <th>{{ t('admin.col_email') }}</th>
                <th>{{ t('admin.col_role') }}</th>
                <th>{{ t('admin.analyses') }}</th>
                <th>{{ t('admin.col_registered') }}</th>
                <th>{{ t('admin.col_actions') }}</th>
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
                  <button class="action-btn" @click="viewUserHistory(u)">{{ t('admin.btn_history') }}</button>
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
            <span v-if="!selectedUser">{{ t('admin.all_analyses') }}</span>
            <span v-else>
              {{ t('admin.analyses_of') }} {{ selectedUser.name }}
              <button class="back-btn" @click="selectedUser = null">{{ t('admin.back') }}</button>
            </span>
          </h1>
          <p class="page-sub">{{ filteredAnalyses.length }} {{ t('admin.analyses').toLowerCase() }}</p>
        </div>
        <div class="card">
          <div class="table-toolbar">
            <input v-model="analysisSearch" class="search-input" :placeholder="t('admin.search')" />
            <select v-model="analysisFilter" class="filter-select">
              <option value="">{{ t('history.all_classes') }}</option>
              <option value="normal">{{ t('class.normal') }}</option>
              <option value="suspected_opacity">{{ t('class.suspected_opacity') }}</option>
              <option value="uncertain">{{ t('class.uncertain') }}</option>
            </select>
          </div>
          <table class="data-table">
            <thead>
              <tr>
                <th>{{ t('admin.col_user') }}</th>
                <th>{{ t('admin.col_date') }}</th>
                <th>{{ t('admin.col_mode') }}</th>
                <th>{{ t('admin.col_result') }}</th>
                <th>{{ t('admin.col_confidence') }}</th>
                <th>{{ t('admin.col_threshold') }}</th>
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
          <h1 class="page-title">{{ t('admin.perf_title') }}</h1>
          <p class="page-sub">{{ t('admin.perf_sub') }} {{ perfData.total }} {{ t('admin.perf_sub2') }}</p>
        </div>

        <div v-if="perfData.total === 0" style="text-align:center;padding:60px;color:#9ca3af;font-size:14px;">
          {{ t('admin.no_data_msg') }}
        </div>

        <div v-else class="perf-grid">
          <div class="card">
            <h2 class="card-title">{{ t('admin.global_metrics') }}</h2>
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
            <h2 class="card-title">{{ t('admin.comparison_title') }}</h2>
            <table class="perf-table">
              <thead>
                <tr><th>{{ t('admin.col_metric') }}</th><th>Baseline</th><th>{{ t('admin.col_improved') }}</th><th>{{ t('admin.col_delta') }}</th></tr>
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
            <h2 class="card-title">{{ t('admin.by_model') }}</h2>
            <table class="perf-table">
              <thead>
                <tr><th>{{ t('admin.col_model') }}</th><th>{{ t('admin.analyses') }}</th><th>{{ t('admin.col_avg_conf') }}</th></tr>
              </thead>
              <tbody>
                <tr v-for="m in perfData.byModel" :key="m.model_name">
                  <td style="font-family:monospace;font-size:12px">{{ m.model_name }}</td>
                  <td class="text-center">{{ m.count }}</td>
                  <td class="text-center">{{ m.avg_conf }}%</td>
                </tr>
                <tr v-if="!perfData.byModel.length">
                  <td colspan="3" style="text-align:center;color:#9ca3af;padding:16px">{{ t('admin.no_data') }}</td>
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
import { t, locale, toggleLocale } from '../store/locale.js'
const raviLogo = '/ravi-logo.png'

const router  = useRouter()
const section = ref('overview')
const isLoading = ref(true)

const today = computed(() => {
  const loc = locale.value === 'fr' ? 'fr-FR' : 'en-GB'
  return new Date().toLocaleDateString(loc, { day: 'numeric', month: 'long', year: 'numeric' })
})

function logout() { auth.logout(); router.push('/login') }
function classLabel(pred) {
  return {
    normal:            t('class.normal'),
    suspected_opacity: t('class.suspected_opacity'),
    uncertain:         t('class.uncertain'),
  }[pred] ?? pred
}
function fmt(iso) {
  const loc = locale.value === 'fr' ? 'fr-FR' : 'en-GB'
  return new Date(iso).toLocaleString(loc, {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}
function timeAgo(iso) {
  const diff = Math.floor((Date.now() - new Date(iso)) / 1000)
  if (locale.value === 'fr') {
    if (diff < 60)    return `il y a ${diff}s`
    if (diff < 3600)  return `il y a ${Math.floor(diff/60)}min`
    if (diff < 86400) return `il y a ${Math.floor(diff/3600)}h`
    return `il y a ${Math.floor(diff/86400)}j`
  } else {
    if (diff < 60)    return `${diff}s ago`
    if (diff < 3600)  return `${Math.floor(diff/60)}min ago`
    if (diff < 86400) return `${Math.floor(diff/3600)}h ago`
    return `${Math.floor(diff/86400)}d ago`
  }
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
        { key: 'normal',            pct: +((s.normal_count  / total) * 100).toFixed(1), color: '#16a34a', count: s.normal_count },
        { key: 'suspected_opacity', pct: +((s.opacity_count / total) * 100).toFixed(1), color: '#c2410c', count: s.opacity_count },
        { key: 'uncertain',         pct: +((s.uncertain_count / total) * 100).toFixed(1), color: '#d97706', count: s.uncertain_count },
      ]
    }

    // Par modèle
    byModel.value = statsRes.data.by_model ?? []

    // Activité récente (5 dernières analyses)
    recentActivity.value = analysesRes.data.slice(0, 5).map(a => ({
      id:        a.id,
      user:      a.user_name,
      result:    a.predicted_class,
      createdAt: a.created_at,
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
      { name: t('admin.metric_avg_conf'),       value: globalConf + '%',  pct: globalConf,              color: '#5b21b6' },
      { name: t('admin.metric_normal_rate'),     value: (distribution.value[0]?.pct ?? 0) + '%', pct: distribution.value[0]?.pct ?? 0, color: '#16a34a' },
      { name: t('admin.metric_opacity_rate'),    value: (distribution.value[1]?.pct ?? 0) + '%', pct: distribution.value[1]?.pct ?? 0, color: '#c2410c' },
      { name: t('admin.metric_uncertain_rate'),  value: globalUncert + '%', pct: globalUncert,            color: '#d97706' },
      { name: t('admin.metric_avg_latency'),     value: globalLat + ' ms',  pct: Math.min(globalLat / 50, 100), color: '#0ea5e9' },
    ],
    comparison: [
      {
        metric:   t('admin.comp_avg_conf'),
        baseline: avgConf(baseline) + '%',
        improved: avgConf(improved) + '%',
        delta:    +(avgConf(improved) - avgConf(baseline)).toFixed(1),
      },
      {
        metric:   t('admin.comp_uncertain_rate'),
        baseline: uncertainPct(baseline) + '%',
        improved: uncertainPct(improved) + '%',
        delta:    +(uncertainPct(improved) - uncertainPct(baseline)).toFixed(1),
      },
      {
        metric:   t('admin.comp_count'),
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
