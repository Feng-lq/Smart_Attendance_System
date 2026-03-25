// web_client/src/api/students.js
import request from './index' // Import the Axios instance with baseURL / 导入配置了 baseURL 的 axios 实例

// 1. Fetch all students
// 1. 获取所有学生 (支持分页或条件过滤)
export function getStudents(params) {
  return request.get('/students', { params })
}

// 2. Fetch all classes (used for dropdown menus)
// 2. 获取所有班级 (用于录入学生时的班级下拉菜单)
export function getAllClasses() {
  return request.get('/classes')
}

// 3. Register a new student (Multipart form data for photo upload)
// 3. 录入新学生 (包含照片上传)
export function createStudent(formData) {
  return request.post('/students', formData)
}

// 4. Delete a student
// 4. 删除学生
export function deleteStudent(id) {
  return request.delete(`/students/${id}`)
}

// 5. Query attendance details by student ID (Student Portal)
// 5. 根据学号查询考勤详情 (学生端门户)
export function queryStudentAttendance(studentId) {
  return request.get(`/student/portal/${studentId}`)
}