import axios from '@/plugins/axios'
import type {App} from 'vue'
import vuetify from './vuetify'
import {apiBaseUrl} from '@/utils'
import {createPinia} from 'pinia'
import {loadFonts} from './webfontloader'

export function registerPlugins (app: App) {
  loadFonts().then(() => {})
  app
    .use(axios, {baseUrl: apiBaseUrl()})
    .use(createPinia())
    .use(vuetify)
}
