<script setup>
import { ref, onMounted } from 'vue'
import { getHistory } from '@/api/attendance'
import { getAllClasses } from '@/api/students'
import { Timer, Picture, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const tableData = ref([])
const classes = ref([])
const selectedClassId = ref('')
const loading = ref(false)
const dialogVisible = ref(false)
const currentImages = ref({ org: '', res: '' })

const fetchClasses = async () => {
  try {
    const res = await getAllClasses()
    classes.value = Array.isArray(res) ? res : (res.data || [])
  } catch (error) {
    console.error('获取班级失败', error)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = selectedClassId.value ? { class_id: selectedClassId.value } : {}
    const res = await getHistory(params)
    // 兼容拦截器逻辑：有的拦截器直接返回 res，有的返回 res.data
    tableData.value = Array.isArray(res) ? res : (res.data || [])

    if (tableData.value.length === 0) {
      ElMessage.info('暂无历史考勤记录')
    }
  } catch (error) {
    console.error("获取历史记录失败:", error)
    ElMessage.error('无法加载历史记录')
  } finally {
    loading.value = false
  }
}

// 下拉框改变时触发刷新
const handleFilterChange = () => {
  loadData()
}

// 打开弹窗查看照片
const showDetail = (row) => {
  currentImages.value = {
    org: row.original_img,
    res: row.result_img
  }
  dialogVisible.value = true
}

onMounted(() => {
  // 🚀 先获取班级列表，再获取历史数据
  fetchClasses().then(() => {
    loadData()
  })
})
</script>

<template>
  <div class="history-page">
    <div class="header">
      <h2><el-icon><Timer /></el-icon> 考勤历史档案</h2>
      <el-select 
          v-model="selectedClassId" 
          placeholder="全部班级" 
          clearable 
          @change="handleFilterChange"
          class="filter-select"
        >
          <el-option label="全部班级" value="" />
          <el-option 
            v-for="item in classes" 
            :key="item.id" 
            :label="item.name" 
            :value="item.id" 
          />
        </el-select>
      <el-button type="primary" plain :icon="Refresh" @click="loadData">刷新列表</el-button>
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
        <el-empty description="暂无考勤记录，快去发起第一次识别吧！" />
      </template>

      <el-table-column prop="created_at" label="考勤时间" width="180" align="center" sortable />
      <el-table-column prop="class_name" label="班级" width="150" align="center" />
      <el-table-column prop="total_count" label="总人数" width="100" align="center" />
      
      <el-table-column label="出勤率" min-width="200" align="center">
        <template #default="scope">
          <div style="padding: 0 10px">
            <el-progress 
              :text-inside="true" 
              :stroke-width="20" 
              :percentage="scope.row.attendance_rate" 
              :status="scope.row.attendance_rate < 90 ? 'exception' : 'success'"
            />
          </div>
        </template>
      </el-table-column>

      <el-table-column label="详细统计" width="200" align="center">
        <template #default="scope">
          <el-tag type="success" effect="dark">实到 {{ scope.row.present_count }}</el-tag>
          <span style="margin: 0 8px; color: #909399">|</span>
          <el-tag type="danger" effect="dark">缺席 {{ scope.row.absent_count }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="凭证操作" width="150" align="center" fixed="right">
        <template #default="scope">
          <el-button type="primary" size="small" :icon="Picture" @click="showDetail(scope.row)">
            查看照片
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="考勤结果详情" width="80%" top="5vh" destroy-on-close>
      <div class="compare-container">
        <div class="img-box">
          <div class="label">📸 原始上传图</div>
          <div class="img-wrapper">
            <el-image 
              :src="currentImages.org" 
              fit="contain" 
              :preview-src-list="[currentImages.org, currentImages.res]"
              hide-on-click-modal
            >
              <template #error>
                <div class="image-slot">图片加载失败</div>
              </template>
              <template #placeholder>
                <div class="loading-slot">加载中...</div>
              </template>
            </el-image>
          </div>
        </div>
        <div class="img-box">
          <div class="label">🤖 系统识别结果</div>
          <div class="img-wrapper">
            <el-image 
              :src="currentImages.res" 
              fit="contain" 
              :preview-src-list="[currentImages.res, currentImages.org]"
              hide-on-click-modal
            >
              <template #error>
                <div class="image-slot">图片加载失败</div>
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
.header h2 { display: flex; align-items: center; gap: 10px; color: #303133; margin: 0; }

/* 🚀 新增样式：左侧标题和下拉框排列 */
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
  margin-right: 20px; /* 标题和下拉框的间距 */
}
.filter-select {
  width: 200px;
}

.compare-container { display: flex; gap: 20px; height: 60vh; }
.img-box { flex: 1; display: flex; flex-direction: column; height: 100%; border: 1px solid #e4e7ed; border-radius: 8px; padding: 15px; background: #fff; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); }
.label { font-weight: bold; margin-bottom: 15px; text-align: center; color: #409EFF; font-size: 16px; border-bottom: 1px solid #ebeef5; padding-bottom: 10px; }
.img-wrapper { flex: 1; overflow: hidden; display: flex; justify-content: center; align-items: center; background: #f5f7fa; border-radius: 4px; }
.el-image { width: 100%; height: 100%; }

/* 图片加载失败或加载中的样式 */
.image-slot, .loading-slot { display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; color: #909399; font-size: 14px; background: #f5f7fa; }
</style>