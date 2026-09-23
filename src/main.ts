import App from './App.vue'
import axios from 'axios'
import router from '@/router'
import {createApp} from 'vue'
import {registerPlugins} from '@/plugins'
import {useContextStore} from '@/stores/context'

const app = createApp(App)

registerPlugins(app)

const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL

axios.get(`${apiBaseUrl}/api/config`).then(({data}) => {
  useContextStore().setConfig({
    ...data,
    apiBaseUrl
  })
  app.use(router)
  app.mount('#app')
})
