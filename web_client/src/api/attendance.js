// web_client/src/api/attendance.js
import request from './index'

// 1. Fetch the list of classes
// 1. 获取班级列表
export function getClasses() {
  return request.get('/classes')
}

// 2. Submit class group photo for recognition
// 2. 提交合照进行识别
export function analyzeClassPhoto(formData) {
  return request.post('/attendance/recognize', formData)
}

// 3. Fetch attendance history
// 3. 获取考勤历史记录
export function getHistory(params) {
  return request.get('/attendance/history', { params })
}

// 4. Send absent notification
// 4. 发送缺勤通知
export function sendNotification(data) {
  return request.post('/attendance/notify', data)
}