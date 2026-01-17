<script setup>
import { ref, onMounted } from 'vue'
// 导入封装后的接口 👈
import { getClasses, createClass, deleteClass } from '@/api/classes'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, School } from '@element-plus/icons-vue'

const classes = ref([])
const newClassName = ref('')
const isLoading = ref(false)

// 1. 获取班级列表 (使用封装接口)
const fetchClasses = async () => {
  try {
    const res = await getClasses()
    classes.value = res // axios 响应数据
  } catch (error) {
    ElMessage.error('获取班级列表失败')
  }
}

// 2. 创建新班级 (使用封装接口)
const handleCreateClass = async () => {
  if (!newClassName.value.trim()) {
    ElMessage.warning('请输入班级名称')
    return
  }
  
  isLoading.value = true
  try {
    await createClass(newClassName.value.trim())
    ElMessage.success('班级创建成功')
    newClassName.value = ''
    fetchClasses()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    isLoading.value = false
  }
}

// 3. 删除班级 (使用封装接口)
const handleDeleteClass = (cls) => {
  if (cls.student_count > 0) {
    ElMessage.error('该班级内已有学生，请先移除学生再删除班级')
    return
  }

  ElMessageBox.confirm(`确定要删除班级 [${cls.name}] 吗?`, '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteClass(cls.id)
      ElMessage.success('删除成功')
      fetchClasses()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  })
}

onMounted(fetchClasses)
</script>

<template>
  <div class="class-container">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <div class="title-group">
            <el-icon><School /></el-icon>
            <h2>班级架构管理</h2>
          </div>
          <div class="add-bar">
            <el-input 
              v-model="newClassName" 
              placeholder="输入新班级名称（如：MMWD2201）" 
              style="width: 250px; margin-right: 10px"
              @keyup.enter="handleCreateClass"
            />
            <el-button type="primary" :icon="Plus" @click="handleCreateClass" :loading="isLoading">
              新建班级
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="classes" style="width: 100%" stripe border>
        <el-table-column prop="id" label="班级ID" width="100" />
        <el-table-column prop="name" label="班级名称" />
        <el-table-column prop="student_count" label="已录入学生人数" width="180">
          <template #default="scope">
            <el-tag :type="scope.row.student_count > 0 ? 'success' : 'info'">
              {{ scope.row.student_count }} 人
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="scope">
            <el-button 
              type="danger" 
              :icon="Delete" 
              circle 
              @click="handleDeleteClass(scope.row)" 
            />
          </template>
        </el-table-column>
      </el-table>
      
      <div class="tips">
        <p>* 注意事项：只有当班级人数为 0 时才允许删除班级。</p>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.class-container { max-width: 900px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; }
.title-group { display: flex; align-items: center; gap: 10px; }
.title-group h2 { margin: 0; font-size: 18px; }
.add-bar { display: flex; }
.tips { margin-top: 20px; color: #909399; font-size: 13px; }
</style>