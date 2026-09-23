import {defineStore} from 'pinia'

export type MonsoonConfig = {
  apiBaseUrl?: string,
  monsoonEnv?: string,
  timezone?: string
}

export const useContextStore = defineStore('context', {
  state: () => ({
    config: {} as MonsoonConfig
  }),
  actions: {
    setConfig(config: MonsoonConfig) {
      this.config = config
    }
  }
})
