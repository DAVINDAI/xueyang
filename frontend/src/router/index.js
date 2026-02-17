import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/stats',
      name: 'stats',
      component: () => import('../views/StatsPage.vue')
    },
    {
      path: '/details',
      name: 'details',
      component: () => import('../views/DetailsPage.vue')
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('../views/ChatPage.vue')
    },
    {
      path: '/memo',
      name: 'memo',
      component: () => import('../views/MemoPage.vue')
    }
  ]
})

export default router
