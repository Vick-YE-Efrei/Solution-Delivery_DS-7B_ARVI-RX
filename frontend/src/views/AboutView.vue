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
          class="rounded-xl px-4 py-3 flex items-center gap-3.5 border border-blue-500/20 bg-blue-600/10 text-blue-400">
          <span class="material-symbols-outlined text-xl" style="font-variation-settings:'FILL' 1">info</span>
          <span class="font-semibold text-sm">{{ t('nav.about') }}</span>
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
    <main class="flex-1 flex flex-col bg-surface overflow-auto">

      <!-- Top Bar -->
      <header class="flex items-center px-8 h-16 glass-header sticky top-0 z-40 border-b border-outline-variant gap-3">
        <span class="material-symbols-outlined text-on-surface-variant">info</span>
        <h2 class="page-title-font text-lg font-extrabold text-on-surface">{{ t('about.title') }}</h2>
      </header>

      <div class="px-8 py-8 space-y-8 max-w-4xl mx-auto w-full">

        <!-- Avertissement -->
        <div class="bg-amber-50 border border-amber-200 rounded-2xl px-6 py-4 flex items-start gap-3">
          <span class="material-symbols-outlined text-amber-600 mt-0.5 flex-shrink-0">warning</span>
          <p class="text-sm text-amber-900 font-medium leading-relaxed">
            {{ t('common.warning') }}
          </p>
        </div>

        <!-- Présentation -->
        <div class="bg-white rounded-2xl border border-outline-variant premium-shadow p-6">
          <div class="flex items-center gap-3 mb-4">
            <span class="material-symbols-outlined text-primary text-2xl">local_hospital</span>
            <h2 class="page-title-font text-xl font-extrabold text-on-surface">{{ t('about.what_title') }}</h2>
          </div>
          <p class="text-sm text-on-surface-variant leading-relaxed mb-3">{{ t('about.what_p1') }}</p>
          <p class="text-sm text-on-surface-variant leading-relaxed mb-3">{{ t('about.what_p2') }}</p>
          <p class="text-sm text-on-surface-variant leading-relaxed">
            {{ t('about.what_p3') }} <strong class="text-emerald-700">{{ t('about.class_normal_label') }}</strong>, <strong class="text-orange-700">{{ t('about.class_opacity_label') }}</strong> {{ locale === 'fr' ? 'ou' : 'or' }} <strong class="text-amber-700">{{ t('about.class_uncertain_label') }}</strong>.
          </p>
        </div>

        <!-- Comment ça marche -->
        <div class="bg-white rounded-2xl border border-outline-variant premium-shadow p-6">
          <div class="flex items-center gap-3 mb-5">
            <span class="material-symbols-outlined text-primary text-2xl">settings_suggest</span>
            <h2 class="page-title-font text-xl font-extrabold text-on-surface">{{ t('about.how_title') }}</h2>
          </div>

          <div class="space-y-4">
            <div v-for="step in steps" :key="step.num" class="flex items-start gap-4">
              <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-xs font-extrabold flex-shrink-0">
                {{ step.num }}
              </div>
              <div>
                <p class="text-sm font-bold text-on-surface">{{ step.title }}</p>
                <p class="text-xs text-on-surface-variant leading-relaxed mt-0.5">{{ step.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Modes d'analyse -->
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-white rounded-2xl border border-outline-variant premium-shadow p-5">
            <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">{{ t('about.mode_baseline_header') }}</p>
            <p class="text-sm font-bold text-on-surface mb-1">{{ t('about.mode_baseline_label') }}</p>
            <p class="text-xs text-on-surface-variant leading-relaxed">{{ t('about.mode_baseline_desc') }}</p>
          </div>
          <div class="bg-white rounded-2xl border border-outline-variant premium-shadow p-5">
            <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">{{ t('about.mode_improved_header') }}</p>
            <p class="text-sm font-bold text-on-surface mb-1">{{ t('about.mode_improved_label') }}</p>
            <p class="text-xs text-on-surface-variant leading-relaxed">{{ t('about.mode_improved_desc') }}</p>
          </div>
        </div>

        <!-- Classes -->
        <div class="bg-white rounded-2xl border border-outline-variant premium-shadow p-6">
          <div class="flex items-center gap-3 mb-4">
            <span class="material-symbols-outlined text-primary text-2xl">category</span>
            <h2 class="page-title-font text-xl font-extrabold text-on-surface">{{ t('about.classes_title') }}</h2>
          </div>
          <div class="space-y-3">
            <div class="flex items-start gap-3 p-3 rounded-xl bg-emerald-50 border border-emerald-100">
              <span class="material-symbols-outlined text-emerald-600 text-lg mt-0.5">check_circle</span>
              <div>
                <p class="text-sm font-bold text-emerald-800">{{ t('about.class_normal_label') }}</p>
                <p class="text-xs text-emerald-700 leading-relaxed">{{ t('about.class_normal_desc') }}</p>
              </div>
            </div>
            <div class="flex items-start gap-3 p-3 rounded-xl bg-orange-50 border border-orange-100">
              <span class="material-symbols-outlined text-orange-600 text-lg mt-0.5">blur_on</span>
              <div>
                <p class="text-sm font-bold text-orange-800">{{ t('about.class_opacity_label') }}</p>
                <p class="text-xs text-orange-700 leading-relaxed">{{ t('about.class_opacity_desc') }}</p>
              </div>
            </div>
            <div class="flex items-start gap-3 p-3 rounded-xl bg-amber-50 border border-amber-100">
              <span class="material-symbols-outlined text-amber-600 text-lg mt-0.5">help</span>
              <div>
                <p class="text-sm font-bold text-amber-800">{{ t('about.class_uncertain_label') }}</p>
                <p class="text-xs text-amber-700 leading-relaxed">{{ t('about.class_uncertain_desc') }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Équipe -->
        <div class="bg-white rounded-2xl border border-outline-variant premium-shadow p-6">
          <div class="flex items-center gap-3 mb-5">
            <span class="material-symbols-outlined text-primary text-2xl">groups</span>
            <h2 class="page-title-font text-xl font-extrabold text-on-surface">{{ t('about.team_title') }}</h2>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div v-for="member in team" :key="member.email"
              class="flex items-start gap-3 p-4 rounded-xl border border-outline-variant hover:bg-slate-50 transition-colors">
              <div class="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-white text-xs font-extrabold flex-shrink-0">
                {{ initials(member.name) }}
              </div>
              <div class="min-w-0">
                <p class="text-sm font-bold text-on-surface truncate">{{ member.name }}</p>
                <p class="text-[10px] font-semibold text-primary uppercase tracking-wider mt-0.5">{{ member.role }}</p>
                <p class="text-[10px] text-on-surface-variant truncate mt-0.5">{{ member.email }}</p>
                <span v-if="member.ref"
                  class="inline-block mt-1 text-[9px] font-bold uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded-full">
                  {{ t('about.role_ref') }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Contexte technique -->
        <div class="bg-white rounded-2xl border border-outline-variant premium-shadow p-6">
          <div class="flex items-center gap-3 mb-4">
            <span class="material-symbols-outlined text-primary text-2xl">code</span>
            <h2 class="page-title-font text-xl font-extrabold text-on-surface">{{ t('about.stack_title') }}</h2>
          </div>
          <div class="grid grid-cols-3 gap-3">
            <div v-for="tech in stack" :key="tech.label" class="p-3 rounded-xl bg-slate-50 border border-outline-variant text-center">
              <p class="text-xs font-bold text-on-surface">{{ tech.label }}</p>
              <p class="text-[10px] text-on-surface-variant mt-0.5">{{ tech.detail }}</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <p class="text-xs text-on-surface-variant text-center pb-4">
          {{ t('about.footer') }}
        </p>

      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../store/auth.js'
import { t, locale, toggleLocale } from '../store/locale.js'
const raviLogo = '/ravi-logo.png'

const router = useRouter()

function logout() { auth.logout(); router.push('/login') }

const userInitials = computed(() => {
  const name = auth.user?.name ?? ''
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) || 'U'
})

function initials(name) {
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

const steps = computed(() => [
  { num: '1', title: t('about.step1_title'), desc: t('about.step1_desc') },
  { num: '2', title: t('about.step2_title'), desc: t('about.step2_desc') },
  { num: '3', title: t('about.step3_title'), desc: t('about.step3_desc') },
  { num: '4', title: t('about.step4_title'), desc: t('about.step4_desc') },
])

const team = [
  { name: 'Vick YE',                  role: 'Données / Modèle',  email: 'vick.ye@efrei.net',                    ref: true  },
  { name: 'Kim Lan TRAN',             role: 'Données / Modèle',  email: 'kim-lan.tran@efrei.net',               ref: false },
  { name: 'Assah Paul Ariel YAPO',    role: 'Intégration',       email: 'assah-paul-ariel.yapo@efrei.net',      ref: false },
  { name: 'Yousri ZOUHDI',            role: 'Évaluation',        email: 'yousri.zouhdi@efrei.net',              ref: false },
  { name: 'Ghaith TAKTAK',            role: 'Intégration',       email: 'ghaith.taktak@efrei.net',              ref: false },
  { name: 'Christian TEWA DJIMBOU',   role: 'Évaluation',        email: 'christian.tewa-djimbou@efrei.net',     ref: false },
]

const stack = [
  { label: 'Vue 3',         detail: 'Frontend SPA'         },
  { label: 'Express.js',    detail: 'API REST backend'     },
  { label: 'FastAPI',       detail: 'Moteur IA Python'     },
  { label: 'MedGemma 4B',   detail: 'VLM médical Google'   },
  { label: 'LoRA / PEFT',   detail: 'Fine-tuning RSNA'     },
  { label: 'MySQL',         detail: 'Base de données'      },
]
</script>
