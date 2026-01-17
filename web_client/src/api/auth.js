// src/api/auth.js
import request from './index' // 这里的 request 基础路径已配置为 /api

/**
 * 登录接口
 * @param {URLSearchParams} formData 包含 username 和 password
 */
export function login(formData) {
  return request.post('/token', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}