<template>
  <div class="law-page">
    <h1>法律助手</h1>
    
    <div class="law-container">
      <!-- 左侧聊天界面 -->
      <div class="chat-panel">
        <div class="panel-header">

          <h2>法律咨询</h2>
          <el-button type="primary" size="small" @click="clearChat" :disabled="messages.length === 0">
              <el-icon><Delete /></el-icon> 清空聊天     
          </el-button>
        </div>
        
        <div class="chat-content" ref="chatContentRef">
          <el-card v-if="messages.length === 0" class="empty-chat">
            <div class="empty-content">
              <el-icon class="empty-icon"><Message /></el-icon>
              <p>开始咨询法律问题</p>
            </div>
          </el-card>
          
          <div v-else class="messages-list">
            <div
              v-for="message in messages"
              :key="message.id"
              class="message-item"
              :class="message.role"
            >
              <div class="message-header">
                <span class="role">{{ message.role === 'user' ? '您' : '法律助手' }}</span>
                <span class="time">{{ formatTime(message.createdAt) }}</span>
              </div>
              <div class="message-body">
                <div class="message-content">{{ message.content }}</div>
                
                <!-- 显示参考文档 -->
                <div class="references" v-if="message.references && message.references.length > 0">
                  <h3>参考文档</h3>
                  <div v-for="(ref, index) in message.references" :key="index" class="reference-item">
                    <h4>{{ index + 1}}. {{ ref.title }}</h4>
                    <p>{{ ref.content }}</p>
                    <div class="reference-meta">
                      <span v-if="ref.pageNumber">页码: {{ ref.pageNumber }}</span>
                      <span v-if="ref.score">相关度: {{ (ref.score * 100).toFixed(1) }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 加载中状态 -->
            <div class="loading-message" v-if="isLoading">
              <div class="loading-content">
                <el-icon class="loading-icon"><Loading /></el-icon>
                <span>正在思考...</span>
              </div>
            </div>
          </div>
        </div>
      
        <div class="chat-input-area">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="请输入您的法律问题..."
            resize="none"
            @keyup.enter.native.exact="sendMessage"
            @keyup.enter.shift="$event.target.value += '\n'"
          />
          
          <div class="input-actions">
            <el-button
              type="primary"
              @click="sendMessage"
              :loading="isLoading"
              :disabled="!inputMessage.trim() || isLoading"
            >
              发送
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 右侧法律文档列表 -->
      <div class="law-docs-panel">
        <div class="panel-header">
          <h2>法律文档</h2>
          <el-button type="primary" size="small" @click="refreshIndex">
            <el-icon><Refresh /></el-icon> 刷新索引
          </el-button>
        </div>
        
        <div v-if="loadingDocs" class="loading">
          <el-icon><Loading /></el-icon>
          <span>加载文档列表...</span>
        </div>
        
        <el-table v-else :data="lawDocs" style="width: 100%" :fit="true">
          <el-table-column prop="filename" label="文件名" min-width="200">
            <template #default="scope">
              <span class="filename">{{ scope.row.filename }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="fileSize" label="文件大小" min-width="100">
            <template #default="scope">
              <span>{{ formatFileSize(scope.row.fileSize) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" min-width="150">
            <template #default="scope">
              <span>{{ formatDate(scope.row.createdAt) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="100">
            <template #default="scope">
              <el-button type="primary" size="small" @click="handleDownload(scope.row.filename)">
                <el-icon><Download /></el-icon>
                下载
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="document-count" v-if="documentCount > 0">
          已索引文档: {{ documentCount }} 个
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Download, Refresh, Delete, Message } from '@element-plus/icons-vue'
import { lawApi } from '../api/lawApi'

// 响应式数据
const lawDocs = ref([])
const documentCount = ref(0)
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const loadingDocs = ref(true)

// 引用
const chatContentRef = ref(null)

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes == null || isNaN(bytes) || bytes < 0) return '未知大小'
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (timestamp) => {
  if (timestamp == null || isNaN(timestamp) || timestamp <= 0) return '未知日期'
  
  let date
  if (typeof timestamp === 'string') {
    date = new Date(timestamp)
  } else if (typeof timestamp === 'number') {
    if (timestamp < 1000000000000) {
      date = new Date(timestamp * 1000)
    } else {
      date = new Date(timestamp)
    }
  } else {
    return '未知日期'
  }
  
  if (isNaN(date.getTime())) return '无效日期'
  
  return date.toLocaleString()
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  try {
    return date.toLocaleString('zh-CN', {
      timeZone: 'Asia/Macau',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }
}

// 加载法律文档列表
const loadLawDocs = async () => {
  try {
    loadingDocs.value = true
    const docs = await lawApi.getAvailableLawDocs()
    lawDocs.value = docs
    const countResponse = await lawApi.getLawDocumentCount()
    documentCount.value = countResponse.count
  } catch (error) {
    ElMessage.error(error.message || '获取法律文档列表失败')
    console.error('获取法律文档列表失败:', error)
  } finally {
    loadingDocs.value = false
  }
}

// 下载法律文档
const handleDownload = (filename) => {
  try {
    lawApi.downloadLawDoc(filename)
  } catch (error) {
    ElMessage.error(error.message || '下载法律文档失败')
  }
}

// 刷新文档索引
const refreshIndex = async () => {
  try {
    ElMessage.info('正在刷新文档索引...')
    await lawApi.refreshLawIndex()
    const countResponse = await lawApi.getLawDocumentCount()
    documentCount.value = countResponse.count
    ElMessage.success('文档索引刷新完成')
  } catch (error) {
    ElMessage.error(error.message || '刷新文档索引失败')
    console.error('刷新文档索引失败:', error)
  }
}

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isLoading.value) return
  
  isLoading.value = true
  const tempInput = inputMessage.value
  inputMessage.value = ''
  
  // 添加用户消息
  const tempUserMessage = {
    id: Date.now(),
    role: 'user',
    content: message,
    createdAt: new Date().toISOString()
  }
  messages.value.push(tempUserMessage)
  scrollToBottom()
  
  try {
    const response = await lawApi.lawRagQuery(message)
    
    // 添加AI回复
    const aiMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: response.answer,
      createdAt: new Date().toISOString(),
      references: response.references
    }
    messages.value.push(aiMessage)
    scrollToBottom()
  } catch (error) {
    ElMessage.error(error.message || '发送消息失败')
    console.error('发送消息失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContentRef.value) {
      chatContentRef.value.scrollTop = chatContentRef.value.scrollHeight
    }
  })
}

// 清空聊天
const clearChat = () => {
  messages.value = []
  ElMessage.success('聊天记录已清空')
}

// 页面加载
onMounted(() => {
  loadLawDocs()
})
</script>

<style scoped>
.law-page {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.law-page h1 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}
/* 页面布局 */
.law-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  box-sizing: border-box;
}

/* 面板样式 */
.law-docs-panel,
.chat-panel {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
}

.panel-header h2 {
  font-size: 1.2rem;
  color: #303133;
}

/* 法律文档列表 */
.law-docs-panel {
  min-height: 400px;
  max-height: 500px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.law-docs-panel .el-table {
  flex: 1;
  overflow-y: auto;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #999;
  flex: 1;
  min-height: 400px;
}

.loading span {
  margin-left: 10px;
}

.document-count {
  padding: 15px;
  font-size: 0.8rem;
  color: #606266;
  background-color: #f5f7fa;
  text-align: center;
  border-top: 1px solid #ebeef5;
}

/* 聊天界面 */
.chat-panel {
  min-height: 500px;
  max-height: 700px;
  display: flex;
  flex-direction: column;
  flex: 2;
  position: relative;
  overflow: hidden;
}

.chat-content {
  flex: 1;
  padding: 20px 20px 160px;
  overflow-y: auto;
  background-color: #fafafa;
  position: relative;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 100%;
}

.message-item {
  max-width: 80%;
  border-radius: 8px;
  padding: 15px;
}

.message-item.user {
  align-self: flex-end;
  background-color: #ecf5ff;
}

.message-item.assistant {
  align-self: flex-start;
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
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

.message-content {
  line-height: 1.6;
  color: #303133;
}

/* 参考文档 */
.references {
  margin-top: 15px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.references h3 {
  font-size: 0.9rem;
  color: #303133;
  margin-bottom: 10px;
  font-weight: 600;
}

/* 聊天输入区域 */
.chat-input-area {
  padding: 20px;
  border-top: 1px solid #ebeef5;
  background-color: white;
}

.chat-input-area textarea {
  resize: none;
  margin-bottom: 10px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 空状态 */
.empty-chat {
  display: flex;
  align-items: center;
  justify-content: center;
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

/* 加载消息 */
.loading-message {
  align-self: flex-start;
  margin-top: 10px;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  color: #606266;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 表格样式 */
.el-table {
  margin-top: 0;
  width: 100% !important;
  border-radius: 0;
  overflow: hidden;
}

.el-table__body {
  table-layout: auto !important;
  width: 100% !important;
}

/* 美化表头 */
.el-table th {
  background-color: #f5f7fa !important;
  font-weight: 600 !important;
  color: #333 !important;
  height: 48px !important;
  text-align: center !important;
}

/* 美化表格行 */
.el-table td {
  height: 48px !important;
  text-align: center !important;
  vertical-align: middle !important;
}

/* 美化表格行 hover 效果 */
.el-table__row:hover {
  background-color: #f0f9ff !important;
}

/* 美化文件名显示 */
.filename {
  font-weight: 500;
  color: #333;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .law-container {
    grid-template-columns: 1fr;
  }
  
  .chat-panel {
    height: 500px;
  }
}

@media (max-width: 768px) {
  .law-page {
    padding: 10px;
  }
  
  .law-page h1 {
    font-size: 20px;
  }
  
  .panel-header {
    padding: 15px;
  }
  
  .panel-header h2 {
    font-size: 1.1rem;
  }
  
  .chat-content {
    padding: 15px;
  }
  
  .chat-input-area {
    padding: 15px;
  }
  
  .message-item {
    max-width: 90%;
  }
}

/* 聊天输入区域 */
.chat-input-area {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 15px;
  border-top: 1px solid #ebeef5;
  background-color: white;
  z-index: 10;
}

.input-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}
</style>
