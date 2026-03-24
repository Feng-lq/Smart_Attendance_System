// src/api/students.js
import request from './index' // 导入你配置了 baseURL: '/api' 的 axios 实例

// 获取所有学生
export function getStudents(params) {
  return request.get('/students', { params })
}

// 获取所有班级 (用于下拉菜单)
export function getAllClasses() {
  return request.get('/classes')
}

// 录入新学生 (Multipart 表单)
export function createStudent(formData) {
  return request.post('/students', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 删除学生
export function deleteStudent(id) {
  return request.delete(`/students/${id}`)
}

// 根据学号查询考勤详情
export function queryStudentAttendance(studentId) {
  return request.get(`/student/portal/${studentId}`)
}