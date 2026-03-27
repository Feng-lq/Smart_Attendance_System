<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router' 
// 🚀 [Optimized] Added Key icon for the password change button
import { User, Calendar, SwitchButton, Key } from '@element-plus/icons-vue' 
import { queryStudentAttendance } from '@/api/students' 
// 🚀 [Optimized] Import the newly added updatePassword API
import { updatePassword } from '@/api/auth'
import { useUserStore } from '@/stores/userStore' 
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore() 

const isLoading = ref(false)
const studentData = ref(null)

// Password Dialog State / 修改密码弹窗状态
const pwdDialogVisible = ref(false)
const isUpdatingPwd = ref(false)
const pwdForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const colors = [
  { color: '#f56c6c', percentage: 60 },
  { color: '#e6a23c', percentage: 80 },
  { color: '#5cb87a', percentage: 100 },
]

const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return baseURL + (path.startsWith('/') ? path : '/' + path)
}

const fetchMyData = async () => {
  isLoading.value = true
  try {
    // Zero-Trust Security: Frontend auto-injects the current user's ID
    const res = await queryStudentAttendance(userStore.name)
    studentData.value = res 
  } catch (error) {
    console.error("❌ [StudentPortal] Fetch error:", error)
    ElMessage.error('Failed to load your attendance data')
  } finally {
    isLoading.value = false
  }
}

// Change Password Logic
// 修改密码的业务逻辑闭环
const handlePasswordChange = async () => {
  if (!pwdForm.oldPassword || !pwdForm.newPassword || !pwdForm.confirmPassword) {
    ElMessage.warning('Please fill in all fields')
    return
  }
  if (pwdForm.newPassword !== pwdForm.confirmPassword) {
    ElMessage.error('New passwords do not match')
    return
  }
  if (pwdForm.oldPassword === pwdForm.newPassword) {
    ElMessage.warning('New password must be different')
    return
  }

  isUpdatingPwd.value = true
  try {
    await updatePassword({
      old_password: pwdForm.oldPassword,
      new_password: pwdForm.newPassword
    })
    
    ElMessage.success('Password updated! Please log in again')
    pwdDialogVisible.value = false
    
    // Force logout after password change for security
    // 为了安全起见，密码修改成功后强制清空 Token 并踢回登录页
    userStore.logoutAction()
  } catch (error) {
    console.error("[StudentPortal] Password update error:", error)
    ElMessage.error(error.response?.data?.detail || 'Update failed')
  } finally {
    isUpdatingPwd.value = false
  }
}

// Reset password form when dialog closes / 弹窗关闭时清空表单
const resetPwdForm = () => {
  pwdForm.oldPassword = ''
  pwdForm.newPassword = ''
  pwdForm.confirmPassword = ''
}

const getStatusType = (status) => {
  return status === 'present' ? 'success' : 'danger'
}
const getStatusText = (status) => {
  return status === 'present' ? 'Present' : 'Absent'
}

const handleLogout = () => {
  ElMessageBox.confirm(
    'Are you sure you want to log out? ',
    'Log out',
    {
      confirmButtonText: 'Log Out',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  ).then(() => {
    userStore.logoutAction()
    ElMessage.success('Logged out securely')
  }).catch(() => {})
}

// Auto-trigger on page load / 页面加载时自动触发静默查询
onMounted(() => {
  fetchMyData()
})
</script>

<template>
  <div class="portal-container" v-loading="isLoading">

    <div class="top-bar">
      <el-button type="primary" plain :icon="Key" @click="pwdDialogVisible = true">
        Change Password 
      </el-button>
      <el-button type="danger" plain :icon="SwitchButton" @click="handleLogout">
        Log Out 
      </el-button>
    </div>
    
    <div class="welcome-box">
      <h1 class="title">🎓 Personal Attendance Portal</h1>
      <p class="subtitle">Welcome, Student {{ userStore.name }}! Here is your attendance record.</p>
    </div>

    <div v-if="studentData" class="result-dashboard">
      
      <div class="profile-section">
        <el-card shadow="hover" class="profile-card">
          <div class="profile-content">
            <el-avatar :size="80" :src="getImageUrl(studentData.student_info.photo_path)" shape="square" />
            <div class="info-text">
              <h2>{{ studentData.student_info.name }}</h2>
              <p><el-icon><User /></el-icon> ID {{ studentData.student_info.student_id }}</p>
              <p><el-icon><Calendar /></el-icon> Class {{ studentData.student_info.class_name }}</p>
            </div>
            
            <div class="rate-circle">
              <el-progress type="dashboard" :percentage="studentData.stats.rate" :color="colors" />
              <div class="rate-label">Rate </div>
            </div>
          </div>
        </el-card>
      </div>

      <el-row :gutter="20" class="stats-row">
        <el-col :span="8">
          <div class="stat-item total">
            <div class="num">{{ studentData.stats.total }}</div>
            <div class="label">Total </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item present">
            <div class="num">{{ studentData.stats.present }}</div>
            <div class="label">Present </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item absent">
            <div class="num">{{ studentData.stats.absent }}</div>
            <div class="label">Absent </div>
          </div>
        </el-col>
      </el-row>

      <el-card shadow="never" class="history-card">
        <template #header>
          <div class="card-header">
            <span>📅 Attendance Timeline </span>
          </div>
        </template>
        
        <el-table :data="studentData.history" style="width: 100%" stripe empty-text="No records yet ">
          <el-table-column prop="date" label="Date " width="180">
            <template #default="scope">
              <span style="font-weight: bold; color: #606266">{{ scope.row.date }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="status" label="Status ">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)" effect="dark">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="Remarks ">
             <template #default="scope">
               <span v-if="scope.row.status === 'absent'" style="color: #F56C6C; font-size: 12px;">
                 Contact admin if incorrect 
               </span>
               <span v-else style="color: #67C23A; font-size: 12px;">Normal </span>
             </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <el-dialog 
      v-model="pwdDialogVisible" 
      title="Security Settings " 
      width="400px" 
      @closed="resetPwdForm"
    >
      <el-form :model="pwdForm" label-position="top">
        <el-form-item label="Current Password ">
          <el-input 
            v-model="pwdForm.oldPassword" 
            type="password" 
            show-password 
            placeholder="Enter current password"
          />
        </el-form-item>
        <el-form-item label="New Password ">
          <el-input 
            v-model="pwdForm.newPassword" 
            type="password" 
            show-password 
            placeholder="Enter new password"
          />
        </el-form-item>
        <el-form-item label="Confirm New Password ">
          <el-input 
            v-model="pwdForm.confirmPassword" 
            type="password" 
            show-password 
            placeholder="Type new password again"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="pwdDialogVisible = false">Cancel </el-button>
          <el-button type="primary" :loading="isUpdatingPwd" @click="handlePasswordChange">
            Update Password 
          </el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<style scoped>
.portal-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
}

.top-bar {
  display: flex;
  justify-content: flex-end;
  gap: 15px; 
  margin-bottom: 20px;
}

.welcome-box {
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