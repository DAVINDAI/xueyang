<template>
  <div class="memo-page">
    <h1>备忘录</h1>
    
    <div class="memo-container">
      <el-card v-if="memos.length === 0" class="empty-card">
        <div class="empty-content">
          <el-icon class="empty-icon"><Document /></el-icon>
          <p>暂无备忘录，在聊天界面输入 "记一下" 或 "m" 创建备忘录</p>
        </div>
      </el-card>
      
      <div v-else class="memos-list">
        <el-card 
          v-for="memo in memos" 
          :key="memo.id"
          class="memo-card"
          @click="viewSession(memo.originalSessionId)"
        >
          <template #header>
            <div class="memo-header">
              <h3>{{ memo.analysis?.topics[0]?.topic || '未命名主题' }}</h3>
              <span class="memo-time">{{ formatTime(memo.createdAt) }}</span>
            </div>
          </template>
          
          <div class="memo-content">
            <div v-if="memo.analysis?.topics[0]" class="memo-topic">
              <div class="topic-item">
                <span class="label">用户问题：</span>
                <span class="value">{{ memo.analysis.topics[0].userQuestion || '无' }}</span>
              </div>
              <div class="topic-item" v-if="memo.analysis.topics[0].aiKeyPoints && memo.analysis.topics[0].aiKeyPoints.length > 0">
                <span class="label">AI 要点：</span>
                <ul class="key-points">
                  <li v-for="(point, index) in memo.analysis.topics[0].aiKeyPoints.slice(0, 3)" :key="index">
                    {{ point }}
                  </li>
                  <li v-if="memo.analysis.topics[0].aiKeyPoints.length > 3" class="more">
                    等 {{ memo.analysis.topics[0].aiKeyPoints.length }} 项
                  </li>
                </ul>
              </div>
              <div class="topic-item" v-if="memo.analysis.topics[0].technicalTerms && memo.analysis.topics[0].technicalTerms.length > 0">
                <span class="label">技术术语：</span>
                <div class="tags">
                  <el-tag v-for="(term, index) in memo.analysis.topics[0].technicalTerms" :key="index" size="small" effect="plain">
                    {{ term }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div v-else class="memo-empty">
              <p>备忘录内容解析失败</p>
            </div>
          </div>
          
          <div class="memo-footer">
            <el-button type="text" size="small" @click.stop="deleteMemo(memo.id)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
            <el-button type="primary" size="small" @click.stop="viewSession(memo.originalSessionId)">
              查看会话
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { chatApi } from '../api'
import { Document, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const memos = ref([])

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  try {
    // 尝试使用 timeZone 参数指定澳门时区（东8区）
    return date.toLocaleString('zh-CN', {
      timeZone: 'Asia/Macau',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    // 兼容性处理：如果浏览器不支持 timeZone 参数，使用默认设置
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

// 加载备忘录列表
const loadMemos = async () => {
  try {
    const data = await chatApi.listMemos()
    memos.value = data
  } catch (error) {
    console.error('加载备忘录失败:', error)
    ElMessage.error('加载备忘录失败')
  }
}

// 查看会话
const viewSession = (sessionId) => {
  router.push({ 
    path: '/chat',
    query: { sessionId }
  })
}

// 删除备忘录
const deleteMemo = async (memoId) => {
  try {
    await chatApi.deleteMemo(memoId)
    ElMessage({
      message: '备忘录删除成功',
      type: 'success'
    })
    // 重新加载备忘录列表
    await loadMemos()
  } catch (error) {
    console.error('删除备忘录失败:', error)
    ElMessage.error('删除备忘录失败')
  }
}

// 生命周期钩子
onMounted(() => {
  loadMemos()
})
</script>

<style scoped>
.memo-page {
  padding: 0;
  margin: 0 -20px;
  width: calc(100% + 40px);
}

.memo-page h1 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 30px;
  padding: 0 20px;
}

.memo-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.memos-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.memo-card {
  cursor: pointer;
  transition: all 0.3s;
}

.memo-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.memo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.memo-header h3 {
  font-size: 1.1rem;
  font-weight: 500;
  color: #303133;
  margin: 0;
}

.memo-time {
  font-size: 0.8rem;
  color: #909399;
}

.memo-content {
  margin: 15px 0;
  line-height: 1.6;
}

.memo-topic {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.topic-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #606266;
}

.value {
  font-size: 0.9rem;
  color: #303133;
}

.key-points {
  margin: 0;
  padding-left: 20px;
  font-size: 0.9rem;
  color: #303133;
}

.key-points li {
  margin-bottom: 4px;
}

.key-points .more {
  color: #909399;
  font-style: italic;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.memo-empty {
  color: #909399;
  text-align: center;
  padding: 20px 0;
}

.memo-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.empty-card {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.empty-content {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.empty-content p {
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .memo-page h1 {
    font-size: 1.5rem;
  }
  
  .memos-list {
    grid-template-columns: 1fr;
  }
  
  .memo-container {
    padding: 0 10px;
  }
  
  .memo-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .memo-footer {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>