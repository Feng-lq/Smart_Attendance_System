// web_client/src/api/classes.js
import request from './index' 

// 1. Fetch class list and student count statistics
// 1. 获取班级列表及人数统计
export function getClasses() {
  return request.get('/classes')
}

// 2. Create a new class
// 2. 创建新班级 
export function createClass(name) {
  return request.post('/classes', { name: name })
}

// 3. Delete a class
// 3. 删除班级
export function deleteClass(id) {
  return request.delete(`/classes/${id}`)
}