<script setup>
import { useRouter, useRoute } from 'vue-router'
import { School, User, Timer, SwitchButton, Camera, TrendCharts, ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/userStore'
import { storeToRefs } from 'pinia'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute() 

const userStore = useUserStore()
const { name, role } = storeToRefs(userStore)

// Added confirmation dialog for better UX
// 为退出动作增加防误触的二次确认弹窗
const handleLogout = () => {
  ElMessageBox.confirm(
    'Are you sure you want to log out?',
    'Log out',
    {
      confirmButtonText: 'Log Out',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  ).then(() => {
    userStore.logoutAction()
  }).catch(() => {})
}

// Handle dropdown commands
// 处理下拉菜单的指令派发
const handleCommand = (command) => {
  if (command === 'logout') {
    handleLogout()
  }
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
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="header">
          <div class="header-left">
            <span class="system-title">Administrator Console</span>
          </div>
          
          <div class="header-right">
            <el-dropdown trigger="click" @command="handleCommand">
              <div class="user-profile-trigger">
                <el-avatar 
                  :size="36" 
                  src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" 
                  class="user-avatar"
                />
                <span class="admin-name">{{ name || 'Administrator' }}</span>
                <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
              </div>
              
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item disabled>
                    Role: {{ role === 'admin' ? 'Super Admin' : 'Teacher' }}
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout" class="logout-item">
                    <el-icon><SwitchButton /></el-icon>
                    Logout
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
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
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.15);
  z-index: 10;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  background-color: #2b3648;
  color: #fff;
  letter-spacing: 0.5px;
}

.el-menu-vertical {
  border-right: none;
}

.el-menu-item:hover {
  background-color: #263445 !important;
}

.header {
  background-color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e6e6e6;
  font-size: 16px;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0,21,41,0.08);
  z-index: 9;
}

.system-title {
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-profile-trigger {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-profile-trigger:hover {
  background-color: #f5f7fa;
}

.user-avatar {
  margin-right: 10px;
  border: 1px solid #EBEEF5;
}

.admin-name {
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.dropdown-icon {
  margin-left: 5px;
  font-size: 12px;
  color: #909399;
}

.logout-item {
  color: #F56C6C;
}
.logout-item:hover {
  background-color: #fef0f0 !important;
  color: #F56C6C !important;
}

.main-content {
  background-color: #f0f2f5;
  padding: 24px;
  overflow-y: auto; 
}
</style>