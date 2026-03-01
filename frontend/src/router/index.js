import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginPage.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('../views/ChatPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/details',
      name: 'details',
      component: () => import('../views/DetailsPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/memo',
      name: 'memo',
      component: () => import('../views/MemoPage.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/stats',
      name: 'stats',
      component: () => import('../views/StatsPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/resume',
      name: 'resume',
      component: () => import('../views/ResumeOptimizer.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/resume/list',
      name: 'resumeList',
      component: () => import('../views/ResumeList.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  const requiresAuth = to.meta.requiresAuth !== false
  
  // 检查用户是否登录
  const isLoggedIn = !!localStorage.getItem('token')
  
  if (requiresAuth && !isLoggedIn) {
    // 未登录，重定向到登录页面
    next('/login')
  } else if (to.path === '/login' && isLoggedIn) {
    // 已登录，重定向到首页
    next('/')
  } else {
    // 正常跳转
    next()
  }
})

export default router
