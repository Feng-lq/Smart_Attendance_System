<script setup>
import { useRouter, useRoute } from 'vue-router'
import { School, User, Timer, SwitchButton, Camera, TrendCharts } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/userStore'
import { storeToRefs } from 'pinia'

const router = useRouter()
const route = useRoute() // Used to keep menu highlighted / 用于获取当前路由路径，保持菜单高亮

const userStore = useUserStore()
// Extract reactive variables from store / 从 store 中提取响应式变量
const { name, role } = storeToRefs(userStore)

// Handle logout action / 处理退出登录
const handleLogout = () => {
  userStore.logoutAction()
}
</script>

<template>
  <div class="common-layout">
    <el-container class="layout-container">
      <el-aside width="220px" class="aside-menu">
        <div class="logo">
          🎓 Smart Attendance
        </div>
        
        <el-menu
          active-text-color="#409EFF"
          background-color="#304156"
          text-color="#bfcbd9"
          :default-active="route.path"
          class="el-menu-vertical"
          router
        >
          <el-menu-item index="/dashboard/class">
            <el-icon><School /></el-icon>
            <span>Class</span>
          </el-menu-item>

          <el-menu-item index="/dashboard/student">
            <el-icon><User /></el-icon>
            <span>Student</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/attendance">
            <el-icon><Camera /></el-icon>
            <span>Face Recognition</span>
          </el-menu-item>

          <el-menu-item index="/dashboard/history">
            <el-icon><Timer /></el-icon>
            <span>History</span>
          </el-menu-item>

          <el-menu-item index="/dashboard/analytics">
            <el-icon><TrendCharts /></el-icon>
            <span>Analytics</span>
          </el-menu-item>

          <el-menu-item index="logout" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>Logout</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="header">
          <span>Administrator Console</span>
          <span class="admin-name">{{ name || 'Administrator' }}</span>
        </el-header>
        
        <el-main class="main-content">
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside-menu {
  background-color: #304156;
  color: white;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  background-color: #2b3648;
  color: white;
}

.el-menu-vertical {
  border-right: none;
}

.header {
  background-color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dcdfe6;
  font-size: 16px;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,21,41,0.08); /* Added subtle shadow for depth / 增加了微弱的阴影提升质感 */
}

.admin-name {
  font-weight: bold;
  color: #409EFF;
  display: flex;
  align-items: center;
  gap: 8px;
}

.admin-name::before {
  content: "👋"; /* A little friendly greeting / 加个友好的小表情 */
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  /* Support smooth scrolling / 支持平滑滚动 */
  overflow-y: auto; 
}
</style>