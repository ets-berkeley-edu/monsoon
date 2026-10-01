import {defineStore} from 'pinia'

export type Tool = {
  key: string,
  name: string
}

export type MonsoonConfig = {
  apiBaseUrl?: string,
  availableTools?: Tool[],
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
