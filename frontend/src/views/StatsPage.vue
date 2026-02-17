<template>
  <div class="stats-page">
    <h1>统计信息</h1>
    
    <div class="stats-summary">
      <div class="summary-card">
        <div class="summary-value">{{ statsData.session_count || 0 }}</div>
        <div class="summary-label">总会话数</div>
      </div>
      
      <div class="summary-card">
        <div class="summary-value">{{ statsData.message_count || 0 }}</div>
        <div class="summary-label">总消息数</div>
      </div>
      
      <div class="summary-card">
        <div class="summary-value">{{ modelCount || 0 }}</div>
        <div class="summary-label">模型数量</div>
      </div>
    </div>
    
    <div class="stats-charts">
      <div class="chart-container">
        <h3>模型使用统计</h3>
        <div ref="modelChartRef" class="chart"></div>
      </div>
      
      <div class="chart-container">
        <h3>每日消息统计</h3>
        <div ref="dailyChartRef" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { statsApi } from '../api'
import * as echarts from 'echarts'

// 响应式数据
const statsData = ref({})
const modelChartRef = ref(null)
const dailyChartRef = ref(null)
const modelChart = ref(null)
const dailyChart = ref(null)

// 计算模型数量
const modelCount = computed(() => {
  return statsData.value.model_stats ? statsData.value.model_stats.length : 0
})

// 初始化图表
const initModelChart = () => {
  if (modelChartRef.value) {
    modelChart.value = echarts.init(modelChartRef.value)
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        data: statsData.value.model_stats?.map(item => item.model_name) || []
      },
      series: [
        {
          name: '模型使用',
          type: 'pie',
          radius: '60%',
          data: statsData.value.model_stats?.map(item => ({
            value: item.count,
            name: item.model_name
          })) || [],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    
    modelChart.value.setOption(option)
  }
}

const initDailyChart = () => {
  if (dailyChartRef.value) {
    dailyChart.value = echarts.init(dailyChartRef.value)
    
    const dailyStats = statsData.value.daily_stats || []
    const dates = dailyStats.map(item => item.date).reverse()
    const counts = dailyStats.map(item => item.count).reverse()
    
    const option = {
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c} 条消息'
      },
      xAxis: {
        type: 'category',
        data: dates
      },
      yAxis: {
        type: 'value',
        name: '消息数量'
      },
      series: [
        {
          data: counts,
          type: 'line',
          smooth: true,
          lineStyle: {
            color: '#409eff'
          },
          itemStyle: {
            color: '#409eff'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(64, 158, 255, 0.5)'
              },
              {
                offset: 1,
                color: 'rgba(64, 158, 255, 0.1)'
              }
            ])
          }
        }
      ]
    }
    
    dailyChart.value.setOption(option)
  }
}

// 加载数据
const loadStatsData = async () => {
  try {
    const data = await statsApi.getStats()
    statsData.value = data
    
    // 初始化图表
    initModelChart()
    initDailyChart()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 监听窗口大小变化，调整图表大小
const handleResize = () => {
  modelChart.value?.resize()
  dailyChart.value?.resize()
}

// 生命周期钩子
onMounted(() => {
  loadStatsData()
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
const onUnmounted = () => {
  window.removeEventListener('resize', handleResize)
  modelChart.value?.dispose()
  dailyChart.value?.dispose()
}
</script>

<style scoped>
.stats-page {
  padding: 20px 0;
}

.stats-page h1 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 30px;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.summary-card {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
}

.summary-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
}

.summary-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 10px;
}

.summary-label {
  font-size: 1rem;
  color: #606266;
}

.stats-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
}

.chart-container {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-container h3 {
  font-size: 1.2rem;
  color: #303133;
  margin-bottom: 20px;
}

.chart {
  width: 100%;
  height: 400px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-page h1 {
    font-size: 1.5rem;
  }
  
  .stats-summary {
    grid-template-columns: 1fr;
  }
  
  .stats-charts {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    padding: 15px;
  }
  
  .chart {
    height: 300px;
  }
}
</style>
