<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { getClasses } from '@/api/classes'
import { getClassTrend, getAbsentRanking } from '@/api/analytics'
import * as echarts from 'echarts'
import { TrendCharts, Warning } from '@element-plus/icons-vue'

// 数据状态
const classList = ref([])
const selectedClass = ref(null)
const rankingData = ref([])
const loading = ref(false)

// 图表实例容器
const chartRef = ref(null)
let myChart = null

// 1. 加载班级列表
const loadClasses = async () => {
  const res = await getClasses()
  classList.value = res.data || res
  // 默认选中第一个班级
  if (classList.value.length > 0) {
    selectedClass.value = classList.value[0].id
    handleAnalyze() // 自动开始分析
  }
}

// 2. 核心：获取数据并渲染图表
const handleAnalyze = async () => {
  if (!selectedClass.value) return
  loading.value = true
  
  try {
    // 并行请求：同时获取 趋势数据 和 排行榜数据
    const [trendRes, rankRes] = await Promise.all([
      getClassTrend(selectedClass.value),
      getAbsentRanking(selectedClass.value)
    ])
    
    const trendData = trendRes.data || trendRes
    rankingData.value = rankRes.data || rankRes
    
    // 渲染图表
    renderChart(trendData)
    
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// 3. ECharts 渲染逻辑
const renderChart = (data) => {
  if (!chartRef.value) return
  
  // 如果实例已存在，先销毁（防止内存泄漏）
  if (myChart) myChart.dispose()
  
  myChart = echarts.init(chartRef.value)
  
  const option = {
    title: { text: '班级出勤率趋势图', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: data.map(item => item.date), // X轴：日期
      axisLabel: { rotate: 45 } // 日期倾斜防止重叠
    },
    yAxis: {
      type: 'value',
      name: '出勤率(%)',
      min: 0,
      max: 100
    },
    series: [
      {
        data: data.map(item => item.rate), // Y轴：出勤率
        type: 'line',
        smooth: true,
        itemStyle: { color: '#409EFF' },
        areaStyle: { color: 'rgba(64,158,255, 0.2)' }, // 区域填充好看点
        label: { show: true, position: 'top', formatter: '{c}%' }
      }
    ]
  }
  
  myChart.setOption(option)
}

// 窗口大小改变时，图表也要自适应
window.addEventListener('resize', () => {
  myChart && myChart.resize()
})

onMounted(loadClasses)
</script>

<template>
  <div class="analytics-page">
    <div class="filter-bar">
      <h2><el-icon><TrendCharts /></el-icon> 数据分析中心</h2>
      <div class="selector">
        <span>选择班级：</span>
        <el-select v-model="selectedClass" placeholder="请选择" @change="handleAnalyze" style="width: 200px">
          <el-option v-for="item in classList" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </div>
    </div>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card shadow="hover">
          <div ref="chartRef" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Warning /></el-icon> 缺勤预警 (Top 10)</span>
            </div>
          </template>
          
          <el-table :data="rankingData" stripe style="width: 100%" height="360">
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="student_id" label="学号" />
            <el-table-column prop="count" label="缺勤次数" align="center">
              <template #default="scope">
                <el-tag type="danger">{{ scope.row.count }} 次</el-tag>
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