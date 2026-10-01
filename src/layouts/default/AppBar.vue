<template>
  <v-app-bar flat>
    <v-app-bar-title>
      <router-link class="app-title-link" to="/">
        <v-icon v-if="!isHome" aria-hidden="true" icon="mdi-chevron-left" />
        <span>Monsoon</span>
      </router-link>
    </v-app-bar-title>
    <v-menu v-if="contextStore.currentUser.username">
      <template #activator="{ props }">
        <v-btn id="account-menu-activator" variant="text" v-bind="props">
          {{ contextStore.currentUser.username }}
        </v-btn>
      </template>
      <v-list>
        <v-list-item title="Log out" @click="handleLogout" />
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script lang="ts" setup>
import {computed} from 'vue'
import {logout} from '@/api/auth'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()
const route = useRoute()

const isHome = computed(() => route.name === 'Home')

const handleLogout = async () => {
  await logout()
  contextStore.setCurrentUser({username: null})
}
</script>

<style scoped>
.app-title-link {
  align-items: center;
  color: inherit;
  display: inline-flex;
  text-decoration: none;
}
</style>
