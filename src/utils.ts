export function apiBaseUrl (): string {
  const port = import.meta.env.VITE_APP_API_PORT
  return port ? `${window.location.protocol}//${window.location.hostname}:${port}` : import.meta.env.VITE_APP_API_BASE_URL
}
