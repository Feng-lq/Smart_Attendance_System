<script setup>
import { ref, onMounted } from 'vue'
// Import encapsulated API methods / 导入封装后的接口 👈
import { getClasses, createClass, deleteClass } from '@/api/classes'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, School } from '@element-plus/icons-vue'

// State management / 数据状态
const classes = ref([])
const newClassName = ref('')
const isLoading = ref(false)

// 1. Fetch class list / 获取班级列表
const fetchClasses = async () => {
  try {
    const res = await getClasses()
    // 🚀 [Optimized] Robust parsing: Handle differences between raw Axios response and intercepted data
    // 🚀 [优化提升] 强健解析：兼容带有 data 包装的 Axios 原生响应和拦截器解包后的响应
    classes.value = res.data || res 
  } catch (error) {
    console.error("❌ [ClassView] Fetch error:", error)
    ElMessage.error('Failed to fetch class list / 获取班级列表失败')
  }
}

// 2. Create new class / 创建新班级
const handleCreateClass = async () => {
  if (!newClassName.value.trim()) {
    ElMessage.warning('Please enter a class name / 请输入班级名称')
    return
  }
  
  isLoading.value = true
  try {
    await createClass(newClassName.value.trim())
    ElMessage.success('Class created successfully / 班级创建成功')
    newClassName.value = ''
    fetchClasses() // Refresh list / 刷新列表
  } catch (error) {
    console.error("❌ [ClassView] Create error:", error)
    ElMessage.error(error.response?.data?.detail || 'Failed to create / 创建失败')
  } finally {
    isLoading.value = false
  }
}

// 3. Delete class / 删除班级
const handleDeleteClass = (cls) => {
  // Defensive programming: Prevent accidental deletion of classes with students
  // 防御性编程：防止误删有学生的班级
  if (cls.student_count > 0) {
    ElMessage.error('Cannot delete: Please remove all students from this class first / 该班级内已有学生，请先移除学生再删除班级')
    return
  }

  ElMessageBox.confirm(
    `Are you sure you want to delete class [${cls.name}]? / 确定要删除班级 [${cls.name}] 吗?`, 
    'Warning / 警告', 
    {
      confirmButtonText: 'Delete / 确定删除',
      cancelButtonText: 'Cancel / 取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteClass(cls.id)
      ElMessage.success('Deleted successfully')
      fetchClasses() // Refresh list / 刷新列表
    } catch (error) {
      console.error("❌ [ClassView] Delete error:", error)
      ElMessage.error(error.response?.data?.detail || 'Failed to delete')
    }
  }).catch(() => {
    // User canceled / 用户取消
  })
}

onMounted(fetchClasses)
</script>

<template>
  <div class="class-container">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <div class="title-group">
            <el-icon><School /></el-icon>
            <h2>Class Architecture Management</h2>
          </div>
          <div class="add-bar">
            <el-input 
              v-model="newClassName" 
              placeholder="Enter class name (e.g., CS101)" 
              style="width: 250px; margin-right: 10px"
              @keyup.enter="handleCreateClass"
            />
            <el-button type="primary" :icon="Plus" @click="handleCreateClass" :loading="isLoading">
              Create Class
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="classes" style="width: 100%" stripe border empty-text="No Data">
        <el-table-column prop="id" label="ID" width="100" align="center" />
        <el-table-column prop="name" label="Class Name" />
        <el-table-column prop="student_count" label="Enrolled Students" width="220" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.student_count > 0 ? 'success' : 'info'">
              {{ scope.row.student_count }} Students
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" align="center">
          <template #default="scope">
            <el-button 
              type="danger" 
              :icon="Delete" 
              circle 
              @click="handleDeleteClass(scope.row)" 
              :disabled="scope.row.student_count > 0"
            />
          </template>
        </el-table-column>
      </el-table>
      
      <div class="tips">
        <p>* Note: A class can only be deleted when its student count is 0.</p>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.class-container { max-width: 900px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; }
.title-group { display: flex; align-items: center; gap: 10px; }
.title-group h2 { margin: 0; font-size: 18px; color: #303133; }
.add-bar { display: flex; }
.tips { margin-top: 20px; color: #909399; font-size: 13px; }
</style>