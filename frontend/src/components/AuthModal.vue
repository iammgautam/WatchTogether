<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Overlay -->
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="$emit('close')"></div>
    
    <!-- Modal Content -->
    <div class="relative w-full max-w-md bg-white text-gray-900 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
      <div class="p-6 sm:p-8">
        <!-- Header -->
        <div class="text-center mb-6">
          <h2 class="text-3xl font-bold text-gray-900 tracking-tight">
            {{ isLogin ? 'Welcome back' : 'Create an account' }}
          </h2>
          <p class="mt-2 text-sm text-gray-500">
            {{ isLogin ? 'Enter your details to sign in.' : 'Join WatchTogether.' }}
          </p>
        </div>

        <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm text-center">
          {{ errorMessage }}
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div v-if="!isLogin">
            <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
            <input v-model="form.email" id="email" name="email" type="email" autocomplete="email" required
              class="mt-1 block w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
              placeholder="you@example.com" />
          </div>

          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
            <input v-model="form.username" id="username" name="username" type="text" autocomplete="username" required
              class="mt-1 block w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
              placeholder="Your username" />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <input v-model="form.password" id="password" name="password" type="password" autocomplete="current-password" required
              class="mt-1 block w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
              placeholder="••••••••" />
          </div>

          <button type="submit" :disabled="isLoading"
            class="w-full flex justify-center py-3 px-4 rounded-xl shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-all">
            <span v-if="isLoading">Loading...</span>
            <span v-else>{{ isLogin ? 'Sign In' : 'Sign Up' }}</span>
          </button>
        </form>

        <!-- Toggle Mode -->
        <p class="mt-6 text-center text-sm text-gray-600">
          {{ isLogin ? "Don't have an account?" : "Already have an account?" }}
          <button @click="toggleMode" type="button" class="font-semibold text-indigo-600 hover:text-indigo-500 transition-colors">
            {{ isLogin ? 'Sign up here' : 'Log in instead' }}
          </button>
        </p>
      </div>
      
      <!-- Close Button -->
      <button @click="$emit('close')" type="button" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors">
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const props = defineProps<{
  isOpen: boolean
  initialMode: 'login' | 'signup'
}>()

const emit = defineEmits(['close'])

const router = useRouter()
const authStore = useAuthStore()

const isLogin = ref(props.initialMode === 'login')
const isLoading = ref(false)
const errorMessage = ref('')

const form = reactive({
  email: '',
  username: '',
  password: ''
})

// Sync mode if parent changes it
watch(() => props.initialMode, (newVal) => {
  isLogin.value = newVal === 'login'
})

const toggleMode = () => {
  isLogin.value = !isLogin.value
  errorMessage.value = ''
}

const handleSubmit = async () => {
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    if (isLogin.value) {
      const formData = new URLSearchParams()
      formData.append('username', form.username)
      formData.append('password', form.password)
      
      const res = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      })
      
      if (!res.ok) throw new Error('Invalid credentials')
      
      const data = await res.json()
      authStore.login(data.access_token, data.refresh_token)
      authStore.setUser(data.user)
      emit('close')
      router.push('/dashboard')
      
    } else {
      const res = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: form.username,
          email: form.email,
          password: form.password
        })
      })
      
      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.detail || 'Signup failed')
      }
      
      // Auto-login after successful registration
      isLogin.value = true
      await handleSubmit()
    }
  } catch (error: any) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}
</script>
