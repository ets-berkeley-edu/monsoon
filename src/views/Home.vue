<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col
        cols="12"
        sm="8"
        md="6"
        class="text-center"
      >
        <h1 id="page-title" class="text-h3 mb-4">
          Monsoon
        </h1>
        <p class="text-body-1">
          Reimplementation scaffolding for UC Berkeley's CollectionSpace web apps.
        </p>
        <p
          v-if="contextStore.config.monsoonEnv"
          class="text-body-2 text-medium-emphasis mt-6"
        >
          Backend environment: <strong>{{ contextStore.config.monsoonEnv }}</strong>
        </p>
        <p
          v-if="contextStore.config.tenantSlug"
          class="text-body-2 text-medium-emphasis"
        >
          Tenant: <strong>{{ contextStore.config.tenantSlug }}</strong>
        </p>

        <v-card v-if="contextStore.config.tenantSlug" class="mt-8 mx-auto text-left" max-width="360">
          <v-card-text v-if="contextStore.currentUser.username">
            <v-list density="compact" :lines="false">
              <v-list-item
                v-for="tool in availableTools"
                :key="tool.key"
                :title="tool.name"
                :to="{name: tool.routeName}"
              >
                <template #prepend>
                  <v-icon :icon="tool.icon" />
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
          <v-card-text v-else>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="username"
                label="CollectionSpace username"
                autocomplete="username"
                required
              />
              <v-text-field
                v-model="password"
                label="CollectionSpace password"
                type="password"
                autocomplete="current-password"
                required
              />
              <v-alert
                v-if="error"
                type="error"
                density="compact"
                class="mb-4"
              >
                {{ error }}
              </v-alert>
              <v-btn type="submit" color="primary" :loading="loading">
                Log in
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
        <p v-else class="text-body-2 text-medium-emphasis mt-8">
          Visit a museum subdomain (e.g. <code>pahma.localhost:8080</code>) to log in.
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import {computed, ref} from 'vue'
import {TOOL_REGISTRY} from '@/lib/tools'
import {login} from '@/api/auth'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const availableTools = computed(() => {
  return (contextStore.config.availableTools || [])
    .filter(tool => TOOL_REGISTRY[tool.key])
    .map(tool => ({...tool, ...TOOL_REGISTRY[tool.key]}))
})

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  try {
    const data = await login(username.value, password.value)
    contextStore.setCurrentUser({username: data.username})
    password.value = ''
  } catch (e: any) {
    error.value = e.response?.data?.message || 'Login failed.'
  } finally {
    loading.value = false
  }
}
</script>
