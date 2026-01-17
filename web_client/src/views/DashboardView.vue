<script setup>
import { useRouter, useRoute } from 'vue-router'
import { School, User, Timer, SwitchButton, Camera, TrendCharts } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute() // 用于获取当前路由路径，保持菜单高亮

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/')
}
</script>

<template>
  <div class="common-layout">
    <el-container class="layout-container">
      <el-aside width="220px" class="aside-menu">
        <div class="logo">
          🎓 智慧考勤
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
            <span>班级管理</span>
          </el-menu-item>

          <el-menu-item index="/dashboard/student">
            <el-icon><User /></el-icon>
            <span>学生管理</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/attendance">
            <el-icon><Camera /></el-icon>
            <span>考勤识别</span>
          </el-menu-item>

          <el-menu-item index="/dashboard/history">
            <el-icon><Timer /></el-icon>
            <span>考勤历史</span>
          </el-menu-item>

          <el-menu-item index="/dashboard/analytics">
            <el-icon><TrendCharts /></el-icon>
            <span>数据分析</span>
          </el-menu-item>

          <el-menu-item index="" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="header">
          <span>管理员控制台</span>
          <span class="admin-name">Admin</span>
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
  font-size: 20px;
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
  font-size: 18px;
  padding: 0 20px;
}

.admin-name {
  font-weight: bold;
  color: #409EFF;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>