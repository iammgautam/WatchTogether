<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Overlay -->
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="$emit('close')"></div>
    
    <!-- Modal Content -->
    <div class="relative w-full max-w-lg bg-white text-gray-900 rounded-2xl shadow-2xl overflow-visible animate-in fade-in zoom-in duration-200">
      <div class="p-6 sm:p-8">
        <div class="text-center mb-6">
          <h2 class="text-2xl font-bold tracking-tight">Create a Room</h2>
          <p class="mt-1 text-sm text-gray-500">Invite up to 10 friends to watch with you.</p>
        </div>

        <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm text-center">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="createRoom" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700">Room Name</label>
            <input v-model="roomName" type="text" required class="mt-1 block w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 bg-white text-gray-900 transition-colors" placeholder="e.g. Movie Night" />
          </div>

          <!-- User Search AutoComplete -->
          <div class="relative">
            <label class="block text-sm font-medium text-gray-700">Invite Friends ({{ selectedUsers.length }}/10)</label>
            <input v-model="searchQuery" @input="debouncedSearch" type="text" :disabled="selectedUsers.length >= 10" class="mt-1 block w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 bg-white text-gray-900 disabled:bg-gray-100 transition-colors" placeholder="Search by username..." />
            
            <!-- Dropdown -->
            <ul v-if="searchResults.length > 0" class="absolute z-20 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-48 overflow-y-auto">
              <li v-for="user in searchResults" :key="user.id" @click="addUser(user)" class="px-4 py-3 hover:bg-indigo-50 cursor-pointer flex justify-between items-center transition-colors">
                <span class="font-medium text-gray-900">{{ user.username }}</span>
                <span v-if="isSelected(user.id)" class="text-indigo-600 text-sm">Added</span>
              </li>
            </ul>
          </div>

          <!-- Selected Tags -->
          <div v-if="selectedUsers.length > 0" class="flex flex-wrap gap-2">
            <span v-for="user in selectedUsers" :key="user.id" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-indigo-100 text-indigo-700">
              {{ user.username }}
              <button @click.prevent="removeUser(user.id)" type="button" class="text-indigo-500 hover:text-indigo-900 transition-colors">&times;</button>
            </span>
          </div>

          <div class="pt-4 space-y-3">
            <button type="submit" :disabled="isLoading || !roomName" class="w-full flex items-center justify-center py-3 rounded-xl font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 transition-all">
              <span v-if="isLoading">Creating...</span>
              <span v-else>Create & Join Room</span>
            </button>
            <button type="button" @click="$emit('close')" class="w-full py-3 rounded-xl font-medium text-gray-600 hover:bg-gray-100 transition-all">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const props = defineProps<{ isOpen: boolean }>()
const emit = defineEmits(['close'])

const router = useRouter()
const authStore = useAuthStore()

const roomName = ref('')
const searchQuery = ref('')
const searchResults = ref<{id: number, username: string}[]>([])
const selectedUsers = ref<{id: number, username: string}[]>([])
const isLoading = ref(false)
const errorMessage = ref('')

let searchTimeout: any = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  if (searchQuery.value.length < 2) {
    searchResults.value = []
    return
  }
  
  searchTimeout = setTimeout(async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/users/search?q=${searchQuery.value}`, {
        headers: {
          'Authorization': `Bearer ${authStore.accessToken}`
        }
      })
      if (res.ok) {
        searchResults.value = await res.json()
      }
    } catch (e) {
      console.error(e)
    }
  }, 300)
}

const isSelected = (id: number) => selectedUsers.value.some(u => u.id === id)

const addUser = (user: {id: number, username: string}) => {
  if (selectedUsers.value.length >= 10) return
  if (!isSelected(user.id)) {
    selectedUsers.value.push(user)
  }
  searchQuery.value = ''
  searchResults.value = []
}

const removeUser = (id: number) => {
  selectedUsers.value = selectedUsers.value.filter(u => u.id !== id)
}

const createRoom = async () => {
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    const res = await fetch('http://localhost:8000/api/rooms/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.accessToken}`
      },
      body: JSON.stringify({
        name: roomName.value,
        invited_user_ids: selectedUsers.value.map(u => u.id)
      })
    })
    
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(errorData.detail || 'Failed to create room')
    }
    
    const room = await res.json()
    emit('close')
    router.push(`/room/${room.id}`)
  } catch (error: any) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}
</script>
