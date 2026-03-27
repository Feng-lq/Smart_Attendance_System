<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import { UploadFilled, Message, Check, Close } from '@element-plus/icons-vue'
import { getClasses, analyzeClassPhoto, sendNotification } from '@/api/attendance'

const classes = ref([])
const selectedClassId = ref(null)
const uploadFile = ref(null)
const previewUrl = ref('')
const isProcessing = ref(false)
const isSending = ref(false) 
const result = ref(null) 

// Replaced hardcoded IP with Environment Variable fallback
// 移除写死的 127.0.0.1，改用 Vite 环境变量，为未来部署服务器做准备
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

// Image URL builder / 图片路径拼接函数
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const cleanPath = path.startsWith('/') ? path : '/' + path
  return baseURL + cleanPath
}

// 1. Fetch class list / 获取班级列表
const fetchClasses = async () => {
  try {
    const res = await getClasses()
    // Error prevention: Handle different Axios wrapper returns
    // 防错处理：有些 axios 封装会返回 res，有些返回 res.data
    classes.value = Array.isArray(res) ? res : (res.data || [])
  } catch (error) {
    console.error("❌ [Attendance] Fetch classes error:", error)
    ElMessage.error('Failed to load class list. Is the backend running?')
  }
}

// 2. Handle file selection / 选择照片
const handleFileChange = (file) => {
  uploadFile.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
  result.value = null 
}

// 3. Submit for analysis / 提交识别
const handleAnalyze = async () => {
  if (!selectedClassId.value || !uploadFile.value) {
    ElMessage.warning('Please select a class and upload a photo')
    return
  }
  
  isProcessing.value = true
  try {
    const formData = new FormData()
    formData.append('class_id', selectedClassId.value)
    formData.append('file', uploadFile.value)

    const response = await analyzeClassPhoto(formData)
    
    // Debug log / 调试日志
    console.log("📦 [Attendance] Backend Analysis Result:", response)
    
    result.value = response
    ElMessage.success('Recognition and annotation completed!')
  } catch (error) {
    console.error("❌ [Attendance] Analysis error:", error)
    const detail = error.response?.data?.detail || 'Server connection timeout'
    ElMessage.error('Recognition failed: ' + detail)
  } finally {
    isProcessing.value = false
  }
}

// 4. Send absent notifications / 通知缺勤
const notifyAbsentees = () => {
  if (!result.value || result.value.absent_count === 0) return

  ElMessageBox.confirm(
    `Are you sure you want to send warning emails to these ${result.value.absent_count} students?`,
    'Batch Notification',
    {
      confirmButtonText: 'Send Now',
      cancelButtonText: 'Cancel',
      type: 'warning',
      icon: Message
    }
  ).then(async () => {
    isSending.value = true
    try {
      // REAL backend API call
      // 接通了真实的后端邮件发送 API！
      await sendNotification({ session_id: result.value.id })
      
      ElNotification({
        title: 'Notification Sent',
        message: `Emails for session ${result.value.id} have been dispatched.`,
        type: 'success'
      })
    } catch (error) {
      console.error("❌ [Attendance] Notification error:", error)
      ElMessage.error('Failed to send emails')
    } finally {
      isSending.value = false
    }
  }).catch(() => {
    // User canceled / 用户取消操作
  })
}

onMounted(fetchClasses)
</script>

<template>
  <div class="container">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <h2>📸 AI Attendance Recognition</h2>
          <p class="subtitle">Upload a class group photo. The system will auto-match and record attendance.</p>
        </div>
      </template>

      <div class="setup-grid">
        <div class="step-section">
          <span class="label"> Select Class </span>
          <el-select v-model="selectedClassId" placeholder="Select a class" size="large" style="width: 240px">
            <el-option
              v-for="cls in classes"
              :key="cls.id"
              :label="cls.name"
              :value="cls.id"
            />
          </el-select>
        </div>
      </div>

    <div class="upload-section">
    <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileChange"
        accept="image/*"
    >
        <img 
        v-if="result && result.result_img" 
        :src="getImageUrl(result.result_img)" 
        class="preview-img result-img" 
        />
        
        <img 
        v-else-if="previewUrl" 
        :src="previewUrl" 
        class="preview-img" 
        />
        
        <div v-else class="placeholder">
        <el-icon class="icon"><upload-filled /></el-icon>
        <div class="text">Drag class photo here, or <em>click to upload</em></div>
        </div>
    </el-upload>
    
    <div v-if="result && result.result_img" class="img-tips">
        Green Box: Recognized | Red Box: Unmatched 
    </div>
    </div>

      <el-button 
        type="primary" 
        size="large" 
        class="action-btn"
        :loading="isProcessing"
        @click="handleAnalyze"
        :disabled="!selectedClassId || !uploadFile"
      >
        {{ isProcessing ? 'Deep Scanning...' : 'Start Recognition' }}
      </el-button>

      <div v-if="result" class="result-section">
        <div class="session-info">
          <el-tag type="info" effect="plain">Session ID{{ result.id }}</el-tag>
        </div>

        <el-row :gutter="20">
          <el-col :span="10">
            <el-card class="result-card present" shadow="never">
              <template #header>
                <div class="card-head success">
                  <el-icon><Check /></el-icon> Present ({{ result.present_count }})
                </div>
              </template>
              <div class="name-container">
                <el-tag 
                  v-for="stu in result.present_students" 
                  :key="stu.id" 
                  type="success" 
                  class="name-tag"
                  effect="light"
                >
                  {{ stu.name }}
                </el-tag>
              </div>
            </el-card>
          </el-col>

          <el-col :span="14">
            <el-card class="result-card absent" shadow="never">
              <template #header>
                <div class="card-head between">
                  <span class="error"><el-icon><Close /></el-icon> Absent ({{ result.absent_count }})</span>
                  <el-button 
                    v-if="result.absent_count > 0"
                    type="danger" 
                    size="small" 
                    :loading="isSending"
                    @click="notifyAbsentees"
                  >
                    Send Warning 
                  </el-button>
                </div>
              </template>
              
              <el-table :data="result.absent_students" size="small" style="width: 100%" empty-text="Everyone is present!">
                <el-table-column prop="name" label="Name" width="100" />
                <el-table-column prop="email" label="Email" />
              </el-table>
            </el-card>
          </el-col>
        </el-row>
        
        <div class="stats-footer">
          <el-divider />
          <span>Analytics: Detected {{ result.total_faces_detected }} faces. Total expected: {{ result.total_count }} students. </span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.container { max-width: 900px; margin: 20px auto; }
.header h2 { margin: 0; color: #303133; }
.subtitle { color: #909399; font-size: 14px; margin: 5px 0 0 0; }
.setup-grid { margin-bottom: 25px; padding: 20px; background: #f8f9fa; border-radius: 8px; }
.label { font-weight: bold; margin-right: 15px; color: #606266; }
.upload-section { margin-bottom: 25px; }
.preview-img { max-width: 100%; max-height: 450px; border-radius: 4px; object-fit: contain; transition: all 0.3s ease; }
.placeholder { padding: 60px 0; color: #C0C4CC; }
.icon { font-size: 48px; margin-bottom: 10px; }
.action-btn { width: 100%; height: 50px; font-size: 16px; font-weight: bold; }

.session-info { margin-bottom: 15px; text-align: right; }
.result-card { border-radius: 8px; min-height: 300px; }
.name-container { display: flex; flex-wrap: wrap; gap: 8px; }
.name-tag { font-size: 13px; }

.card-head { font-weight: bold; display: flex; align-items: center; gap: 5px; }
.card-head.between { justify-content: space-between; width: 100%; }
.success { color: #67C23A; }
.error { color: #F56C6C; }

.stats-footer { margin-top: 30px; text-align: center; color: #909399; font-size: 13px; }

.result-img {
  border: 2px solid #67C23A; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.img-tips {
  margin-top: 10px;
  font-size: 13px;
  color: #666;
  background: #f0f9eb;
  padding: 5px 15px;
  border-radius: 4px;
  display: inline-block;
}
</style>