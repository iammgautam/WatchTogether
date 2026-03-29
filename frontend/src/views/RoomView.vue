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
      <!-- Main Content (Video Grid) -->
      <main class="flex-1 flex flex-col min-w-0 bg-slate-950 relative">
        <div class="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
          <div :class="gridClass" class="h-full w-full gap-4 transition-all duration-500">
            <!-- Local Video -->
            <div class="relative group bg-slate-900 rounded-2xl overflow-hidden border border-slate-800 aspect-video shadow-2xl">
              <video 
                ref="localVideoRef" 
                autoplay 
                muted 
                playsinline 
                class="w-full h-full object-cover mirror transform scale-x-[-1]"
              ></video>
              <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-4">
                <span class="text-sm font-semibold flex items-center gap-2">
                  <User class="w-4 h-4 text-indigo-400" />
                  You ({{ authStore.user?.username }})
                </span>
                <div class="ml-auto flex gap-2">
                  <MicOff v-if="!micEnabled" class="w-4 h-4 text-rose-500" />
                  <VideoOff v-if="!cameraEnabled" class="w-4 h-4 text-rose-500" />
                </div>
              </div>
            </div>

            <!-- Remote Videos -->
            <div 
              v-for="[userId, stream] in remoteStreams" 
              :key="userId"
              class="relative group bg-slate-900 rounded-2xl overflow-hidden border border-slate-800 aspect-video shadow-2xl"
            >
              <video 
                :srcObject.prop="stream" 
                autoplay 
                playsinline 
                class="w-full h-full object-cover"
              ></video>
              <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-4">
                <span class="text-sm font-semibold flex items-center gap-2">
                  <User class="w-4 h-4 text-emerald-400" />
                  {{ peerUsernames.get(userId) || `User ${userId}` }}
                </span>
              </div>
            </div>
            
            <!-- Waiting Placeholder if alone -->
            <div v-if="remoteStreams.size === 0" class="flex flex-col items-center justify-center p-8 bg-slate-900/30 border border-dashed border-slate-800 rounded-2xl aspect-video">
              <Users class="w-12 h-12 text-slate-700 mb-4" />
              <p class="text-slate-500 font-medium">Waiting for others to join...</p>
              <span class="text-xs text-slate-600 mt-1">Invited users will appear here automatically.</span>
            </div>
          </div>
        </div>

        <!-- Floating Controls -->
        <div class="absolute bottom-10 left-1/2 -translate-x-1/2 flex items-center gap-4 px-6 py-4 bg-slate-900/80 backdrop-blur-xl border border-slate-700 rounded-2xl shadow-2xl z-20">
          <button 
            @click="toggleMic"
            :class="micEnabled ? 'bg-slate-700 hover:bg-slate-600 text-white' : 'bg-rose-600 hover:bg-rose-500 text-white'"
            class="w-12 h-12 rounded-xl flex items-center justify-center transition-all group relative"
          >
            <Mic v-if="micEnabled" class="w-5 h-5" />
            <MicOff v-else class="w-5 h-5" />
            <span class="absolute -top-10 scale-0 group-hover:scale-100 transition-all bg-slate-800 text-xs px-2 py-1 rounded">{{ micEnabled ? 'Mute' : 'Unmute' }}</span>
          </button>

          <button 
            @click="toggleCamera"
            :class="cameraEnabled ? 'bg-slate-700 hover:bg-slate-600 text-white' : 'bg-rose-600 hover:bg-rose-500 text-white'"
            class="w-12 h-12 rounded-xl flex items-center justify-center transition-all group relative"
          >
            <VideoIcon v-if="cameraEnabled" class="w-5 h-5" />
            <VideoOff v-else class="w-5 h-5" />
            <span class="absolute -top-10 scale-0 group-hover:scale-100 transition-all bg-slate-800 text-xs px-2 py-1 rounded">{{ cameraEnabled ? 'Stop Camera' : 'Start Camera' }}</span>
          </button>

          <div class="w-[1px] h-8 bg-slate-700 mx-2"></div>

          <button 
            @click="showSidebar = !showSidebar"
            class="w-12 h-12 rounded-xl flex items-center justify-center transition-all bg-slate-700 hover:bg-indigo-600 text-white relative group"
          >
            <MessageSquare class="w-5 h-5" />
            <span v-if="!showSidebar" class="absolute -top-1 right-0 w-3 h-3 bg-indigo-500 border-2 border-slate-900 rounded-full"></span>
            <span class="absolute -top-10 scale-0 group-hover:scale-100 transition-all bg-slate-800 text-xs px-2 py-1 rounded">Chat</span>
          </button>
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
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { 
  MonitorPlay, User, Mic, MicOff, Video as VideoIcon, VideoOff, 
  MessageSquare, X, Send, Users, MessageCircle
} from 'lucide-vue-next'
import { useRoomSocket } from '../composables/useRoomSocket'
import { useWebRTC } from '../composables/useWebRTC'

const route = useRoute()
const roomId = route.params.id as string
const authStore = useAuthStore()

// State
const showSidebar = ref(true)
const newMessage = ref('')
const micEnabled = ref(true)
const cameraEnabled = ref(true)
const chatContainerRef = ref<HTMLElement | null>(null)
const localVideoRef = ref<HTMLVideoElement | null>(null)

// Composables
const { 
  messages, 
  isConnected, 
  connect, 
  sendMessage, 
  sendSignaling, 
  setSignalingHandler 
} = useRoomSocket(roomId)

const { 
  remoteStreams, 
  peerUsernames,
  getLocalStream, 
  handleSignaling, 
  toggleVideo, 
  toggleAudio 
} = useWebRTC(Number(authStore.user?.id) || 0, sendSignaling)

// Grid layout logic — always at least 2-column to avoid layout shift
const gridClass = computed(() => {
  const total = remoteStreams.size + 1
  // Always show 2 columns (local + placeholder/remote) so the layout never jumps
  if (total <= 2) return 'grid grid-cols-1 md:grid-cols-2 place-items-center max-w-6xl mx-auto'
  if (total <= 4) return 'grid grid-cols-1 sm:grid-cols-2 place-items-center max-w-6xl mx-auto'
  return 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 max-w-7xl mx-auto'
})

// Initialization
onMounted(async () => {
  // Get User Media permissions immediately BEFORE connecting
  // This ensures localStream is available when RTCPeerConnections are created during signaling
  const stream = await getLocalStream()
  if (stream && localVideoRef.value) {
    localVideoRef.value.srcObject = stream
  }

  // Setup WebRTC signaling link
  setSignalingHandler(handleSignaling)

  // Finally, connect to room (WS) so we are announced and receive/send offers with tracks ready
  await connect()
})

// Handlers
const handleSendMessage = () => {
  if (newMessage.value.trim()) {
    sendMessage(newMessage.value.trim())
    newMessage.value = ''
  }
}

const toggleMic = () => {
  micEnabled.value = !micEnabled.value
  toggleAudio(micEnabled.value)
}

const toggleCamera = () => {
  cameraEnabled.value = !cameraEnabled.value
  toggleVideo(cameraEnabled.value)
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
