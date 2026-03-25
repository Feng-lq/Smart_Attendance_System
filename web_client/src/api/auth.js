// web_client/src/api/auth.js
import request from './index'

// 1. Login API endpoint
// 1. 登录接口

export function login(data) {
  return request({
    url: '/auth/token',  
    method: 'post',
    data: data           
  })
}

// 2. Fetch user profile
// 2. 获取用户信息 (预留接口，如果以后需要单独获取用户详情)
export function getInfo() {
  return request({
    url: '/auth/me',
    method: 'get'
  })
}

// 3. Update User Password
// 3. 修改用户密码 (学生/管理员通用)
export function updatePassword(data) {
  // data 结构: { old_password: '...', new_password: '...' }
  return request.put('/auth/password', data)
}