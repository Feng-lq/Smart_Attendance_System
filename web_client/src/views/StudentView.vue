<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, UploadFilled } from '@element-plus/icons-vue'
// 导入封装好的接口 👈
import { getStudents, getAllClasses, createStudent, deleteStudent } from '@/api/students'

const students = ref([])
const classes = ref([]) 
const dialogVisible = ref(false)
const isLoading = ref(false)
const previewUrl = ref('') 

const form = reactive({
  name: '',
  student_id: '',
  email: '',
  class_id: ''
})
const uploadFile = ref(null)

const baseURL = 'http://127.0.0.1:8000'

const getImageUrl = (path) => {
  if (!path) {
    console.warn("⚠️ [前端日志] 图片路径为空");
    return '';
  }
  if (path.startsWith('http')) return path
  
  // 拼接逻辑：后端地址 + 数据库里的相对路径
  // 例如：http://127.0.0.1:8000 + /static/avatars/xxx.jpg
  return baseURL + path
}

// 1. 获取班级列表
const fetchClasses = async () => {
  try {
    const response = await getAllClasses() // 使用封装接口
    classes.value = response
  } catch (error) {
    console.error('获取班级失败', error)
  }
}

// 2. 获取学生列表
const fetchStudents = async () => {
  try {
    const response = await getStudents() // 使用封装接口
    students.value = response
  } catch (error) {
    ElMessage.error('获取列表失败')
  }
}

const handleFileChange = (file) => {
  uploadFile.value = file.raw 
  previewUrl.value = URL.createObjectURL(file.raw)
}

// 3. 提交新学生
const handleSubmit = async () => {
  if (!form.name || !form.student_id || !form.email || !form.class_id || !uploadFile.value) {
    ElMessage.warning('请填写完整信息并上传照片')
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

    // 使用封装接口 👈
    await createStudent(formData)

    ElMessage.success('录入成功！')
    dialogVisible.value = false
    
    // 重置逻辑保持不变
    Object.assign(form, { name: '', student_id: '', email: '', class_id: '' })
    uploadFile.value = null
    previewUrl.value = '' 
    fetchStudents() 
  } catch (error) {
    const detail = error.response?.data?.detail
    ElMessage.error(detail || '添加失败，请重试')
  } finally {
    isLoading.value = false
  }
}

// 4. 删除学生
const handleDelete = (id) => {
  ElMessageBox.confirm('确定要删除该学生吗?', '警告', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteStudent(id) // 使用封装接口
      ElMessage.success('删除成功')
      fetchStudents()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

onMounted(() => {
  fetchClasses()
  fetchStudents()
})
</script>

<template>
  <div class="student-container">
    <div class="header-actions">
      <h2>学生信息管理</h2>
      <el-button type="primary" :icon="Plus" @click="dialogVisible = true">
        录入学生
      </el-button>
    </div>

    <el-table :data="students" style="width: 100%" border stripe>
      <el-table-column prop="student_id" label="学号" width="120" />
      
    <el-table-column label="照片" width="100">
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
      
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="email" label="邮箱" />
      
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <el-button type="danger" :icon="Delete" circle @click="handleDelete(scope.row.id)" />
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="采集学生人脸信息" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="所属班级">
          <el-select v-model="form.class_id" placeholder="请选择班级" style="width: 100%">
            <el-option v-for="item in classes" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>

        <el-form-item label="学号">
          <el-input v-model="form.student_id" />
        </el-form-item>

        <el-form-item label="电子邮箱">
          <el-input v-model="form.email" />
        </el-form-item>

        <el-form-item label="人脸照片">
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
              <div class="el-upload__text">将照片拖到此处，或 <em>点击上传</em></div>
            </div>
          </el-upload>
          <div class="tips">上传单人正脸照，背景尽量纯净。</div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="isLoading">确定录入</el-button>
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

/* 🚀 样式修改点：美化拖拽框和预览图 */
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

/* 如果图片加载失败显示的占位符样式 */
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