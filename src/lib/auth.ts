import {useContextStore} from '@/stores/context'

export function requiresTool(toolKey: string) {
  return (to: any, from: any, next: any) => {
    const context = useContextStore()
    const isLoggedIn = !!context.currentUser.username
    const isAvailable = (context.config.availableTools || []).some(tool => tool.key === toolKey)
    if (isLoggedIn && isAvailable) {
      next()
    } else {
      next({path: '/'})
    }
  }
}
