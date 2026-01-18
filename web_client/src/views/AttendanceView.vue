<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import { UploadFilled, Message, Check, Close } from '@element-plus/icons-vue'
import { getClasses, analyzeClassPhoto } from '@/api/attendance'

const classes = ref([])
const selectedClassId = ref(null)
const uploadFile = ref(null)
const previewUrl = ref('')
const isProcessing = ref(false)
const isSending = ref(false) 
const result = ref(null) 

// 1. 定义后端基准地址
const baseURL = 'http://127.0.0.1:8000'

// 2. 图片路径拼接函数
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const cleanPath = path.startsWith('/') ? path : '/' + path
  return baseURL + cleanPath
}

// 3. 获取班级列表
const fetchClasses = async () => {
  try {
    const res = await getClasses()
    // 🔥 防错处理：有些 axios 封装会返回 res，有些返回 res.data
    // 如果 res 是数组，直接用；如果是对象且有 data 属性，用 res.data
    classes.value = Array.isArray(res) ? res : (res.data || [])
  } catch (error) {
    console.error(error)
    ElMessage.error('无法获取班级列表，请检查后端是否启动')
  }
}

// 选择照片
const handleFileChange = (file) => {
  uploadFile.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
  result.value = null 
}

// 4. 提交识别
const handleAnalyze = async () => {
  if (!selectedClassId.value || !uploadFile.value) {
    ElMessage.warning('请先选择班级并上传照片')
    return
  }
  
  isProcessing.value = true
  try {
    const formData = new FormData()
    formData.append('class_id', selectedClassId.value)
    formData.append('file', uploadFile.value)

    const response = await analyzeClassPhoto(formData)
    
    // 🔥 调试日志：看看后端到底返了什么
    console.log("后端返回的识别结果:", response)
    
    result.value = response
    ElMessage.success('识别并标注完成！')
  } catch (error) {
    console.error(error)
    const detail = error.response?.data?.detail || '服务器连接超时'
    ElMessage.error('识别失败: ' + detail)
  } finally {
    isProcessing.value = false
  }
}

// 通知缺勤
const notifyAbsentees = () => {
  if (!result.value || result.value.absent_count === 0) return

  // 🔥 字段修正：result.id
  ElMessageBox.confirm(
    `确定要向这 ${result.value.absent_count} 名同学发送缺勤预警邮件吗？`,
    '批量发送通知',
    {
      confirmButtonText: '立即发送',
      cancelButtonText: '取消',
      type: 'info',
      icon: Message
    }
  ).then(async () => {
    isSending.value = true
    setTimeout(() => {
      isSending.value = false
      ElNotification({
        title: '通知已下发',
        // 🔥 字段修正：result.id
        message: `考勤批次 ${result.value.id} 的提醒邮件已发送。`,
        type: 'success'
      })
    }, 2000)
  })
}

onMounted(fetchClasses)
</script>

<template>
  <div class="container">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <h2>📸 课堂合照智能识别</h2>
          <p class="subtitle">上传班级全家福，系统将自动比对名单并记录考勤</p>
        </div>
      </template>

      <div class="setup-grid">
        <div class="step-section">
          <span class="label">选择班级：</span>
          <el-select v-model="selectedClassId" placeholder="选择上课班级" size="large" style="width: 240px">
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
        <div class="text">将课堂合照拖到此处，或 <em>点击上传</em></div>
        </div>
    </el-upload>
    
    <div v-if="result && result.result_img" class="img-tips">
        绿色框：识别成功 | 红色框：未匹配到名单
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
        {{ isProcessing ? '深度检测中...' : '开始批量识别考勤' }}
      </el-button>

      <div v-if="result" class="result-section">
        <div class="session-info">
          <el-tag type="info" effect="plain">考勤批次: {{ result.id }}</el-tag>
        </div>

        <el-row :gutter="20">
          <el-col :span="10">
            <el-card class="result-card present" shadow="never">
              <template #header>
                <div class="card-head success">
                  <el-icon><Check /></el-icon> 已出席 ({{ result.present_count }})
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
                  <span class="error"><el-icon><Close /></el-icon> 缺席名单 ({{ result.absent_count }})</span>
                  <el-button 
                    v-if="result.absent_count > 0"
                    type="danger" 
                    size="small" 
                    :loading="isSending"
                    @click="notifyAbsentees"
                  >
                    发送提醒
                  </el-button>
                </div>
              </template>
              
              <el-table :data="result.absent_students" size="small" style="width: 100%" empty-text="全员到齐！">
                <el-table-column prop="name" label="姓名" width="100" />
                <el-table-column prop="email" label="邮箱" />
              </el-table>
            </el-card>
          </el-col>
        </el-row>
        
        <div class="stats-footer">
          <el-divider />
          <span>算法统计：本次合照识别到 {{ result.total_faces_detected }} 张面孔，该班级应到 {{ result.total_count }} 人。</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
/* 保持原样 */
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