import App from './App.vue'
import axios from 'axios'
import router from '@/router'
import {apiBaseUrl} from '@/utils'
import {createApp} from 'vue'
import {registerPlugins} from '@/plugins'
import {useContextStore} from '@/stores/context'

const app = createApp(App)

registerPlugins(app)

const baseUrl = apiBaseUrl()

axios.get(`${baseUrl}/api/config`).then(({data}) => {
  useContextStore().setConfig({
    ...data,
    apiBaseUrl: baseUrl
  })
  app.use(router)
  app.mount('#app')
})
