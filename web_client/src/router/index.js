// web_client/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

// Eager load ONLY the login view for fastest initial render
// 仅对登录页进行同步加载，保证首屏瞬间渲染完毕
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
      meta: { title: 'Login' }
    },
    {
      path: '/student',
      name: 'student-portal',
      component: () => import('../views/StudentPortal.vue'),
      meta: { title: 'Student Portal / 学生考勤查询', requiresAuth: true } 
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      // Protect the entire dashboard area / 保护整个后台区域
      meta: { requiresAuth: true }, 
      // Configure child routes / 配置子路由
      children: [
        {
          path: 'class', 
          name: 'class',
          component: () => import('../views/ClassView.vue')
        },
        {
          path: 'student', 
          name: 'student',
          component: () => import('../views/StudentView.vue')
        },
        {
          path: 'attendance', 
          name: 'attendance',
          component: () => import('../views/AttendanceView.vue')
        },
        {
          path: 'history', 
          name: 'history',
          component: () => import('../views/HistoryView.vue')
        },
        {
          path: 'analytics',
          name: 'analytics',
          component: () => import('../views/AnalyticsView.vue')
        }
      ]
    }
  ]
})

// Global Navigation Guard for Frontend Security
// 全局路由守卫 (Navigation Guard)：防止未登录用户“翻墙”
router.beforeEach((to, from, next) => {
  // Check if token exists in local storage
  // 检查本地是否存在 Token
  const isAuthenticated = localStorage.getItem('token')
  
  // If the route requires auth and the user is not logged in
  // 如果目标路由需要权限 (requiresAuth)，且用户当前没有 Token
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Kick back to login page
    // 拦截请求，强制踢回登录页
    next({ name: 'login' }) 
  } else {
    // Otherwise, proceed normally
    // 否则，正常放行
    next() 
  }
})

export default router