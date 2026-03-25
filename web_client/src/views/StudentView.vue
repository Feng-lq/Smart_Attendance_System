<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, UploadFilled, Picture } from '@element-plus/icons-vue'
// Import encapsulated APIs / 导入封装好的接口 👈
import { getStudents, getAllClasses, createStudent, deleteStudent } from '@/api/students'

// State management / 状态管理
const students = ref([])
const classes = ref([]) 
const dialogVisible = ref(false)
const isLoading = ref(false)
const previewUrl = ref('') 
const selectedClassId = ref('')

const form = reactive({
  name: '',
  student_id: '',
  email: '',
  class_id: ''
})
const uploadFile = ref(null)

// 🚀 [Optimized] Replaced hardcoded IP with Environment Variable
// 🚀 [优化提升] 引入环境变量 baseURL，为云端部署做准备
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

// Image path resolver / 图片路径拼接函数
const getImageUrl = (path) => {
  if (!path) return ''; // Eliminate useless warnings / 消除无用警告
  if (path.startsWith('http')) return path
  return baseURL + (path.startsWith('/') ? path : '/' + path)
}

// Map class_id to class name / 将 class_id 映射为班级名称
const getClassName = (classId) => {
  const targetClass = classes.value.find(c => c.id === classId)
  return targetClass ? targetClass.name : 'Unknown'
}

// 1. Fetch class list / 获取班级列表
const fetchClasses = async () => {
  try {
    const response = await getAllClasses()
    classes.value = Array.isArray(response) ? response : (response.data || [])
  } catch (error) {
    console.error('❌ [StudentView] Fetch classes error:', error)
  }
}

// 2. Fetch student list / 获取学生列表 (🚀 支持传入 class_id 进行筛选)
const fetchStudents = async () => {
  try {
    const params = selectedClassId.value ? { class_id: selectedClassId.value } : {}
    const response = await getStudents(params) 
    students.value = Array.isArray(response) ? response : (response.data || [])
  } catch (error) {
    console.error('❌ [StudentView] Fetch students error details:', error.response?.data || error)
    ElMessage.error('Failed to load student list')
  }
}

// Triggered when dropdown filter changes / 下拉框改变时触发刷新
const handleFilterChange = () => {
  fetchStudents()
}

// Handle local file selection and preview / 处理本地文件选择与预览
const handleFileChange = (file) => {
  uploadFile.value = file.raw 
  previewUrl.value = URL.createObjectURL(file.raw)
}

// 3. Submit new student / 提交新学生
const handleSubmit = async () => {
  if (!form.name || !form.student_id || !form.email || !form.class_id || !uploadFile.value) {
    ElMessage.warning('Please fill in all fields and upload a photo')
    return
  }

  isLoading.value = true
  try {
    const formData = new FormData()
    formData.append('name', form.name)
    formData.append('student_id', form.student_id)
    formData.append('email', form.email)
    formData.append('class_id', form.class_id)
    formData.append('file', uploadFile.value)

    await createStudent(formData)

    ElMessage.success('Registration successful!')
    dialogVisible.value = false
    
    // Reset form / 重置表单逻辑
    Object.assign(form, { name: '', student_id: '', email: '', class_id: '' })
    uploadFile.value = null
    previewUrl.value = '' 

    // Refresh current view / 录入完顺便刷新当前视角
    fetchStudents() 
  } catch (error) {
    console.error("❌ [StudentView] Create error:", error)
    const detail = error.response?.data?.detail
    ElMessage.error(detail || 'Failed to add student')
  } finally {
    isLoading.value = false
  }
}

// 4. Delete student / 删除学生
const handleDelete = (id) => {
  ElMessageBox.confirm(
    'Are you sure you want to delete this student?', 
    'Warning / 警告', 
    {
      confirmButtonText: 'Delete / 删除',
      cancelButtonText: 'Cancel / 取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await deleteStudent(id)
      ElMessage.success('Deleted successfully')
      fetchStudents()
    } catch (error) {
      console.error("❌ [StudentView] Delete error:", error)
      ElMessage.error('Failed to delete')
    }
  }).catch(() => {})
}

onMounted(() => {
  // Chain promises: Ensure classes are loaded BEFORE students for proper name mapping
  // 保证先获取到班级列表后，再获取学生（这样表格里的班级名称才能正确匹配）
  fetchClasses().then(() => {
    fetchStudents()
  })
})
</script>

<template>
  <div class="student-container">
    <div class="header-actions">
      <div class="left-actions">
        <h2>Student Management</h2>
        <el-select 
          v-model="selectedClassId" 
          placeholder="All Classes" 
          clearable 
          @change="handleFilterChange"
          class="filter-select"
        >
          <el-option label="All Classes" value="" />
          <el-option 
            v-for="item in classes" 
            :key="item.id" 
            :label="item.name" 
            :value="item.id" 
          />
        </el-select>
      </div>
        
      <el-button type="primary" :icon="Plus" @click="dialogVisible = true">
        Add Student 
      </el-button>
    </div>

    <el-table :data="students" style="width: 100%" border stripe empty-text="No Data">
      <el-table-column prop="student_id" label="Student ID" width="140" align="center" />
      
      <el-table-column label="Photo" width="100" align="center">
        <template #default="scope">
          <el-image 
            style="width: 50px; height: 50px; border-radius: 4px"
            :src="getImageUrl(scope.row.photo_path)"
            :preview-src-list="[getImageUrl(scope.row.photo_path)]"
            preview-teleported
            fit="cover"
          >
            <template #error>
              <div class="image-slot">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </template>
      </el-table-column>
      
      <el-table-column prop="name" label="Name" width="120" />
      
      <el-table-column label="Class" width="150" align="center">
        <template #default="scope">
          <el-tag type="info" effect="plain">{{ getClassName(scope.row.class_id) }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="email" label="Email" min-width="180" />
      
      <el-table-column label="Action" width="100" align="center" fixed="right">
        <template #default="scope">
          <el-button type="danger" :icon="Delete" circle @click="handleDelete(scope.row.id)" />
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="Capture Face Info" width="500px" destroy-on-close>
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item label="Class">
          <el-select v-model="form.class_id" placeholder="Select Class" style="width: 100%">
            <el-option v-for="item in classes" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="Name">
          <el-input v-model="form.name" placeholder="Real name" />
        </el-form-item>

        <el-form-item label="ID">
          <el-input v-model="form.student_id" placeholder="Student ID" />
        </el-form-item>

        <el-form-item label="Email">
          <el-input v-model="form.email" placeholder="For notifications" />
        </el-form-item>

        <el-form-item label="Face">
          <el-upload
            class="face-uploader"
            drag
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileChange"
            accept="image/*"
          >
            <img v-if="previewUrl" :src="previewUrl" class="preview-img" />
            <div v-else class="upload-placeholder">
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">Drag photo here or <em>click to upload</em></div>
            </div>
          </el-upload>
          <div class="tips">* Single clear face shot, clean background</div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="isLoading">Register</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.left-actions {
  display: flex;
  align-items: center;
}
.left-actions h2 {
  margin: 0;
  margin-right: 20px;
  color: #303133;
}
.filter-select {
  width: 200px;
}

.face-uploader {
  width: 100%;
}
:deep(.el-upload-dragger) {
  padding: 10px;
  border: 1px dashed #dcdfe6;
}
:deep(.el-upload-dragger:hover) {
  border-color: #409eff;
}

.preview-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 4px;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.el-icon--upload {
  font-size: 40px;
  color: #909399;
  margin-bottom: 8px;
}

.tips {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
  line-height: 1.4;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 20px;
}
</style>