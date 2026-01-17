import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  // 👈 关键点：统一加上 /api，这样以后后端改地址你只需要改这里
  baseURL: 'http://127.0.0.1:8000/api', 
  timeout: 15000 // 考勤识别较慢，建议设置长一点
})

// 响应拦截器：统一处理错误提示
request.interceptors.response.use(
  response => response.data,
  error => {
    ElMessage.error(error.response?.data?.detail || '网络请求失败')
    return Promise.reject(error)
  }
)

export default request