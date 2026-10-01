import {defineStore} from 'pinia'

export type MonsoonConfig = {
  apiBaseUrl?: string,
  monsoonEnv?: string,
  tenantSlug?: string | null,
  timezone?: string
}

export type CurrentUser = {
  username: string | null
}

export const useContextStore = defineStore('context', {
  state: () => ({
    config: {} as MonsoonConfig,
    currentUser: {username: null} as CurrentUser
  }),
  actions: {
    setConfig(config: MonsoonConfig) {
      this.config = config
    },
    setCurrentUser(currentUser: CurrentUser) {
      this.currentUser = currentUser
    }
  }
})
