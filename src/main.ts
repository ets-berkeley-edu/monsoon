import App from './App.vue'
import axios from 'axios'
import router from '@/router'
import {apiBaseUrl} from '@/utils'
import {createApp} from 'vue'
import {fetchAuthStatus} from '@/api/auth'
import {registerPlugins} from '@/plugins'
import {useContextStore} from '@/stores/context'

const app = createApp(App)

registerPlugins(app)

const baseUrl = apiBaseUrl()

axios.get(`${baseUrl}/api/config`, {withCredentials: true}).then(({data}) => {
  useContextStore().setConfig({
    ...data,
    apiBaseUrl: baseUrl
  })
  return fetchAuthStatus()
}).then(({username}) => {
  useContextStore().setCurrentUser({username})
  app.use(router)
  app.mount('#app')
})
