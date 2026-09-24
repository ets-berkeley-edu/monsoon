import {defineStore} from 'pinia'

export type MonsoonConfig = {
  apiBaseUrl?: string,
  monsoonEnv?: string,
  tenantSlug?: string | null,
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
