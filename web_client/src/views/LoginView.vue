<script setup>
import { User, Lock } from '@element-plus/icons-vue'
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
// 🚀 [Optimized] Removed unused useRouter import, as routing is handled by Pinia Store
// 🚀 [优化提升] 移除了未使用的 useRouter，因为路由跳转的职责已经完美剥离到了 Pinia Store 中
import { useUserStore } from '@/stores/userStore'

const userStore = useUserStore()
const isLoading = ref(false)

// Form data / 表单数据 (增加 role 字段)
const form = reactive({
  username: '',
  password: '',
  role: 'admin' // Default to teacher/admin / 默认选中教师
})

// Login logic / 登录逻辑
const handleLogin = async () => {
  // Simple validation / 简单非空校验
  if (!form.username || !form.password) {
    ElMessage.warning('Please enter both username and password')
    return
  }

  isLoading.value = true

  try {
    // 🚀 [Optimized] Direct Store Action call for Separation of Concerns
    // 🚀 [优化提升] 核心变化：直接调用 Store 的 Action。视图层只负责 UI，逻辑层负责 API 和路由跳转
    const success = await userStore.loginAction(form)

    if (success) {
      ElMessage.success('Login Successful!')
      // Note: Redirection is handled in stores/userStore.js
      // 注意：跳转逻辑已移至 store/userStore.js 中处理
      // 老师 (admin) -> /dashboard/class
      // 学生 (student) -> /student
    } else {
      ElMessage.error('Login Failed: Check credentials or role')
    }
  } catch (error) {
    console.error("❌ [LoginView] System error:", error)
    ElMessage.error('System error, please try again later')
  } finally {
    isLoading.value = false
  }
}

// Computed property: Dynamic input placeholder based on role
// 计算属性：根据角色动态显示输入框提示
const usernamePlaceholder = computed(() => {
  return form.role === 'admin' ? 'Admin Username' : 'Student ID'
})
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="title">Smart Attendance System</h2>
      
      <el-tabs v-model="form.role" stretch class="role-tabs">
        <el-tab-pane label="Teacher" name="admin"></el-tab-pane>
        <el-tab-pane label="Student" name="student"></el-tab-pane>
      </el-tabs>

      <el-form :model="form" size="large" @submit.prevent>
        <el-form-item>
          <el-input 
            v-model="form.username" 
            :placeholder="usernamePlaceholder" 
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="Password" 
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-button 
          type="primary" 
          class="login-btn" 
          :loading="isLoading"
          @click="handleLogin"
        >
          {{ isLoading ? 'Logging in...' : 'Login' }}
        </el-button>
        
        <div class="tips" v-if="form.role === 'student'">
          <small>Notice: Default student password is 123456</small>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.title {
  text-align: center;
  margin: 0 0 20px 0;
  color: #333;
  font-size: 24px;
}

.role-tabs {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
  margin-top: 10px;
  font-weight: bold;
  padding: 20px 0; 
}

.tips {
  margin-top: 15px;
  text-align: center;
  color: #909399;
}
</style>