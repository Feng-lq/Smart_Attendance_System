// web_client/src/stores/userStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login } from '@/api/auth'
import router from '@/router' 

export const useUserStore = defineStore('user', () => {
  // Initialize state from local storage to persist session across page reloads
  // 从本地存储初始化状态，保证刷新页面后登录状态不丢失
  const token = ref(localStorage.getItem('token') || '')
  const role = ref(localStorage.getItem('role') || '') 
  const name = ref(localStorage.getItem('name') || '')

  const loginAction = async (loginForm) => {
    try {
      // 1. Send login request
      // 1. 发送请求
      const res = await login(loginForm)
      
      // 🔍 Debugging: Check the complete response in the browser console (F12)
      // 🔍 调试：请在浏览器控制台(F12)查看这个输出
      console.log("[UserStore] Full backend response:", res)

      // 2. Smart data extraction (Compatible with/without Axios response interceptors)
      // 2. 智能获取数据 (兼容是否有拦截器解包的情况)
      // If `res` directly contains access_token, the interceptor unpacked it. Otherwise, check `res.data`.
      const data = res.access_token ? res : (res.data || {})

      if (!data.access_token) {
        console.error("[UserStore] Failed to parse Token, invalid data structure:", data)
        return false
      }

      // 3. Extract fields
      // 3. 提取字段
      const accessToken = data.access_token
      const userRole = data.role
      
      if (!userRole) {
         console.warn("[UserStore] Backend did not return a 'role' field. Please check auth.py")
      }

      // 4. Update state and LocalStorage
      // 4. 保存状态
      token.value = accessToken
      role.value = userRole || 'admin' 
      name.value = loginForm.username 

      localStorage.setItem('token', accessToken)
      localStorage.setItem('role', userRole || 'admin')
      localStorage.setItem('name', loginForm.username)

      console.log("[UserStore] Login successful, redirecting...")

      // 5. Role-Based Routing
      // 5. 基于角色的路由分流
      if (role.value === 'admin') {
        // Teachers/Admins redirect to the Class Management dashboard
        // 教师跳转到仪表盘的班级管理页 (更常用)
        router.push('/dashboard/class')
      } else {
        // Students redirect to the portal and pass the student ID automatically!
        // 学生跳转到门户页，并携带学号参数，实现自动查询！
        router.push({ 
          path: '/student', 
          query: { id: loginForm.username } 
        })
      }
      
      return true
    } catch (error) {
      console.error("[UserStore] Exception occurred during login:", error)
      return false
    }
  }

  const logoutAction = () => {
    // Clear state in memory
    // 清除内存中的状态
    token.value = ''
    role.value = ''
    name.value = ''
    
    // Clear persistent storage
    // 清除持久化存储
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('name')
    
    // Redirect to login page
    // 踢回登录页
    router.push('/')
  }

  return { 
    token, 
    role, 
    name, 
    loginAction, 
    logoutAction 
  }
})