<template>
  <div class="h-screen bg-slate-950 text-white flex flex-col overflow-hidden">
    <!-- Navbar -->
    <nav class="bg-slate-900 border-b border-slate-800 px-6 py-3 flex justify-between items-center z-20 shrink-0">
      <div class="flex items-center gap-3">
        <div class="p-1.5 bg-indigo-600 rounded-lg">
          <MonitorPlay class="w-5 h-5 text-white" />
        </div>
        <span class="text-lg font-bold tracking-tight">WatchTogether</span>
        <div class="h-4 w-[1px] bg-slate-700 mx-2"></div>
        <span class="text-xs font-mono text-slate-400 bg-slate-800 px-2 py-1 rounded truncate max-w-[150px] md:max-w-none">
          {{ roomId }}
        </span>
      </div>
      
      <div class="flex items-center gap-4">
        <div v-if="!isConnected" class="flex items-center gap-2 text-xs text-amber-400 animate-pulse">
          <span class="w-2 h-2 rounded-full bg-amber-400"></span>
          Connecting...
        </div>
        <button 
          @click="$router.push('/dashboard')" 
          class="text-sm font-medium px-4 py-2 bg-slate-800 hover:bg-rose-600/20 hover:text-rose-400 rounded-lg transition-all border border-transparent hover:border-rose-500/30"
        >
          Leave Room
        </button>
      </div>
    </nav>
    
    <div class="flex-1 flex overflow-hidden relative">
      <!-- Main Content (Placeholder for video) -->
      <main class="flex-1 flex flex-col min-w-0 bg-slate-950 relative items-center justify-center">
        <div class="text-center p-8 bg-slate-900/30 border border-dashed border-slate-800 rounded-2xl max-w-md">
          <Users class="w-12 h-12 text-slate-700 mx-auto mb-4" />
          <p class="text-slate-500 font-medium text-lg">Room: {{ roomId }}</p>
          <p class="text-slate-600 mt-2 text-sm italic">Video calling feature is coming soon...</p>
        </div>
      </main>

      <!-- Chat Sidebar -->
      <aside 
        :class="showSidebar ? 'translate-x-0 w-80 md:w-96 border-l' : 'translate-x-full w-0 border-none'"
        class="bg-slate-900 border-slate-800 flex flex-col transition-all duration-300 transform shrink-0 overflow-hidden"
      >
        <div class="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
          <h2 class="font-bold flex items-center gap-2">
            <MessageSquare class="w-4 h-4 text-indigo-400" />
            Room Chat
          </h2>
          <button @click="showSidebar = false" class="text-slate-400 hover:text-white p-1">
            <X class="w-4 h-4" />
          </button>
        </div>

        <!-- Messages List -->
        <div ref="chatContainerRef" class="flex-1 overflow-y-auto p-4 space-y-4">
          <div 
            v-for="(msg, i) in messages" 
            :key="i" 
            :class="msg.user_id === authStore.user?.id ? 'items-end' : 'items-start'"
            class="flex flex-col"
          >
            <div class="flex items-center gap-2 mb-1 px-1">
              <span class="text-[10px] uppercase font-bold tracking-wider text-slate-500">{{ msg.username }}</span>
              <span class="text-[9px] text-slate-600">{{ formatTime(msg.created_at) }}</span>
            </div>
            <div 
              :class="msg.user_id === authStore.user?.id ? 'bg-indigo-600 text-white rounded-l-2xl rounded-br-2xl' : 'bg-slate-800 text-slate-200 rounded-r-2xl rounded-bl-2xl'"
              class="px-4 py-2 text-sm shadow-sm max-w-[85%] break-words"
            >
              {{ msg.content }}
            </div>
          </div>
          <div v-if="messages.length === 0" class="h-full flex flex-col items-center justify-center opacity-30">
            <MessageCircle class="w-12 h-12 mb-2" />
            <p class="text-xs">No messages yet.</p>
          </div>
        </div>

        <!-- Chat Input -->
        <div class="p-4 bg-slate-900/80 backdrop-blur-lg border-t border-slate-800">
          <form @submit.prevent="handleSendMessage" class="flex items-center gap-2">
            <input 
              v-model="newMessage"
              placeholder="Type a message..."
              class="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all placeholder:text-slate-500"
            />
            <button 
              type="submit"
              :disabled="!newMessage.trim()"
              class="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 p-2 rounded-xl transition-all shadow-lg shadow-indigo-500/20"
            >
              <Send class="w-4 h-4" />
            </button>
          </form>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { 
  MonitorPlay, MessageSquare, X, Send, Users, MessageCircle
} from 'lucide-vue-next'
import { useRoomSocket } from '../composables/useRoomSocket'

const route = useRoute()
const roomId = route.params.id as string
const authStore = useAuthStore()

// State
const showSidebar = ref(true)
const newMessage = ref('')
const chatContainerRef = ref<HTMLElement | null>(null)

// Composables
const { 
  messages, 
  isConnected, 
  connect, 
  sendMessage
} = useRoomSocket(roomId)

// Initialization
onMounted(async () => {
  // Connect to room (messages + WS)
  await connect()
})

// Handlers
const handleSendMessage = () => {
  if (newMessage.value.trim()) {
    sendMessage(newMessage.value.trim())
    newMessage.value = ''
  }
}

const formatTime = (iso?: string) => {
  if (!iso) return ''
  try {
    const date = new Date(iso)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (e) {
    return ''
  }
}

// Auto-scroll chat
watch(messages, () => {
  nextTick(() => {
    if (chatContainerRef.value) {
      chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight
    }
  })
}, { deep: true })
</script>

<style scoped>
.h-screen {
  height: 100vh;
}
</style>
