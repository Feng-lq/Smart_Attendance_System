// web_client/src/api/auth.js
import request from './index'

// 登录接口
// data 结构: { username: '', password: '', role: 'admin' | 'student' }
export function login(data) {
  return request({
    url: '/auth/token',  // 对应后端的 @router.post("/auth/token")
    method: 'post',
    data: data           // Axios 默认会以 application/json 发送
  })
}

// 获取用户信息 (预留接口，如果以后需要单独获取用户详情)
export function getInfo() {
  return request({
    url: '/auth/me',
    method: 'get'
  })
}