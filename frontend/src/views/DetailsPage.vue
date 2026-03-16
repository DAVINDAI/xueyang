<template>
  <div class="details-page">
    <h1>详情查看</h1>
    
    <div class="details-container">
      <!-- 会话列表 -->
      <div class="sessions-list">
        <h2>会话列表</h2>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索会话名称"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-card v-if="sessions.length === 0" class="empty-card">
          <div class="empty-content">
            <el-icon class="empty-icon"><ChatLineSquare /></el-icon>
            <p>暂无会话记录</p>
          </div>
        </el-card>
        
        <el-list v-else class="sessions">
          <el-list-item
            v-for="session in filteredSessions"
            :key="session.id"
            class="session-item"
            :class="{ active: selectedSession?.id === session.id }"
            @click="selectSession(session)"
          >
            <template #default>
              <div class="session-info">
                <h3>{{ session.sessionName }}</h3>
                <div class="session-meta">
                  <span class="model-tag">{{ session.modelName }}</span>
                  <span class="message-count">{{ session.messageCount }} 条消息</span>
                  <span class="time">{{ formatTime(session.updatedAt) }}</span>
                </div>
              </div>
            </template>
          </el-list-item>
        </el-list>
      </div>
      
      <!-- 会话详情 -->
      <div class="session-details" v-if="selectedSession">
        <div class="session-header">
          <h2>{{ selectedSession.sessionName }}</h2>
          <div class="session-actions">
            <el-button type="primary" size="small" @click="editSessionName">
              <el-icon><Edit /></el-icon> 重命名
            </el-button>
            <el-button type="danger" size="small" @click="deleteSession">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </div>
        </div>
        
        <div class="session-meta-info">
          <span class="meta-item">
            <el-icon><Cpu /></el-icon> {{ selectedSession.modelName }}
          </span>
          <span class="meta-item">
            <el-icon><Message /></el-icon> {{ sessionMessages.length }} 条消息
          </span>
          <span class="meta-item">
            <el-icon><Timer /></el-icon> 创建于 {{ formatTime(selectedSession.createdAt) }}
          </span>
          <span class="meta-item">
            <el-icon><Refresh /></el-icon> 更新于 {{ formatTime(selectedSession.updatedAt) }}
          </span>
        </div>
        
        <div class="messages-container">
          <h3>消息记录</h3>
          
          <el-card v-if="sessionMessages.length === 0" class="empty-card">
            <div class="empty-content">
              <el-icon class="empty-icon"><Message /></el-icon>
              <p>暂无消息记录</p>
            </div>
          </el-card>
          
          <div v-else class="messages">
            <div
              v-for="message in sessionMessages"
              :key="message.id"
              class="message-item"
              :class="message.role"
            >
              <div class="message-header">
                <span class="role">{{ message.role === 'user' ? '用户' : 'AI' }}</span>
                <span class="time">{{ formatTime(message.createdAt) }}</span>
                <span v-if="message.tokenCount" class="token-count">{{ message.tokenCount }} tokens</span>
              </div>
              <div class="message-content">{{ message.content }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 未选择会话时的提示 -->
      <div class="no-selection" v-else>
        <div class="no-selection-content">
          <el-icon class="no-selection-icon"><View /></el-icon>
          <p>请选择一个会话查看详情</p>
        </div>
      </div>
    </div>
    
    <!-- 重命名对话框 -->
    <el-dialog
      v-model="renameDialogVisible"
      title="重命名会话"
      width="400px"
    >
      <el-input v-model="newSessionName" placeholder="请输入新的会话名称" />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="renameDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmRename">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除会话"
      width="400px"
    >
      <p>确定要删除会话 "{{ selectedSession?.sessionName }}" 吗？此操作不可恢复。</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete">删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { detailsApi, chatApi } from '../api'
import { Search, ChatLineSquare, Edit, Delete, Cpu, Message, Timer, Refresh, View } from '@element-plus/icons-vue'

// 响应式数据
const sessions = ref([])
const selectedSession = ref(null)
const sessionMessages = ref([])
const searchKeyword = ref('')
const renameDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const newSessionName = ref('')

// 过滤会话
const filteredSessions = computed(() => {
  if (!searchKeyword.value) {
    return sessions.value
  }
  return sessions.value.filter(session => 
    session.sessionName.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 加载会话列表
const loadSessions = async () => {
  try {
    const data = await detailsApi.getAllDetails()
    sessions.value = data.sessions || []
  } catch (error) {
    console.error('加载会话列表失败:', error)
  }
}

// 选择会话
const selectSession = async (session) => {
  selectedSession.value = session
  try {
    const data = await detailsApi.getSessionDetails(session.id)
    sessionMessages.value = data.messages || []
  } catch (error) {
    console.error('加载会话详情失败:', error)
  }
}

// 编辑会话名称
const editSessionName = () => {
  if (selectedSession.value) {
    newSessionName.value = selectedSession.value.sessionName
    renameDialogVisible.value = true
  }
}

// 确认重命名
const confirmRename = async () => {
  if (selectedSession.value && newSessionName.value) {
    try {
      await chatApi.updateSession(selectedSession.value.id, newSessionName.value)
      selectedSession.value.sessionName = newSessionName.value
      await loadSessions()
      renameDialogVisible.value = false
      
      ElMessage({
        message: '会话重命名成功',
        type: 'success'
      })
    } catch (error) {
      console.error('重命名会话失败:', error)
      ElMessage.error('重命名会话失败')
    }
  }
}

// 删除会话
const deleteSession = () => {
  if (selectedSession.value) {
    deleteDialogVisible.value = true
  }
}

// 确认删除
const confirmDelete = async () => {
  if (selectedSession.value) {
    try {
      await chatApi.deleteSession(selectedSession.value.id)
      selectedSession.value = null
      sessionMessages.value = []
      await loadSessions()
      deleteDialogVisible.value = false
      
      ElMessage({
        message: '会话删除成功',
        type: 'success'
      })
    } catch (error) {
      console.error('删除会话失败:', error)
      ElMessage.error('删除会话失败')
    }
  }
}

// 生命周期钩子
onMounted(() => {
  loadSessions()
})

// 导入Element Plus消息组件
import { ElMessage } from 'element-plus'
</script>

<style scoped>
.details-page {
  padding: 20px 0;
}

.details-page h1 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 30px;
}

.details-container {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 30px;
  min-height: 600px;
}

/* 会话列表 */
.sessions-list {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  height: fit-content;
  position: sticky;
  top: 20px;
}

.sessions-list h2 {
  font-size: 1.5rem;
  color: #303133;
  margin-bottom: 20px;
}

.search-input {
  margin-bottom: 20px;
}

.sessions {
  max-height: 600px;
  overflow-y: auto;
}

.session-item {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 4px;
  margin-bottom: 10px;
}

.session-item:hover {
  background-color: #f5f7fa;
}

.session-item.active {
  background-color: #ecf5ff;
}

.session-info h3 {
  font-size: 1rem;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.session-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.8rem;
  color: #606266;
}

.model-tag {
  padding: 2px 8px;
  background-color: #ecf5ff;
  color: #409eff;
  border-radius: 10px;
}

.message-count {
  display: flex;
  align-items: center;
}

.time {
  margin-left: auto;
}

/* 会话详情 */
.session-details {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.session-header h2 {
  font-size: 1.5rem;
  color: #303133;
}

.session-actions {
  display: flex;
  gap: 10px;
}

.session-meta-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
  color: #606266;
}

.messages-container h3 {
  font-size: 1.2rem;
  color: #303133;
  margin-bottom: 20px;
}

.messages {
  max-height: 500px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.message-item {
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 8px;
}

.message-item.user {
  background-color: #ecf5ff;
  margin-right: 20%;
}

.message-item.assistant {
  background-color: #f0f9eb;
  margin-left: 20%;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 0.8rem;
}

.message-header .role {
  font-weight: 500;
  color: #303133;
}

.message-header .time {
  color: #909399;
}

.message-header .token-count {
  margin-left: auto;
  color: #909399;
}

.message-content {
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
}

/* 空状态 */
.empty-card {
  margin-top: 20px;
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

.no-selection {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.no-selection-content {
  text-align: center;
}

.no-selection-icon {
  font-size: 64px;
  color: #c0c4cc;
  margin-bottom: 20px;
}

.no-selection-content p {
  font-size: 1.2rem;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .details-container {
    grid-template-columns: 1fr;
  }
  
  .sessions-list {
    position: static;
  }
  
  .sessions {
    max-height: 300px;
  }
  
  .message-item.user,
  .message-item.assistant {
    margin-right: 0;
    margin-left: 0;
  }
}

@media (max-width: 768px) {
  .details-page h1 {
    font-size: 1.5rem;
  }
  
  .sessions-list {
    padding: 15px;
  }
  
  .session-details {
    padding: 15px;
  }
  
  .session-meta-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
