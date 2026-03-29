<template>
  <div class="min-h-screen bg-slate-900 text-white selection:bg-indigo-500/30">
    <!-- Navbar -->
    <nav class="absolute top-0 w-full px-6 py-4 flex items-center justify-between z-10">
      <div class="flex items-center gap-2">
        <MonitorPlay class="w-8 h-8 text-indigo-500" />
        <span class="text-xl font-bold tracking-tight">WatchTogether</span>
      </div>
      <div class="flex items-center gap-4">
        <button @click="openModal('login')" class="text-sm font-medium hover:text-indigo-400 transition-colors">
          Log in
        </button>
        <button @click="openModal('signup')" class="text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-full transition-all shadow-lg hover:shadow-indigo-500/25">
          Sign up
        </button>
      </div>
    </nav>

    <!-- Hero Section -->
    <main class="relative h-screen flex items-center justify-center overflow-hidden">
      <!-- Background Effects -->
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-indigo-600/20 blur-[120px] rounded-full pointer-events-none"></div>
      
      <div class="relative z-10 text-center px-4 max-w-4xl mx-auto">
        <h1 class="text-5xl md:text-7xl font-extrabold tracking-tight mb-8">
          Watch movies with friends, <br>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">
            perfectly in sync.
          </span>
        </h1>
        <p class="text-lg md:text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
          Create rooms, invite your friends, and watch videos together. Chat in real-time and never miss a reaction.
        </p>
        
        <button @click="openModal('signup')" class="group relative inline-flex items-center justify-center gap-2 bg-white text-slate-900 px-8 py-4 rounded-full text-lg font-bold transition-all hover:scale-105 active:scale-95">
          Start Watching Free
          <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </main>

    <AuthModal 
      :is-open="isModalOpen" 
      :initial-mode="modalMode" 
      @close="isModalOpen = false" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { MonitorPlay, ArrowRight } from 'lucide-vue-next'
import AuthModal from '../components/AuthModal.vue'

const isModalOpen = ref(false)
const modalMode = ref<'login' | 'signup'>('login')

const openModal = (mode: 'login' | 'signup') => {
  modalMode.value = mode
  isModalOpen.value = true
}
</script>
