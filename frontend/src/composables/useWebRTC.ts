import { ref, onUnmounted, reactive } from 'vue'

export function useWebRTC(userId: number, sendSignaling: (data: any) => void) {
  const localStream = ref<MediaStream | null>(null)
  const remoteStreams = reactive<Map<number, MediaStream>>(new Map())
  const peerUsernames = reactive<Map<number, string>>(new Map())
  const peerConnections = new Map<number, RTCPeerConnection>()
  
  const iceServers = [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
  ]

  const getLocalStream = async () => {
    try {
      // 480p default as per user request, scaling between 360p and 720p
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { min: 480, ideal: 640, max: 1280 },
          height: { min: 360, ideal: 480, max: 720 },
          frameRate: { ideal: 24, max: 30 }
        },
        audio: true
      })
      localStream.value = stream
      return stream
    } catch (e) {
      console.error('Error accessing media devices:', e)
      return null
    }
  }

  const createPeerConnection = (targetUserId: number) => {
    const pc = new RTCPeerConnection({ iceServers })
    
    // Add local tracks to peer connection
    if (localStream.value) {
      localStream.value.getTracks().forEach(track => {
        pc.addTrack(track, localStream.value!)
      })
    }

    pc.onicecandidate = (event) => {
      if (event.candidate) {
        sendSignaling({
          event: 'webrtc_ice_candidate',
          target_user_id: targetUserId,
          candidate: event.candidate
        })
      }
    }

    pc.ontrack = (event) => {
      remoteStreams.set(targetUserId, event.streams[0])
    }

    pc.onconnectionstatechange = () => {
      if (pc.connectionState === 'disconnected' || pc.connectionState === 'closed' || pc.connectionState === 'failed') {
        remoteStreams.delete(targetUserId)
        peerConnections.delete(targetUserId)
      }
    }

    peerConnections.set(targetUserId, pc)
    return pc
  }

  const handleSignaling = async (data: any) => {
    const { event, sender_user_id } = data
    console.log('[WebRTC] Received signaling event:', event, 'from:', sender_user_id || data.user_id, 'my userId:', userId)
    
    if (event === 'webrtc_offer') {
      console.log('[WebRTC] Handling offer from user', sender_user_id)
      // Track the sender's username for display
      if (data.sender_username) peerUsernames.set(sender_user_id, data.sender_username)
      let pc = peerConnections.get(sender_user_id)
      if (!pc) pc = createPeerConnection(sender_user_id)
      
      await pc.setRemoteDescription(new RTCSessionDescription(data.offer))
      const answer = await pc.createAnswer()
      await pc.setLocalDescription(answer)
      
      sendSignaling({
        event: 'webrtc_answer',
        target_user_id: sender_user_id,
        answer: answer
      })
      console.log('[WebRTC] Sent answer to user', sender_user_id)
    } else if (event === 'webrtc_answer') {
      console.log('[WebRTC] Handling answer from user', sender_user_id)
      const pc = peerConnections.get(sender_user_id)
      if (pc) {
        await pc.setRemoteDescription(new RTCSessionDescription(data.answer))
      }
    } else if (event === 'webrtc_ice_candidate') {
      const pc = peerConnections.get(sender_user_id)
      if (pc) {
        try {
          await pc.addIceCandidate(new RTCIceCandidate(data.candidate))
        } catch (e) {
          console.error('[WebRTC] Error adding ICE candidate:', e)
        }
      }
    } else if (event === 'user_joined') {
      const joinedUserId = Number(data.user_id)
      console.log('[WebRTC] user_joined event. joinedUserId:', joinedUserId, 'myUserId:', userId, 'same?', joinedUserId === userId)
      if (joinedUserId !== userId) {
        // Track username for display
        if (data.username) peerUsernames.set(joinedUserId, data.username)
        console.log('[WebRTC] Creating offer for new user', joinedUserId)
        const pc = createPeerConnection(joinedUserId)
        const offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        
        sendSignaling({
          event: 'webrtc_offer',
          target_user_id: joinedUserId,
          offer: offer
        })
        console.log('[WebRTC] Sent offer to user', joinedUserId)
      }
    } else if (event === 'user_left') {
      const leftUserId = Number(data.user_id)
      const pc = peerConnections.get(leftUserId)
      if (pc) {
        pc.close()
        peerConnections.delete(leftUserId)
        remoteStreams.delete(leftUserId)
        peerUsernames.delete(leftUserId)
      }
    }
  }

  const toggleVideo = (enabled: boolean) => {
    if (localStream.value) {
      localStream.value.getVideoTracks().forEach(track => {
        track.enabled = enabled
      })
    }
  }

  const toggleAudio = (enabled: boolean) => {
    if (localStream.value) {
      localStream.value.getAudioTracks().forEach(track => {
        track.enabled = enabled
      })
    }
  }

  onUnmounted(() => {
    localStream.value?.getTracks().forEach(track => track.stop())
    peerConnections.forEach(pc => pc.close())
  })

  return {
    localStream,
    remoteStreams,
    peerUsernames,
    getLocalStream,
    handleSignaling,
    toggleVideo,
    toggleAudio
  }
}
