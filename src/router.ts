import {createRouter, createWebHistory} from 'vue-router'
import {requiresTool} from '@/lib/auth'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/default/Default.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue')
      },
      {
        path: '/tools/bulk-media-uploader',
        name: 'BulkMediaUploader',
        component: () => import('@/views/BulkMediaUploader.vue'),
        beforeEnter: requiresTool('bulk_media_uploader')
      },
      {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('@/views/NotFound.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
