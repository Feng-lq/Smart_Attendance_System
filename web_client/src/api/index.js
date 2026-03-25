// web_client/src/api/index.js
import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000/api', 
  // Attendance recognition can be slow, set a longer timeout (15s)
  // 考勤识别较慢，建议设置长一点 (15秒)
  timeout: 15000 
})

// 🚀 [Optimized] Request Interceptor: Automatically inject JWT Token
// 🚀 [优化提升] 请求拦截器：在每次发请求前，自动挂载 JWT Token
request.interceptors.request.use(
  config => {
    // Retrieve token from local storage (Make sure your login page saves it here!)
    // 从本地存储获取 Token (请确保你的登录页把它存到了这里！)
    const token = localStorage.getItem('token')
    if (token) {
      // Standard OAuth2 / JWT header format
      // 标准的 OAuth2 / JWT 请求头格式
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response Interceptor: Unified error handling
// 响应拦截器：统一处理错误提示与身份失效
request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response && error.response.status === 401) {
      ElMessage.error('Session expired, please log in again / 登录已过期，请重新登录')
      localStorage.removeItem('token')
      
      // Prevent redirecting if already on login page
      // 防止在登录页无限重定向
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    } else {
      // Default error message
      // 默认的后端报错提取
      ElMessage.error(error.response?.data?.detail || 'Network request failed / 网络请求失败')
    }
    
    return Promise.reject(error)
  }
)

export default request