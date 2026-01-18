import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import StudentView from '../views/StudentView.vue' 
import ClassView from '../views/ClassView.vue'
import ClassAttendance from '../views/AttendanceView.vue'
import HistoryView from '../views/HistoryView.vue'
import AnalyticsView from '../views/AnalyticsView.vue'
import StudentPortal from '../views/StudentPortal.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView
    },
    // 🔥 2. 新增学生端独立路由 (放在 Dashboard 外面)
    {
      path: '/student',
      name: 'student-portal',
      component: StudentPortal,
      meta: { title: '学生考勤查询' }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      // 配置子路由
      children: [
        {
          path: 'class', // 访问路径: /dashboard/class
          name: 'class',
          component: ClassView
        },
        {
          path: 'student', // 访问路径是 /dashboard/student
          name: 'student',
          component: StudentView
        },
        {
          path: 'attendance', 
          name: 'attendance',
          component: ClassAttendance
        },
        {
          path: 'history', // 👈 2. 新增路由配置 (访问地址: /dashboard/history)
          name: 'history',
          component: HistoryView
        },
        {
          path: 'analytics',
          name: 'analytics',
          component: AnalyticsView
        }
      ]
    }
  ]
})

export default router