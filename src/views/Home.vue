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
          v-if="config.monsoonEnv"
          class="text-body-2 text-medium-emphasis mt-6"
        >
          Backend environment: <strong>{{ config.monsoonEnv }}</strong>
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import {useContextStore} from '@/stores/context'

const config = useContextStore().config
</script>
