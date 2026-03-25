<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { getClasses } from '@/api/classes'
import { getClassTrend, getAbsentRanking } from '@/api/analytics'
import * as echarts from 'echarts'
import { TrendCharts, Warning } from '@element-plus/icons-vue'

// State management / 数据状态
const classList = ref([])
const selectedClass = ref(null)
const rankingData = ref([])
const loading = ref(false)

// Chart instance container / 图表实例容器
const chartRef = ref(null)
let myChart = null

// 1. Load class list
// 1. 加载班级列表
const loadClasses = async () => {
  try {
    const res = await getClasses()
    classList.value = res.data || res
    
    // Select the first class by default and auto-analyze
    // 默认选中第一个班级并自动开始分析
    if (classList.value.length > 0) {
      selectedClass.value = classList.value[0].id
      await handleAnalyze() 
    }
  } catch (error) {
    console.error("❌ [Analytics] Failed to load classes:", error)
  }
}

// 2. Core: Fetch data and render chart
// 2. 核心：获取数据并渲染图表
const handleAnalyze = async () => {
  if (!selectedClass.value) return
  loading.value = true
  
  try {
    // Parallel requests
    // 并行请求
    const [trendRes, rankRes] = await Promise.all([
      getClassTrend(selectedClass.value),
      getAbsentRanking(selectedClass.value)
    ])
    
    const trendData = trendRes.data || trendRes
    rankingData.value = rankRes.data || rankRes
    
    // Render the chart
    // 渲染图表
    await nextTick() 
    renderChart(trendData)
    
  } catch (e) {
    console.error("[Analytics] Analysis failed:", e)
  } finally {
    loading.value = false
  }
}

// 3. ECharts rendering logic
// 3. ECharts 渲染逻辑
const renderChart = (data) => {
  if (!chartRef.value) return
  
  // Memory Leak Prevention
  // 内存泄漏防范
  if (myChart) {
    myChart.dispose()
  }
  
  myChart = echarts.init(chartRef.value)
  
  const option = {
    title: { text: 'Class Attendance Trend ', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: data.map(item => item.date), // X-axis: Date / X轴：日期
      axisLabel: { rotate: 45 } // Tilt dates to prevent overlap / 日期倾斜防止重叠
    },
    yAxis: {
      type: 'value',
      name: 'Attendance Rate (%)',
      min: 0,
      max: 100
    },
    series: [
      {
        data: data.map(item => item.rate), // Y-axis: Attendance Rate / Y轴：出勤率
        type: 'line',
        smooth: true,
        itemStyle: { color: '#409EFF' },
        areaStyle: { color: 'rgba(64,158,255, 0.2)' }, // Make the fill area look better / 区域填充好看点
        label: { show: true, position: 'top', formatter: '{c}%' }
      }
    ]
  }
  
  myChart.setOption(option)
}

// Resize handler definition
// 定义独立的 resize 函数，便于后续卸载
const handleResize = () => {
  if (myChart) {
    myChart.resize()
  }
}

// Lifecycle hooks
// 生命周期钩子
onMounted(() => {
  loadClasses()
  window.addEventListener('resize', handleResize)
})

// Remove event listener and destroy Echarts to prevent memory leaks in SPA
// 在组件销毁时卸载事件监听器和 Echarts 实例，防止单页应用 (SPA) 发生严重内存泄漏
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (myChart) {
    myChart.dispose()
  }
})
</script>

<template>
  <div class="analytics-page">
    <div class="filter-bar">
      <h2><el-icon><TrendCharts /></el-icon> Data Analytics Center </h2>
      <div class="selector">
        <span> Select Class </span>
        <el-select 
          v-model="selectedClass" 
          placeholder="Please select" 
          @change="handleAnalyze" 
          style="width: 200px"
        >
          <el-option 
            v-for="item in classList" 
            :key="item.id" 
            :label="item.name" 
            :value="item.id" 
          />
        </el-select>
      </div>
    </div>

    <el-row :gutter="20" style="margin-top: 20px" v-loading="loading">
      <el-col :span="16">
        <el-card shadow="hover">
          <div ref="chartRef" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Warning /></el-icon> Absence Warning (Top 10)</span>
            </div>
          </template>
          
          <el-table :data="rankingData" stripe style="width: 100%" height="360">
            <el-table-column prop="name" label="Name" />
            <el-table-column prop="student_id" label="ID" />
            <el-table-column prop="count" label="Absences" align="center">
              <template #default="scope">
                <el-tag type="danger">{{ scope.row.count }} times</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.analytics-page { padding: 20px; max-width: 1400px; margin: 0 auto; }
.filter-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.filter-bar h2 { display: flex; align-items: center; gap: 10px; margin: 0; color: #303133; }
.card-header { display: flex; align-items: center; gap: 5px; font-weight: bold; color: #F56C6C; }
</style>