// web_client/src/stores/userStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login } from '@/api/auth'
import router from '@/router' 

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const role = ref(localStorage.getItem('role') || '') 
  const name = ref(localStorage.getItem('name') || '')

  const loginAction = async (loginForm) => {
    try {
      // 1. 发送请求
      const res = await login(loginForm)
      
      // 🔍 调试：请在浏览器控制台(F12)查看这个输出
      console.log("🔥 后端返回的完整响应:", res)

      // 2. 智能获取数据 (兼容是否有拦截器的情况)
      // 如果 res 直接包含 access_token，说明拦截器已经解包了
      // 如果 res.data 包含 access_token，说明是原生 Axios 响应
      const data = res.access_token ? res : (res.data || {})

      if (!data.access_token) {
        console.error("❌ 无法解析 Token，数据结构不对:", data)
        return false
      }

      // 3. 提取字段
      const accessToken = data.access_token
      const userRole = data.role
      // 如果后端没返回 role，我们先做个防错，默认为 admin (或者根据逻辑处理)
      if (!userRole) {
         console.warn("⚠️ 后端未返回 role 字段，请检查 auth.py 返回值")
      }

      // 4. 保存状态
      token.value = accessToken
      role.value = userRole || 'admin' 
      name.value = loginForm.username 

      localStorage.setItem('token', accessToken)
      localStorage.setItem('role', userRole || 'admin')
      localStorage.setItem('name', loginForm.username)

      console.log("✅ 登录成功，准备跳转...")

      // 5. 跳转
      if (role.value === 'admin') {
        router.push('/dashboard')
      } else {
        router.push('/student/my-attendance')
      }
      
      return true
    } catch (error) {
      console.error("❌ 登录过程发生异常:", error)
      return false
    }
  }

  const logoutAction = () => {
    token.value = ''
    role.value = ''
    name.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('name')
    router.push('/login')
  }

  return { 
    token, 
    role, 
    name, 
    loginAction, 
    logoutAction 
  }
})