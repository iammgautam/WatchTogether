<!-- <script setup lang="ts">
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <HelloWorld />
</template>

 -->


<script setup lang="ts">
import { ref, onMounted } from 'vue'

// A reactive variable to hold the message we get from Python!
const backendMessage = ref<string>('Connecting to backend...')

onMounted(async () => {
  try {
    // This goes to Vite, which secretly proxies it to FastAPI!
    const response = await fetch('/api/ping')
    
    if (!response.ok) throw new Error('Network response was not ok')
    
    const data = await response.json()
    // Update the UI with the JSON data from Python
    backendMessage.value = data.message 
  } catch (error) {
    backendMessage.value = 'Failed to connect to backend ❌'
    console.error('Fetch error:', error)
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-900 flex items-center justify-center">
    <div class="text-center p-12 bg-gray-800 rounded-3xl shadow-2xl border border-gray-700 max-w-xl w-full">
      <h1 class="text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 mb-8">
        WatchTogether
      </h1>
      
      <!-- The Backend Status Box -->
      <div class="p-6 bg-gray-900 rounded-xl border border-purple-500/30 shadow-inner">
        <h2 class="text-gray-400 text-sm font-bold uppercase tracking-wider mb-2">Backend Status</h2>
        <p class="text-purple-300 font-mono text-xl animate-pulse" v-if="backendMessage === 'Connecting to backend...'">
          {{ backendMessage }}
        </p>
        <p class="text-green-400 font-mono text-xl" v-else-if="!backendMessage.includes('❌')">
          ✅ {{ backendMessage }}
        </p>
        <p class="text-red-400 font-mono text-xl" v-else>
          {{ backendMessage }}
        </p>
      </div>

    </div>
  </div>
</template>
