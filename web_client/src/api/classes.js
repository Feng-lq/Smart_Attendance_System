// src/api/classes.js
import request from './index' // 假设 index.js 中 baseURL 为 /api

// 1. 获取班级列表及人数统计
export function getClasses() {
  return request.get('/classes')
}

// 2. 创建新班级
export function createClass(name) {
  const formData = new FormData()
  formData.append('name', name)
  return request.post('/classes', formData)
}

// 3. 删除班级
export function deleteClass(id) {
  return request.delete(`/classes/${id}`)
}