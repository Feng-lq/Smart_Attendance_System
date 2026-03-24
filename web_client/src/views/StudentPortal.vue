<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router' // 引入 useRouter
import { Search, User, Calendar, SwitchButton } from '@element-plus/icons-vue' // 引入退出图标
// 引入 API 和 Store
import { queryStudentAttendance } from '@/api/students' 
import { useUserStore } from '@/stores/userStore' // 引入 Store
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore() // 获取 store 实例

const searchId = ref('')
const isLoading = ref(false)
const studentData = ref(null)

const baseURL = 'http://127.0.0.1:8000'

const colors = [
  { color: '#f56c6c', percentage: 60 },
  { color: '#e6a23c', percentage: 80 },
  { color: '#5cb87a', percentage: 100 },
]

const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const cleanPath = path.startsWith('/') ? path : '/' + path
  return baseURL + cleanPath
}

const handleSearch = async () => {
  if (!searchId.value) {
    ElMessage.warning('请输入学号')
    return
  }
  
  isLoading.value = true
  studentData.value = null 
  
  try {
    const res = await queryStudentAttendance(searchId.value)
    studentData.value = res 
  } catch (error) {
    const msg = error.response?.data?.detail || '未找到该学号或服务器错误'
    ElMessage.error(msg)
  } finally {
    isLoading.value = false
  }
}

const getStatusType = (status) => {
  return status === 'present' ? 'success' : 'danger'
}
const getStatusText = (status) => {
  return status === 'present' ? '✅ 出勤' : '❌ 缺勤'
}

// 🔥 新增：退出登录逻辑
const handleLogout = () => {
  ElMessageBox.confirm(
    '确定要退出查询并返回登录页吗？',
    '提示',
    {
      confirmButtonText: '确定退出',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 1. 清理 Store 中的 Token 和用户信息
    userStore.logoutAction()
    // 2. 强制跳转回首页 (登录页)
    router.push('/')
    ElMessage.success('已安全退出')
  }).catch(() => {
    // 取消操作，不做任何事
  })
}

onMounted(() => {
  if (route.query.id) {
    searchId.value = route.query.id
    handleSearch()
  }
})
</script>

<template>
  <div class="portal-container">

    <div class="top-bar">
      <el-button type="danger" plain :icon="SwitchButton" @click="handleLogout">
        退出 / 返回登录
      </el-button>
    </div>
    
    <div class="search-box">
      <h1 class="title">🎓 学生考勤查询门户</h1>
      <p class="subtitle">输入学号，一键查看你的出勤记录</p>
    </div>

    <div v-if="studentData" class="result-dashboard">
      
      <div class="profile-section">
        <el-card shadow="hover" class="profile-card">
          <div class="profile-content">
            <el-avatar :size="80" :src="getImageUrl(studentData.student_info.photo_path)" shape="square" />
            <div class="info-text">
              <h2>{{ studentData.student_info.name }}</h2>
              <p><el-icon><User /></el-icon> 学号: {{ studentData.student_info.student_id }}</p>
              <p><el-icon><Calendar /></el-icon> 班级: {{ studentData.student_info.class_name }}</p>
            </div>
            
            <div class="rate-circle">
              <el-progress type="dashboard" :percentage="studentData.stats.rate" :color="colors" />
              <div class="rate-label">出勤率</div>
            </div>
          </div>
        </el-card>
      </div>

      <el-row :gutter="20" class="stats-row">
        <el-col :span="8">
          <div class="stat-item total">
            <div class="num">{{ studentData.stats.total }}</div>
            <div class="label">应到次数</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item present">
            <div class="num">{{ studentData.stats.present }}</div>
            <div class="label">实到次数</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item absent">
            <div class="num">{{ studentData.stats.absent }}</div>
            <div class="label">缺勤次数</div>
          </div>
        </el-col>
      </el-row>

      <el-card shadow="never" class="history-card">
        <template #header>
          <div class="card-header">
            <span>📅 考勤流水记录</span>
          </div>
        </template>
        
        <el-table :data="studentData.history" style="width: 100%" stripe>
          <el-table-column prop="date" label="考勤时间" width="180">
            <template #default="scope">
              <span style="font-weight: bold; color: #606266">{{ scope.row.date }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)" effect="dark">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="备注">
             <template #default="scope">
               <span v-if="scope.row.status === 'absent'" style="color: #F56C6C; font-size: 12px;">
                 若有异议请联系辅导员
               </span>
               <span v-else style="color: #67C23A; font-size: 12px;">正常</span>
             </template>
          </el-table-column>
        </el-table>
      </el-card>

    </div>
  </div>
</template>

<style scoped>
/* 保持样式不变 */
.portal-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
}

.search-box {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  color: #303133;
  margin-bottom: 10px;
}

.subtitle {
  color: #909399;
  margin-bottom: 30px;
}

.input-wrapper {
  display: flex;
  justify-content: center;
  gap: 10px;
  max-width: 500px;
  margin: 0 auto;
}

.custom-input {
  width: 100%;
}

.search-btn {
  padding: 0 30px;
}

/* 结果区域动画 */
.result-dashboard {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.profile-card {
  border-radius: 12px;
  margin-bottom: 20px;
}

.profile-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.info-text {
  flex: 1;
}

.info-text h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.info-text p {
  margin: 5px 0;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 5px;
}

.rate-circle {
  text-align: center;
}

.rate-label {
  font-size: 12px;
  color: #909399;
  margin-top: -5px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-item {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
  border: 1px solid #EBEEF5;
}

.stat-item .num {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-item .label {
  font-size: 13px;
  color: #909399;
}

.stat-item.total .num { color: #409EFF; }
.stat-item.present .num { color: #67C23A; }
.stat-item.absent .num { color: #F56C6C; }

.history-card {
  border-radius: 12px;
}
</style>