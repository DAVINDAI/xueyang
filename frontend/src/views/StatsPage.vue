<template>
  <div class="stats-page">
    <h1>统计信息</h1>
    
    <div class="stats-summary">
      <div class="summary-card">
        <div class="summary-value">{{ statsData.sessionCount || 0 }}</div>
        <div class="summary-label">总会话数</div>
      </div>
      
      <div class="summary-card">
        <div class="summary-value">{{ statsData.messageCount || 0 }}</div>
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

  <div class="celebration-modal" v-if="showCelebration">
    <transition name="modal-fade">
      <div class="modal-content-wrapper">
        <div class="confetti-container">
          <div class="confetti" v-for="n in 50" :key="n"></div>
        </div>
        
        <div class="celebration-content">
          <div class="emoji-large">🎉</div>
          <h2>太棒了！</h2>
          <p>你刚刚发现了：{{ discovery }}</p>
          <p class="encouragement">{{ encouragement }}</p>
          
          <div class="achievement-badge">
            <span class="badge-emoji">🏆</span>
            <span class="badge-text">探索者徽章</span>
          </div>
          
          <button class="continue-btn" @click="continueExploring">
            <span>继续探索</span>
            <span class="arrow">→</span>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { statsApi } from '../api'
import * as echarts from 'echarts'

// 响应式数据
const statsData = ref({})
const modelChartRef = ref(null)
const dailyChartRef = ref(null)
const modelChart = ref(null)
const dailyChart = ref(null)
const showCelebration = ref(false)
const discovery = ref('统计数据的奥秘！')
const encouragement = ref('继续探索，发现更多精彩！')
const colors = ['#8b5cf6', '#0ea5e9', '#f59e0b', '#10b981', '#ef4444']

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
        data: statsData.value.modelStats?.map(item => item.modelName) || []
      },
      series: [
        {
          name: '模型使用',
          type: 'pie',
          radius: '60%',
          data: statsData.value.modelStats?.map(item => ({
            value: item.count,
            name: item.modelName
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
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
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

// 动态创建五彩纸屑
const createConfetti = () => {
  nextTick(() => {
    const confettiContainer = document.querySelector('.confetti-container')
    if (confettiContainer) {
      colors.forEach(color => {
        for (let i = 0; i < 10; i++) {
          const confetti = document.createElement('div')
          confetti.className = 'confetti'
          confetti.style.left = `${Math.random() * 100}%`
          confetti.style.top = `${Math.random() * 100}%`
          confetti.style.setProperty('--color', color)
          confetti.style.animationDuration = `${Math.random() * 3 + 2}s`
          confetti.style.animationDelay = `${Math.random() * 2}s`
          confettiContainer.appendChild(confetti)
        }
      })
    }
  })
}

// 加载数据
const loadStatsData = async () => {
  try {
    const data = await statsApi.getStats()
    statsData.value = data
    
    // 初始化图表
    // initModelChart()
    // initDailyChart()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 监听窗口大小变化，调整图表大小
const handleResize = () => {
  modelChart.value?.resize()
  dailyChart.value?.resize()
}

// 继续探索
const continueExploring = () => {
  showCelebration.value = false
  // 清理动态创建的 confetti 元素
  nextTick(() => {
    const confettiContainer = document.querySelector('.confetti-container')
    if (confettiContainer) {
      confettiContainer.innerHTML = ''
    }
  })
}

// 生命周期钩子
onMounted(() => {
  loadStatsData()
  window.addEventListener('resize', handleResize)
  
  // 显示庆祝模态框
  // showCelebration.value = true
  // createConfetti()
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  modelChart.value?.dispose()
  dailyChart.value?.dispose()
  
  // 关闭模态框
  showCelebration.value = false
})
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

/* 模态框进入动画 */
.modal-fade-enter-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from {
  opacity: 0;
}

/* 模态框离开动画 */
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-leave-to {
  opacity: 0;
  pointer-events: none;
}

/* 模态框内容离开动画 */
.modal-fade-leave-active .modal-content-wrapper {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.modal-fade-leave-to .modal-content-wrapper {
  opacity: 0;
  transform: scale(0.9);
}

/* 模态框内容进入动画 */
.modal-fade-enter-active .modal-content-wrapper {
  animation: bounceIn 0.8s ease;
}

.celebration-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.confetti-container {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.confetti {
  position: absolute;
  width: 10px;
  height: 10px;
  background: var(--color);
  border-radius: 2px;
  animation: fall linear infinite;
}

.celebration-content {
  text-align: center;
  background: white;
  padding: 40px;
  border-radius: 30px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  position: relative;
}

.emoji-large {
  font-size: 60px;
  animation: pulse 2s infinite;
  margin-bottom: 20px;
}

h2 {
  color: #7c3aed;
  font-size: 32px;
  margin-bottom: 10px;
}

.encouragement {
  color: #6d28d9;
  font-size: 18px;
  margin: 20px 0;
  font-style: italic;
}

.achievement-badge {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  padding: 10px 20px;
  border-radius: 50px;
  margin: 25px 0;
  animation: wiggle 2s infinite;
}

.badge-emoji {
  font-size: 24px;
  margin-right: 10px;
}

.badge-text {
  color: #92400e;
  font-weight: 600;
}

.continue-btn {
  background: linear-gradient(135deg, #8b5cf6, #0ea5e9);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 50px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 20px auto 0;
  transition: all 0.3s ease;
}

.continue-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);
}

.arrow {
  animation: slide 1s infinite;
}

/* 动画定义 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes bounceIn {
  0% { transform: scale(0.3); opacity: 0; }
  50% { transform: scale(1.05); }
  70% { transform: scale(0.9); }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

@keyframes wiggle {
  0%, 100% { transform: rotate(0); }
  25% { transform: rotate(-3deg); }
  75% { transform: rotate(3deg); }
}

@keyframes slide {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(5px); }
}

@keyframes fall {
  to {
    transform: translateY(100vh) rotate(360deg);
    opacity: 0;
  }
}
</style>
