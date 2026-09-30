import axios from 'axios'
import {apiBaseUrl} from '@/utils'

const client = () => axios.create({baseURL: apiBaseUrl(), withCredentials: true})

export function login (username: string, password: string) {
  return client().post('/api/auth/login', {username, password}).then(response => response.data)
}

export function logout () {
  return client().post('/api/auth/logout').then(response => response.data)
}

export function fetchAuthStatus () {
  return client().get('/api/auth/status').then(response => response.data)
}
