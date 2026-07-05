<template>
  <div class="flex min-h-screen">

    <!-- ═══════════════════ SIDEBAR ═══════════════════ -->
    <aside class="flex flex-col h-screen w-64 sticky left-0 top-0 bg-[#0f172a] py-6 z-50">
      <div class="px-8 mb-8">
        <h1 class="page-title-font text-2xl text-white font-extrabold tracking-tight">ARVI-RX</h1>
        <p class="text-[10px] uppercase tracking-[0.2em] text-slate-400 font-bold mt-1">Prototype Pédagogique</p>
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
          <span class="font-medium text-sm">Métriques</span>
        </router-link>
        <router-link to="/guide"
          class="rounded-xl px-4 py-3 flex items-center gap-3.5 border border-blue-500/20 bg-blue-600/10 text-blue-400">
          <span class="material-symbols-outlined text-xl" style="font-variation-settings:'FILL' 1">menu_book</span>
          <span class="font-semibold text-sm">Guide d'utilisation</span>
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
          class="w-full text-[10px] font-bold text-slate-500 hover:text-slate-300 uppercase tracking-wider py-1 transition-colors">
          Déconnexion
        </button>
      </div>
    </aside>

    <!-- ═══════════════════ MAIN ═══════════════════ -->
    <main class="flex-1 flex flex-col bg-surface overflow-auto">

      <!-- Top Bar -->
      <header class="flex items-center justify-between px-8 h-16 glass-header sticky top-0 z-40 border-b border-outline-variant">
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-on-surface-variant">menu_book</span>
          <h2 class="page-title-font text-lg font-extrabold text-on-surface">Guide d'utilisation</h2>
        </div>
        <div class="flex items-center gap-2 text-xs text-on-surface-variant font-medium">
          <span>Étape {{ currentStep + 1 }} / {{ steps.length }}</span>
          <div class="flex gap-1 ml-2">
            <div v-for="(_, i) in steps" :key="i"
              class="h-1.5 rounded-full transition-all duration-300 cursor-pointer"
              :class="i === currentStep ? 'w-6 bg-primary' : i < currentStep ? 'w-3 bg-primary/40' : 'w-3 bg-slate-200'"
              @click="goTo(i)">
            </div>
          </div>
        </div>
      </header>

      <!-- Progress bar -->
      <div class="h-0.5 bg-slate-100">
        <div class="h-full bg-primary transition-all duration-500"
          :style="{ width: ((currentStep + 1) / steps.length * 100) + '%' }">
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 flex flex-col">

        <!-- Step panel -->
        <transition :name="direction === 'forward' ? 'slide-left' : 'slide-right'" mode="out-in">
          <div :key="currentStep" class="flex-1 px-8 py-8 max-w-3xl">

            <!-- Step header -->
            <div class="flex items-center gap-4 mb-6">
              <div class="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0"
                :style="{ background: steps[currentStep].color + '20', border: '2px solid ' + steps[currentStep].color + '40' }">
                <span class="material-symbols-outlined text-2xl" :style="{ color: steps[currentStep].color }">
                  {{ steps[currentStep].icon }}
                </span>
              </div>
              <div>
                <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                  Étape {{ currentStep + 1 }}
                </p>
                <h1 class="page-title-font text-2xl font-extrabold text-on-surface">
                  {{ steps[currentStep].title }}
                </h1>
              </div>
            </div>

            <!-- Step description -->
            <p class="text-sm text-on-surface-variant leading-relaxed mb-6">
              {{ steps[currentStep].description }}
            </p>

            <!-- Interactive content -->
            <div class="space-y-3 mb-6">
              <div v-for="(item, i) in steps[currentStep].items" :key="i"
                class="group flex items-start gap-4 p-4 rounded-2xl border cursor-pointer transition-all duration-200"
                :class="selectedItems[currentStep] === i
                  ? 'border-primary/40 bg-primary/5 shadow-sm'
                  : 'border-outline-variant bg-white hover:border-primary/20 hover:bg-slate-50'"
                @click="selectItem(i)">

                <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors"
                  :class="selectedItems[currentStep] === i ? 'bg-primary text-white' : 'bg-slate-100 text-slate-500 group-hover:bg-primary/10 group-hover:text-primary'">
                  <span class="material-symbols-outlined text-sm">{{ item.icon }}</span>
                </div>

                <div class="flex-1 min-w-0">
                  <p class="text-sm font-bold text-on-surface">{{ item.label }}</p>
                  <p class="text-xs text-on-surface-variant leading-relaxed mt-0.5">{{ item.detail }}</p>
                </div>

                <span class="material-symbols-outlined text-sm transition-colors flex-shrink-0 mt-1"
                  :class="selectedItems[currentStep] === i ? 'text-primary' : 'text-slate-300'">
                  {{ selectedItems[currentStep] === i ? 'check_circle' : 'radio_button_unchecked' }}
                </span>
              </div>
            </div>

            <!-- Tip box -->
            <div v-if="steps[currentStep].tip"
              class="flex items-start gap-3 p-4 rounded-2xl bg-amber-50 border border-amber-200">
              <span class="material-symbols-outlined text-amber-600 text-lg flex-shrink-0 mt-0.5">lightbulb</span>
              <div>
                <p class="text-[10px] font-bold uppercase tracking-wider text-amber-700 mb-1">Conseil</p>
                <p class="text-xs text-amber-900 leading-relaxed">{{ steps[currentStep].tip }}</p>
              </div>
            </div>

            <!-- Warning box -->
            <div v-if="steps[currentStep].warning"
              class="mt-3 flex items-start gap-3 p-4 rounded-2xl bg-red-50 border border-red-200">
              <span class="material-symbols-outlined text-red-600 text-lg flex-shrink-0 mt-0.5">warning</span>
              <p class="text-xs text-red-900 leading-relaxed">{{ steps[currentStep].warning }}</p>
            </div>

          </div>
        </transition>

        <!-- Navigation -->
        <div class="px-8 py-5 border-t border-outline-variant flex items-center justify-between bg-white sticky bottom-0">

          <!-- Step pills -->
          <div class="hidden md:flex gap-2">
            <button v-for="(step, i) in steps" :key="i"
              @click="goTo(i)"
              class="text-[10px] font-bold uppercase tracking-wider px-3 py-1.5 rounded-full transition-all"
              :class="i === currentStep
                ? 'bg-primary text-white'
                : i < currentStep
                  ? 'bg-primary/10 text-primary'
                  : 'bg-slate-100 text-slate-400 hover:bg-slate-200'">
              {{ i + 1 }}. {{ step.short }}
            </button>
          </div>

          <div class="flex gap-3 ml-auto">
            <button v-if="currentStep > 0" @click="prev"
              class="flex items-center gap-2 px-5 py-2.5 rounded-full border border-outline-variant text-sm font-bold text-on-surface hover:bg-slate-50 transition-all">
              <span class="material-symbols-outlined text-sm">arrow_back</span>
              Précédent
            </button>

            <button v-if="currentStep < steps.length - 1" @click="next"
              class="flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-bold text-white transition-all btn-primary-gradient hover:scale-[1.02]">
              Suivant
              <span class="material-symbols-outlined text-sm">arrow_forward</span>
            </button>

            <router-link v-else to="/"
              class="flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-bold text-white btn-primary-gradient hover:scale-[1.02] no-underline transition-all">
              <span class="material-symbols-outlined text-sm">radiology</span>
              Commencer l'analyse
            </router-link>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../store/auth.js'

const router = useRouter()
function logout() { auth.logout(); router.push('/login') }

const userInitials = computed(() => {
  const name = auth.user?.name ?? ''
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) || 'U'
})

const currentStep = ref(0)
const direction   = ref('forward')
const selectedItems = ref({})

function selectItem(i) { selectedItems.value[currentStep.value] = i }

function next() {
  if (currentStep.value < steps.length - 1) {
    direction.value = 'forward'
    currentStep.value++
  }
}
function prev() {
  if (currentStep.value > 0) {
    direction.value = 'backward'
    currentStep.value--
  }
}
function goTo(i) {
  direction.value = i > currentStep.value ? 'forward' : 'backward'
  currentStep.value = i
}

const steps = [
  {
    short: 'Connexion',
    title: 'Se connecter à la plateforme',
    icon: 'login',
    color: '#3b82f6',
    description: 'Avant d\'utiliser ARVI-RX, vous devez vous authentifier avec votre compte. La plateforme dispose de deux types de comptes avec des accès différents.',
    items: [
      {
        icon: 'manage_accounts',
        label: 'Compte Administrateur',
        detail: 'Accès complet : analyse de radiographies, historique, tableau de bord avec métriques réelles, gestion des utilisateurs et performances du modèle.',
      },
      {
        icon: 'person',
        label: 'Compte Utilisateur',
        detail: 'Accès standard : analyse de radiographies et consultation de son propre historique d\'analyses.',
      },
    ],
    tip: 'Entrez votre email et mot de passe sur la page de connexion. Si c\'est votre première utilisation, contactez l\'administrateur pour obtenir vos identifiants.',
  },
  {
    short: 'Mode',
    title: 'Choisir le mode d\'analyse',
    icon: 'tune',
    color: '#8b5cf6',
    description: 'ARVI-RX propose deux modes d\'analyse selon vos besoins et les ressources disponibles. Sélectionnez le mode en haut de la page d\'analyse.',
    items: [
      {
        icon: 'speed',
        label: 'Mode Baseline',
        detail: 'Résultat instantané basé sur le nom du fichier. Idéal pour tester le pipeline sans attente. Ne mobilise pas le modèle IA.',
      },
      {
        icon: 'psychology',
        label: 'Mode Amélioré (Improved)',
        detail: 'Analyse réelle par MedGemma 4B PT fine-tuné sur données RSNA. Requiert un GPU NVIDIA. Première analyse ~1-2 minutes (chargement du modèle), les suivantes sont plus rapides.',
      },
    ],
    tip: 'Pour une démonstration rapide, utilisez le mode Baseline. Pour une analyse réelle avec le modèle IA, choisissez Amélioré.',
    warning: 'Le mode Amélioré est un prototype pédagogique. Le résultat ne constitue en aucun cas un avis médical.',
  },
  {
    short: 'Modèle',
    title: 'Choisir le modèle',
    icon: 'model_training',
    color: '#10b981',
    description: 'En mode Amélioré, vous pouvez sélectionner le modèle VLM à utiliser via le sélecteur en haut à droite de la page.',
    items: [
      {
        icon: 'medical_information',
        label: 'MedGemma 4B PT',
        detail: 'Modèle médical de Google pré-entraîné sur des données médicales multimodales, fine-tuné avec des adaptateurs LoRA sur des radiographies thoraciques RSNA. Recommandé.',
      },
      {
        icon: 'smart_toy',
        label: 'Gemma 4E4B',
        detail: 'Modèle généraliste de Google fine-tuné avec LoRA sur des données chest X-ray. Alternative expérimentale.',
      },
    ],
    tip: 'MedGemma 4B PT est recommandé car il a été pré-entraîné sur des données médicales, ce qui améliore la qualité des descriptions radiologiques générées.',
  },
  {
    short: 'Upload',
    title: 'Uploader une radiographie',
    icon: 'upload_file',
    color: '#f59e0b',
    description: 'Glissez-déposez ou cliquez sur la zone d\'upload pour sélectionner votre image de radiographie thoracique frontale.',
    items: [
      {
        icon: 'image',
        label: 'Formats acceptés',
        detail: 'PNG, JPG, JPEG. Taille maximale : 20 Mo. L\'image doit être une radiographie thoracique frontale (PA ou AP).',
      },
      {
        icon: 'drag_pan',
        label: 'Glisser-déposer',
        detail: 'Faites glisser directement votre fichier depuis l\'explorateur vers la zone de dépôt. L\'analyse démarre automatiquement.',
      },
      {
        icon: 'folder_open',
        label: 'Sélection manuelle',
        detail: 'Cliquez sur la zone d\'upload pour ouvrir l\'explorateur de fichiers et sélectionner votre image.',
      },
    ],
    tip: 'L\'analyse démarre automatiquement dès que l\'image est déposée. Vous verrez un indicateur de chargement pendant le traitement.',
  },
  {
    short: 'Résultats',
    title: 'Lire les résultats',
    icon: 'lab_research',
    color: '#ef4444',
    description: 'Une fois l\'analyse terminée, les résultats s\'affichent dans le panneau droit. Voici comment interpréter chaque élément.',
    items: [
      {
        icon: 'category',
        label: 'Classe prédite',
        detail: 'Normal (poumons sains), Opacité suspectée (consolidation, effusion détectée) ou Incertain (description ambiguë — c\'est un garde-fou, pas une erreur).',
      },
      {
        icon: 'percent',
        label: 'Indice de confiance',
        detail: '70% si un terme discriminant clair est détecté, 50% si la description est ambiguë. C\'est une confiance heuristique, non probabiliste.',
      },
      {
        icon: 'visibility',
        label: 'Observations visuelles',
        detail: 'Les termes détectés dans la description générée par le modèle et le texte brut de la description radiologique.',
      },
      {
        icon: 'summarize',
        label: 'Justification et limites',
        detail: 'La méthode de classification utilisée et les limites à prendre en compte pour interpréter le résultat.',
      },
    ],
    tip: 'Cliquez sur "Informations techniques" en bas du panneau pour voir les détails du modèle utilisé, la version du prompt et la latence.',
    warning: 'Ces résultats sont expérimentaux et non cliniquement validés. Ne jamais utiliser pour un diagnostic réel.',
  },
  {
    short: 'Historique',
    title: 'Consulter l\'historique',
    icon: 'history',
    color: '#06b6d4',
    description: 'Toutes vos analyses sont automatiquement sauvegardées et accessibles dans la page Historique via la barre latérale.',
    items: [
      {
        icon: 'filter_list',
        label: 'Filtrer les analyses',
        detail: 'Filtrez par classe prédite (Normal, Opacité, Incertain) ou par mode d\'analyse (Baseline / Amélioré) pour retrouver rapidement une analyse.',
      },
      {
        icon: 'expand_more',
        label: 'Détail d\'une analyse',
        detail: 'Cliquez sur une ligne pour afficher le détail complet : qualité image, justification, observations visuelles et limites identifiées.',
      },
      {
        icon: 'bar_chart',
        label: 'Résumé rapide',
        detail: 'Les compteurs en haut de la page affichent le total d\'analyses, le nombre de résultats normaux, d\'opacités et d\'incertains.',
      },
    ],
    tip: 'L\'historique est personnel — chaque utilisateur ne voit que ses propres analyses. L\'administrateur peut voir toutes les analyses depuis le tableau de bord.',
  },
]
</script>

<style scoped>
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.25s ease;
}
.slide-left-enter-from  { opacity: 0; transform: translateX(30px); }
.slide-left-leave-to    { opacity: 0; transform: translateX(-30px); }
.slide-right-enter-from { opacity: 0; transform: translateX(-30px); }
.slide-right-leave-to   { opacity: 0; transform: translateX(30px); }
</style>
