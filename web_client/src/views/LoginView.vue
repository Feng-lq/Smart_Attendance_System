<script setup>
import { User, Lock } from '@element-plus/icons-vue'
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api/auth'

const router = useRouter()

// 表单数据
const form = reactive({
  username: '',
  password: ''
})

const isLoading = ref(false)

// 登录逻辑
const handleLogin = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }

  isLoading.value = true

  try {
    // 1. 准备表单数据 (FastAPI 要求格式)
    const formData = new URLSearchParams()
    formData.append('username', form.username)
    formData.append('password', form.password)

    // 2. 调用封装接口 (路径会自动变为 /api/token) 👈
    const response = await login(formData)

    // 3. 登录成功处理 (axios 拦截器如果已处理返回 response.data, 此处可简写)
    const token = response.access_token || response.data.access_token
    
    // 存储 Token
    localStorage.setItem('token', token)
    
    ElMessage.success('登录成功！')
    
    // 跳转到主页
    router.push('/dashboard/student') 
    
  } catch (error) {
    console.error(error)
    // 这里的错误提示会涵盖 401 (密码错误) 和 404 (路径错误)
    ElMessage.error(error.response?.data?.detail || '登录失败：请检查网络或账号密码')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="title">智慧考勤系统</h2>
      <p class="subtitle">管理员登录</p>

      <el-form :model="form" size="large">
        <el-form-item>
          <el-input 
            v-model="form.username" 
            placeholder="用户名" 
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码" 
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
          立即登录
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
/* 居中背景 */
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 登录卡片 */
.login-card {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  text-align: center;
}

.title {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.subtitle {
  color: #666;
  margin-bottom: 30px;
}

.login-btn {
  width: 100%;
  margin-top: 10px;
  font-weight: bold;
}
</style>