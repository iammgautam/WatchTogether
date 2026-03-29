import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'

export interface ChatMessage {
  id?: number
  user_id: number
  username: string
  content: string
  created_at?: string
  event?: string
}

export function useRoomSocket(roomId: string) {
  const authStore = useAuthStore()
  const messages = ref<ChatMessage[]>([])
  const isConnected = ref(false)
  const socket = ref<WebSocket | null>(null)
  
  // Callback for WebRTC signaling
  let onSignalingMessage: ((data: any) => void) | null = null

  const connect = async () => {
    // 1. Fetch initial chat history
    try {
      const res = await fetch(`http://localhost:8000/api/rooms/${roomId}/messages`, {
        headers: {
          'Authorization': `Bearer ${authStore.accessToken}`
        }
      })
      if (res.ok) {
        messages.value = await res.json()
      }
    } catch (e) {
      console.error('Failed to fetch chat history:', e)
    }

    // 2. Establish WebSocket connection
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//localhost:8000/ws/rooms/${roomId}?token=${authStore.accessToken}`
    
    socket.value = new WebSocket(wsUrl)

    socket.value.onopen = () => {
      isConnected.value = true
      console.log('Connected to room socket')
    }

    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.event === 'chat') {
        messages.value.push(data)
      } else if (data.event === 'user_joined' || data.event === 'user_left') {
        // Show in chat
        messages.value.push({
          user_id: data.user_id,
          username: 'System',
          content: `${data.username} has ${data.event === 'user_joined' ? 'joined' : 'left'} the room.`,
          event: data.event
        })
        // ALSO forward to WebRTC handler so it can initiate/close peer connections
        if (onSignalingMessage) onSignalingMessage(data)
      }
      
      // Pass WebRTC signaling messages to the handler
      if (['webrtc_offer', 'webrtc_answer', 'webrtc_ice_candidate'].includes(data.event)) {
        if (onSignalingMessage) onSignalingMessage(data)
      }
    }

    socket.value.onclose = () => {
      isConnected.value = false
      console.log('Disconnected from room socket')
    }
  }

  const sendMessage = (content: string) => {
    if (socket.value && isConnected.value) {
      socket.value.send(JSON.stringify({
        event: 'chat',
        content
      }))
    }
  }

  const sendSignaling = (data: any) => {
    if (socket.value && isConnected.value) {
      socket.value.send(JSON.stringify(data))
    }
  }

  const setSignalingHandler = (handler: (data: any) => void) => {
    onSignalingMessage = handler
  }

  const disconnect = () => {
    if (socket.value) {
      socket.value.close()
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    messages,
    isConnected,
    connect,
    disconnect,
    sendMessage,
    sendSignaling,
    setSignalingHandler
  }
}
