<template>
  <div class="flex min-h-screen">
    <aside class="flex flex-col h-screen w-64 sticky left-0 top-0 bg-[#0f172a] py-6 z-50">
      <div class="px-6 mb-8 flex items-center gap-3">
        <img src="/ravi-logo.png" alt="Logo RaVI" class="h-12 w-12 rounded-xl bg-white object-contain p-1 shadow-sm" />
        <div>
          <h1 class="page-title-font text-2xl text-white font-extrabold tracking-tight">RaVI</h1>
          <p class="text-[10px] uppercase tracking-[0.2em] text-slate-400 font-bold mt-1">Prototype Pédagogique</p>
        </div>
      </div>

      <nav class="flex-1 px-4 space-y-1">
        <router-link to="/"
          class="text-slate-400 hover:text-white rounded-xl px-4 py-3 flex items-center gap-3.5 hover:bg-white/5 transition-colors">
          <span class="material-symbols-outlined text-xl">radiology</span>
          <span class="font-medium text-sm">Analyse RX Thorax</span>
        </router-link>
        <router-link to="/history"
          class="text-slate-400 hover:text-white rounded-xl px-4 py-3 flex items-center gap-3.5 hover:bg-white/5 transition-colors">
          <span class="material-symbols-outlined text-xl">history</span>
          <span class="font-medium text-sm">Historique</span>
        </router-link>
        <router-link v-if="auth.isAdmin" to="/admin"
          class="text-slate-400 hover:text-white rounded-xl px-4 py-3 flex items-center gap-3.5 hover:bg-white/5 transition-colors">
          <span class="material-symbols-outlined text-xl">assessment</span>
          <span class="font-medium text-sm">M&eacute;triques</span>
        </router-link>
        <router-link to="/about"
          class="rounded-xl px-4 py-3 flex items-center gap-3.5 border border-blue-500/20 bg-blue-600/10 text-blue-400">
          <span class="material-symbols-outlined text-xl" style="font-variation-settings:'FILL' 1">info</span>
          <span class="font-semibold text-sm">&Agrave; propos</span>
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
          class="w-full text-[10px] font-bold text-slate-500 hover:text-slate-300 uppercase tracking-wider py-1 transition-colors">
          D&eacute;connexion
        </button>
      </div>
    </aside>

    <main class="flex-1 flex flex-col bg-surface overflow-auto">
      <header class="flex justify-between items-center px-8 h-16 glass-header sticky top-0 z-40 border-b border-outline-variant">
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-on-surface-variant">info</span>
          <h2 class="page-title-font text-lg font-extrabold text-on-surface">&Agrave; propos de RaVI</h2>
        </div>
        <router-link to="/"
          class="flex items-center gap-2 btn-primary-gradient text-white text-xs font-bold px-4 py-2 rounded-full hover:scale-[1.02] transition-all no-underline">
          <span class="material-symbols-outlined text-sm">radiology</span>
          Nouvelle analyse
        </router-link>
      </header>

      <div class="px-8 py-6 space-y-6 flex-1">
        <section class="bg-white rounded-2xl border border-outline-variant premium-shadow p-7">
          <p class="text-[10px] font-bold uppercase tracking-[0.16em] text-primary mb-3">Prototype p&eacute;dagogique</p>
          <h1 class="page-title-font text-3xl font-extrabold text-on-surface mb-4">Assistant radiologique virtuel intelligent</h1>
          <p class="text-sm leading-7 text-slate-600 max-w-4xl">
            RaVI aide &agrave; tester une cha&icirc;ne d'analyse de radiographies thoraciques frontales avec une sortie JSON structur&eacute;e :
            qualit&eacute; image, classe pr&eacute;dite, confiance, observations visuelles, justification, limites et avertissement.
            Le projet reste non clinique et doit toujours &ecirc;tre valid&eacute; par un professionnel qualifi&eacute;.
          </p>
        </section>

        <section class="grid grid-cols-3 gap-4">
          <article class="bg-white rounded-2xl border border-outline-variant premium-shadow p-5">
            <span class="material-symbols-outlined text-primary text-2xl mb-3">account_tree</span>
            <h3 class="page-title-font text-sm font-extrabold text-on-surface mb-2">Pipeline</h3>
            <p class="text-xs leading-6 text-slate-600">Vue.js re&ccedil;oit l'image, Express.js orchestre l'analyse, MedGemma produit la r&eacute;ponse, MySQL journalise les r&eacute;sultats.</p>
          </article>
          <article class="bg-white rounded-2xl border border-outline-variant premium-shadow p-5">
            <span class="material-symbols-outlined text-primary text-2xl mb-3">verified_user</span>
            <h3 class="page-title-font text-sm font-extrabold text-on-surface mb-2">Garde-fous</h3>
            <p class="text-xs leading-6 text-slate-600">La classe uncertain est une d&eacute;cision de s&eacute;curit&eacute; quand la qualit&eacute;, le JSON ou la confiance ne permettent pas de conclure.</p>
          </article>
          <article class="bg-white rounded-2xl border border-outline-variant premium-shadow p-5">
            <span class="material-symbols-outlined text-primary text-2xl mb-3">database</span>
            <h3 class="page-title-font text-sm font-extrabold text-on-surface mb-2">Tra&ccedil;abilit&eacute;</h3>
            <p class="text-xs leading-6 text-slate-600">Chaque pr&eacute;diction conserve le mod&egrave;le, le mode, la confiance, la latence et les champs importants pour l'audit.</p>
          </article>
        </section>

        <section class="grid grid-cols-[1.2fr_0.8fr] gap-4">
          <article class="bg-white rounded-2xl border border-outline-variant premium-shadow p-6">
            <h3 class="page-title-font text-base font-extrabold text-on-surface mb-4">Contrat de sortie attendu</h3>
            <div class="grid grid-cols-2 gap-3 text-xs text-slate-600">
              <div class="rounded-xl bg-slate-50 border border-slate-200 p-3"><strong>image_quality</strong><br />good, limited ou insufficient</div>
              <div class="rounded-xl bg-slate-50 border border-slate-200 p-3"><strong>predicted_class</strong><br />normal, suspected_opacity ou uncertain</div>
              <div class="rounded-xl bg-slate-50 border border-slate-200 p-3"><strong>confidence</strong><br />score entre 0 et 1</div>
              <div class="rounded-xl bg-slate-50 border border-slate-200 p-3"><strong>visual_evidence</strong><br />observations visuelles courtes</div>
              <div class="rounded-xl bg-slate-50 border border-slate-200 p-3"><strong>justification</strong><br />raisonnement synth&eacute;tique</div>
              <div class="rounded-xl bg-slate-50 border border-slate-200 p-3"><strong>warning</strong><br />rappel non clinique obligatoire</div>
            </div>
          </article>

          <article class="bg-amber-50 rounded-2xl border border-amber-200 premium-shadow p-6">
            <div class="flex items-center gap-2 mb-3">
              <span class="material-symbols-outlined text-amber-600">warning</span>
              <h3 class="page-title-font text-base font-extrabold text-amber-900">Limite essentielle</h3>
            </div>
            <p class="text-sm leading-7 text-amber-900">
              RaVI n'est pas un dispositif m&eacute;dical. Il ne doit pas servir &agrave; diagnostiquer, trier ou orienter un patient.
              La sortie sert uniquement &agrave; d&eacute;montrer une architecture d'IA m&eacute;dicale responsable.
            </p>
          </article>
        </section>

        <section class="bg-white rounded-2xl border border-outline-variant premium-shadow p-6">
          <h3 class="page-title-font text-base font-extrabold text-on-surface mb-4">Documentation projet</h3>
          <div class="grid grid-cols-4 gap-3">
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">Mod&egrave;le</p>
              <p class="text-sm font-bold text-slate-700">MedGemma 4B PT</p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">Frontend</p>
              <p class="text-sm font-bold text-slate-700">Vue 3 + Vite</p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">Backend</p>
              <p class="text-sm font-bold text-slate-700">Express.js</p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">Base</p>
              <p class="text-sm font-bold text-slate-700">MySQL</p>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../store/auth.js'

const router = useRouter()

const userInitials = computed(() => {
  const name = auth.user?.name ?? 'EF'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
