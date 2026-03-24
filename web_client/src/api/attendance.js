// web_client/src/api/attendance.js
import request from './index'

// 1. 获取班级列表
// (保留这个函数，因为 AttendanceView.vue 需要它)
export function getClasses() {
  return request.get('/classes')
}

// 2. 提交合照识别
export function analyzeClassPhoto(formData) {
  // 🔥 关键修改：把地址改为新的 /attendance/recognize
  return request.post('/attendance/recognize', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 3. 获取历史记录
// (保留原名 getHistory，防止其他页面报错)
export function getHistory(params) {
  return request.get('/attendance/history', { params })
}

// 4. 发送通知 (新增，如果你后续要用手动通知功能)
export function sendNotification(data) {
  return request.post('/attendance/notify', data)
}