<script setup>
import { ref, onMounted } from 'vue'
import { getHistory } from '@/api/attendance'
import { getAllClasses } from '@/api/students'
import { Timer, Picture, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// State management / 状态管理
const tableData = ref([])
const classes = ref([])
const selectedClassId = ref('')
const loading = ref(false)
const dialogVisible = ref(false)
const currentImages = ref({ org: '', res: '' })

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

// Image URL helper
// 图片路径拼接函数
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const cleanPath = path.startsWith('/') ? path : '/' + path
  return baseURL + cleanPath
}

// 1. Fetch class list for filter dropdown
// 1. 获取用于筛选下拉框的班级列表
const fetchClasses = async () => {
  try {
    const res = await getAllClasses()
    classes.value = Array.isArray(res) ? res : (res.data || [])
  } catch (error) {
    console.error("❌ [HistoryView] Fetch classes error:", error)
  }
}

// 2. Fetch history records
// 2. 加载历史考勤记录数据
const loadData = async () => {
  loading.value = true
  try {
    // Dynamically build query params / 动态构建查询参数
    const params = selectedClassId.value ? { class_id: selectedClassId.value } : {}
    const res = await getHistory(params)
    
    // Robust parsing / 兼容拦截器逻辑
    tableData.value = Array.isArray(res) ? res : (res.data || [])

    if (tableData.value.length === 0) {
      ElMessage.info('No attendance records found')
    }
  } catch (error) {
    console.error("❌ [HistoryView] Fetch history error:", error)
    ElMessage.error('Failed to load history')
  } finally {
    loading.value = false
  }
}

// 3. Trigger refresh on dropdown change
// 3. 下拉框改变时触发刷新
const handleFilterChange = () => {
  loadData()
}

// 4. Open image comparison dialog
// 4. 打开弹窗查看照片对比
const showDetail = (row) => {
  // Process image paths before passing to UI
  // 在传给 UI 前，先将路径拼接完整
  currentImages.value = {
    org: getImageUrl(row.original_img),
    res: getImageUrl(row.result_img)
  }
  dialogVisible.value = true
}

// Lifecycle Hooks
onMounted(() => {
  // Chain promises to ensure classes are loaded before history
  // 先获取班级列表，再获取历史数据，保证 UI 渲染顺序
  fetchClasses().then(() => {
    loadData()
  })
})
</script>

<template>
  <div class="history-page">
    <div class="header">
      <div class="left-actions">
        <h2><el-icon><Timer /></el-icon> History Archive </h2>
        <el-select 
          v-model="selectedClassId" 
          placeholder="All Classes" 
          clearable 
          @change="handleFilterChange"
          class="filter-select"
        >
          <el-option label="All Classes" value="" />
          <el-option 
            v-for="item in classes" 
            :key="item.id" 
            :label="item.name" 
            :value="item.id" 
          />
        </el-select>
      </div>
      <el-button type="primary" plain :icon="Refresh" @click="loadData">Refresh</el-button>
    </div>

    <el-table 
      :data="tableData" 
      v-loading="loading" 
      stripe 
      border 
      style="width: 100%"
      :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
    >
      <template #empty>
        <el-empty description="No records found. Start a new session!" />
      </template>

      <el-table-column prop="created_at" label="Time" width="180" align="center" sortable />
      <el-table-column prop="class_name" label="Class" width="150" align="center" />
      <el-table-column prop="total_count" label="Total" width="120" align="center" />
      
      <el-table-column label="Rate" min-width="200" align="center">
        <template #default="scope">
          <div style="padding: 0 10px">
            <el-progress 
              :text-inside="true" 
              :stroke-width="20" 
              :percentage="Number(scope.row.attendance_rate) || 0" 
              :status="scope.row.attendance_rate < 90 ? 'exception' : 'success'"
            />
          </div>
        </template>
      </el-table-column>

      <el-table-column label="Stats" width="220" align="center">
        <template #default="scope">
          <el-tag type="success" effect="dark">Present {{ scope.row.present_count }}</el-tag>
          <span style="margin: 0 8px; color: #909399">|</span>
          <el-tag type="danger" effect="dark">Absent {{ scope.row.absent_count }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Action" width="160" align="center" fixed="right">
        <template #default="scope">
          <el-button 
            type="primary" 
            size="small" 
            :icon="Picture" 
            @click="showDetail(scope.row)"
            :disabled="!scope.row.original_img"
          >
            Photos 
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="Analysis Details" width="80%" top="5vh" destroy-on-close>
      <div class="compare-container">
        <div class="img-box">
          <div class="label">📸 Original Photo</div>
          <div class="img-wrapper">
            <el-image 
              :src="currentImages.org" 
              fit="contain" 
              :preview-src-list="[currentImages.org, currentImages.res]"
              hide-on-click-modal
            >
              <template #error>
                <div class="image-slot">Load Failed</div>
              </template>
              <template #placeholder>
                <div class="loading-slot">Loading...</div>
              </template>
            </el-image>
          </div>
        </div>
        <div class="img-box">
          <div class="label">🤖 AI Recognition</div>
          <div class="img-wrapper">
            <el-image 
              :src="currentImages.res" 
              fit="contain" 
              :preview-src-list="[currentImages.res, currentImages.org]"
              hide-on-click-modal
            >
              <template #error>
                <div class="image-slot">Load Failed</div>
              </template>
            </el-image>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.history-page { padding: 20px; max-width: 1200px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; margin-bottom: 20px; align-items: center; }

.left-actions {
  display: flex;
  align-items: center;
}
.left-actions h2 { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  color: #303133; 
  margin: 0; 
  margin-right: 20px; 
}
.filter-select {
  width: 220px;
}

.compare-container { display: flex; gap: 20px; height: 60vh; }
.img-box { flex: 1; display: flex; flex-direction: column; height: 100%; border: 1px solid #e4e7ed; border-radius: 8px; padding: 15px; background: #fff; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); }
.label { font-weight: bold; margin-bottom: 15px; text-align: center; color: #409EFF; font-size: 16px; border-bottom: 1px solid #ebeef5; padding-bottom: 10px; }
.img-wrapper { flex: 1; overflow: hidden; display: flex; justify-content: center; align-items: center; background: #f5f7fa; border-radius: 4px; }
.el-image { width: 100%; height: 100%; }

.image-slot, .loading-slot { display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; color: #909399; font-size: 14px; background: #f5f7fa; }
</style>