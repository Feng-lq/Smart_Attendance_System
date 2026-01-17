import request from './index'

// 获取班级列表
export function getClasses() {
  return request.get('/classes')
}

// 提交合照识别
export function analyzeClassPhoto(formData) {
  return request.post('/attendance/class_photo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取历史记录 👈
export function getHistory() {
  return request.get('/attendance/history')
}