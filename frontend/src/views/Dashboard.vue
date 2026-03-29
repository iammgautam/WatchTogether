<template>
  <div class="min-h-screen bg-slate-900 text-white">
    <nav class="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16 items-center">
          <div class="flex items-center gap-2">
            <MonitorPlay class="w-6 h-6 text-indigo-500" />
            <span class="font-bold text-lg tracking-tight">WatchTogether</span>
          </div>
          <div class="flex items-center gap-4">
            <span class="text-sm text-slate-400">Welcome, <span class="text-white font-medium">{{ authStore.user?.username }}</span></span>
            <button @click="handleLogout" class="text-sm font-medium text-slate-300 hover:text-white transition-colors">
              Log out
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Header Area -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-12">
        <div>
          <h1 class="text-3xl font-bold tracking-tight mb-2">Your Dashboard</h1>
          <p class="text-slate-400">Join a room you've been invited to or start a new one.</p>
        </div>
        <button @click="isModalOpen = true" class="inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl font-semibold transition-all shadow-lg hover:shadow-indigo-500/25">
          <Plus class="w-5 h-5" />
          Create Room
        </button>
      </div>

      <!-- Invitations Section -->
      <div class="mb-12">
        <h2 class="text-xl font-semibold mb-6 flex items-center gap-2">
          <Mail class="w-5 h-5 text-indigo-400" />
          Invitations
        </h2>
        
        <div v-if="isLoading" class="text-slate-400">Loading rooms...</div>
        <div v-else-if="invitations.length === 0" class="bg-slate-800/50 border border-slate-800 rounded-2xl p-8 text-center">
          <p class="text-slate-400">No pending invitations.</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="room in invitations" :key="room.id" class="bg-slate-800 border border-slate-700 hover:border-indigo-500/50 rounded-2xl p-6 transition-all group">
            <div class="flex justify-between items-start mb-4">
              <h3 class="font-bold text-lg leading-tight">{{ room.name }}</h3>
              <span class="bg-indigo-500/10 text-indigo-400 text-xs px-2 py-1 rounded font-medium">Invited</span>
            </div>
            <p class="text-sm text-slate-400 mb-6 line-clamp-2">Click below to join this room and start watching together.</p>
            <button @click="$router.push(`/room/${room.id}`)" class="w-full flex justify-center items-center gap-2 bg-white/10 hover:bg-white text-white hover:text-slate-900 py-2.5 rounded-lg font-medium transition-all cursor-pointer">
              Join Room
              <ArrowRight class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- My Rooms Section -->
      <div>
        <h2 class="text-xl font-semibold mb-6 flex items-center gap-2">
          <MonitorPlay class="w-5 h-5 text-indigo-400" />
          My Rooms
        </h2>
        
        <div v-if="!isLoading && myRooms.length === 0" class="bg-slate-800/50 border border-slate-800 rounded-2xl p-8 text-center">
          <p class="text-slate-400">You haven't created any rooms yet.</p>
        </div>
        <div v-else-if="!isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="room in myRooms" :key="room.id" class="bg-slate-800 border border-slate-700 hover:border-indigo-500/50 rounded-2xl p-6 transition-all group">
            <h3 class="font-bold text-lg mb-2">{{ room.name }}</h3>
            <p class="text-slate-400 mb-6 font-mono text-xs opacity-50">{{ room.id }}</p>
            <button @click="$router.push(`/room/${room.id}`)" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2.5 rounded-lg font-medium transition-all cursor-pointer">
              Enter Room
            </button>
          </div>
        </div>
      </div>
    </main>

    <CreateRoomModal :is-open="isModalOpen" @close="closeModal" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { MonitorPlay, Plus, Mail, ArrowRight } from 'lucide-vue-next'
import CreateRoomModal from '../components/CreateRoomModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const isModalOpen = ref(false)
const isLoading = ref(true)
const myRooms = ref<any[]>([])
const invitations = ref<any[]>([])

const fetchRooms = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/rooms/me', {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`
      }
    })
    if (res.ok) {
      const data = await res.json()
      myRooms.value = data.my_rooms
      invitations.value = data.invitations
    }
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchRooms()
})

const closeModal = () => {
  isModalOpen.value = false
  fetchRooms()
}

const handleLogout = async () => {
  try {
    await fetch('http://localhost:8000/api/auth/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`
      }
    })
  } catch (e) {
    console.error('Logout failed:', e)
  } finally {
    authStore.logout()
    router.push('/')
  }
}
</script>
