<script setup>
import { User, Lock } from '@element-plus/icons-vue'
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
// 引入我们刚写好的 Store
import { useUserStore } from '@/stores/userStore'

const userStore = useUserStore()
const isLoading = ref(false)

// 表单数据 (增加 role 字段)
const form = reactive({
  username: '',
  password: '',
  role: 'admin' // 默认选中教师
})

// 登录逻辑
const handleLogin = async () => {
  // 简单非空校验
  if (!form.username || !form.password) {
    ElMessage.warning('请输入完整信息')
    return
  }

  isLoading.value = true

  try {
    // 🔥 核心变化：直接调用 Store 的 Action
    // Store 内部负责：调用API -> 存Token -> 存Role -> 路由跳转
    const success = await userStore.loginAction(form)

    if (success) {
      ElMessage.success('登录成功！')
      // 注意：跳转逻辑已移至 store/userStore.js 中处理
      // 老师 -> /dashboard
      // 学生 -> /student/my-attendance
    } else {
      ElMessage.error('登录失败：请检查账号、密码或角色选择')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('系统错误，请稍后再试')
  } finally {
    isLoading.value = false
  }
}

// 计算属性：动态显示输入框提示
const usernamePlaceholder = computed(() => {
  return form.role === 'admin' ? '请输入管理员账号' : '请输入学号'
})
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="title">智慧考勤系统</h2>
      
      <el-tabs v-model="form.role" stretch class="role-tabs">
        <el-tab-pane label="我是教师" name="admin"></el-tab-pane>
        <el-tab-pane label="我是学生" name="student"></el-tab-pane>
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
          {{ isLoading ? '登录中...' : '立即登录' }}
        </el-button>
        
        <div class="tips" v-if="form.role === 'student'">
          <small>📢 提示：学生初始密码默认为 123456</small>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
/* 保持你原本漂亮的样式 */
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
  /* text-align: center; */ /* 去掉这个，让 tabs 更好看 */
}

.title {
  text-align: center;
  margin: 0 0 20px 0;
  color: #333;
  font-size: 24px;
}

/* 新增：标签页样式微调 */
.role-tabs {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
  margin-top: 10px;
  font-weight: bold;
  padding: 20px 0; /* 按钮稍微高一点更好看 */
}

.tips {
  margin-top: 15px;
  text-align: center;
  color: #909399;
}
</style>