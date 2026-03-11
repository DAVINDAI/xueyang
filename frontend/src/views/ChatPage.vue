<template>
  <div class="chat-page">
    <h1>对话连接</h1>
    
    <div class="chat-container">
      <!-- 左侧会话列表 -->
      <div class="chat-sessions">
        <div class="sessions-header">
          <h2>会话</h2>
          <el-button type="primary" size="small" @click="showCreateSessionDialog = true">
            <el-icon><Plus /></el-icon> 新建
          </el-button>
        </div>
        
        <el-input
          v-model="sessionSearchKeyword"
          placeholder="搜索会话"
          class="session-search"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-card v-if="sessions.length === 0" class="empty-card">
          <div class="empty-content">
            <el-icon class="empty-icon"><ChatLineSquare /></el-icon>
            <p>暂无会话，点击新建开始聊天</p>
          </div>
        </el-card>
        
        <el-list v-else class="sessions-list">
          <el-list-item
            v-for="session in filteredSessions"
            :key="session.id"
            class="session-item"
            :class="{ active: activeSession?.id === session.id }"
            @click="selectSession(session)"
          >
            <template #default>
              <div class="session-info">
                <h3>{{ session.sessionName }}</h3>
                <div class="session-meta">
                  <span class="model-tag">{{ session.modelName }}</span>
                  <span class="time">{{ formatTime(session.updatedAt) }}</span>
                </div>
              </div>
            </template>
          </el-list-item>
        </el-list>
      </div>
      
      <!-- 右侧聊天界面 -->
      <div class="chat-main" v-if="activeSession">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <div class="chat-title">
            <h2>{{ activeSession.sessionName }}</h2>
            <el-button type="text" size="small" @click="editSessionName">
              <el-icon><Edit /></el-icon>
            </el-button>
          </div>
          
          <div class="chat-settings">
            <el-select v-model="selectedModel" placeholder="选择模型" size="small" @change="changeModel">
              <el-option
                v-for="model in availableModels"
                :key="model.value"
                :label="model.label"
                :value="model.value"
              />
            </el-select>
            
            <div class="context-status" v-if="contextStatus">
              <span class="status-text">
                {{ contextStatus.currentTokens }} / {{ contextStatus.contextLength }} tokens
              </span>
              <el-progress
                :percentage="Math.min((contextStatus.currentTokens / contextStatus.contextLength) * 100, 100)"
                :color="getProgressColor"
                :stroke-width="6"
                size="small"
              />
            </div>
          </div>
        </div>
        
        <!-- 聊天内容 -->
        <div class="chat-content" ref="chatContentRef" @scroll="handleContentScroll">
          <el-card v-if="messages.length === 0" class="empty-chat">
            <div class="empty-content">
              <el-icon class="empty-icon"><Message /></el-icon>
              <p>开始与大模型聊天吧</p>
            </div>
          </el-card>
          
          <div v-else class="messages-list">
            <div
              v-for="message in messages"
              :key="message.id"
              :id="`message-${message.id}`"
              class="message-item"
              :class="message.role"
            >
              <div class="message-header">
                <span class="role">{{ message.role === 'user' ? '你' : 'AI' }}</span>
                <span class="time">{{ formatTime(message.createdAt) }}</span>
                <span v-if="message.tokenCount" class="token-count">{{ message.tokenCount }} tokens</span>
              </div>
              <div class="message-body">
                <div class="message-content markdown-body" v-html="renderMarkdown(message.content)"></div>
              </div>
            </div>
            
            <!-- 加载中状态 -->
            <div class="loading-message" v-if="isLoading">
              <div class="loading-content">
                <el-icon class="loading-icon"><Loading /></el-icon>
                <span>AI正在思考...</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 悬浮按钮 -->
        <div class="floating-buttons" v-if="messages.length > 0">
          <el-button
            class="floating-btn"
            type="primary"
            circle
            @click="scrollToTop"
            title="滚动到顶部"
          >
            <el-icon><Top /></el-icon>
          </el-button>
          <el-button
            class="floating-btn"
            type="primary"
            circle
            @click="scrollToBottom"
            title="滚动到底部"
          >
            <el-icon><Bottom /></el-icon>
          </el-button>
        </div>
        
        <!-- 输入区域 -->
        <div class="chat-input-area">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入消息..."
            resize="none"
            @keyup.enter.exact="sendMessage"
            @keyup.enter.shift="$event.target.value += '\n'"
          />
          
          <div class="input-actions">
            <div class="input-info" v-if="inputTokenCount">
              {{ inputTokenCount }} tokens
            </div>
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
      
      <!-- 未选择会话时的提示 -->
      <div class="no-session-selected" v-else>
        <div class="no-session-content">
          <el-icon class="no-session-icon"><ChatDotSquare /></el-icon>
          <p>请选择或创建一个会话开始聊天</p>
        </div>
      </div>
    </div>
    
    <!-- 新建会话对话框 -->
    <el-dialog
      v-model="showCreateSessionDialog"
      title="新建会话"
      width="400px"
    >
      <el-form>
        <el-form-item label="会话名称">
          <el-input v-model="newSessionName" placeholder="请输入会话名称" />
        </el-form-item>
        <el-form-item label="模型选择">
          <el-select v-model="newSessionModel" placeholder="选择模型">
            <el-option
              v-for="model in availableModels"
              :key="model.value"
              :label="model.label"
              :value="model.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateSessionDialog = false">取消</el-button>
          <el-button type="primary" @click="createSession">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 重命名会话对话框 -->
    <el-dialog
      v-model="showRenameDialog"
      title="重命名会话"
      width="400px"
    >
      <el-input v-model="renameSessionName" placeholder="请输入新的会话名称" />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRenameDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmRename">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { chatApi } from '../api'
import { Search, Plus, ChatLineSquare, Edit, Message, Loading, ChatDotSquare, Top, Bottom } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import mermaid from 'mermaid'

// 配置marked
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (__) {}
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

// 路由
const route = useRoute()

// 响应式数据
const sessions = ref([])
const activeSession = ref(null)
const messages = ref([])
const inputMessage = ref('')
const selectedModel = ref('qwen-plus')
const sessionSearchKeyword = ref('')
const isLoading = ref(false)
const contextStatus = ref(null)
const inputTokenCount = ref(0)

// 对话框状态
const showCreateSessionDialog = ref(false)
const showRenameDialog = ref(false)
const newSessionName = ref('')
const newSessionModel = ref('qwen-plus')
const renameSessionName = ref('')

// DOM引用
const chatContentRef = ref(null)
const userScrolled = ref(false)

// Markdown 渲染函数
const renderMarkdown = (content) => {
  if (!content) return ''
  // 使用marked.parse将Markdown转换为HTML
  let html = marked.parse(content)
  // 检查返回值类型（marked v17+的新API）
  if (typeof html === 'object' && html.html) {
    html = html.html
  }
  // 手动处理Mermaid代码块
  html = html.replace(/<pre><code class="language-mermaid">([\s\S]*?)<\/code><\/pre>/g, '<div class="mermaid">$1</div>')
  return html
}

// 高亮所有代码块和渲染Mermaid图表
const highlightAllCodeBlocks = () => {
  nextTick(() => {
    // 高亮代码块
    document.querySelectorAll('.markdown-body pre code').forEach((block) => {
      hljs.highlightElement(block)
    })
    // 渲染Mermaid图表
    mermaid.init()
  })
}

// 可用模型
const availableModels = [
  { value: 'glm-5', label: 'GLM 5' },
  { value: 'qwen-plus', label: 'Qwen Plus' },
  { value: 'deepseek-chat', label: 'DeepSeek Chat' }
]

// 过滤会话
const filteredSessions = computed(() => {
  if (!sessionSearchKeyword.value) {
    return sessions.value
  }
  return sessions.value.filter(session => 
    session.sessionName.toLowerCase().includes(sessionSearchKeyword.value.toLowerCase())
  )
})

// 进度条颜色
const getProgressColor = computed(() => {
  if (!contextStatus.value) return '#409eff'
  
  const ratio = contextStatus.value.currentTokens / contextStatus.value.contextLength
  if (ratio > 0.8) return '#f56c6c'
  if (ratio > 0.6) return '#e6a23c'
  return '#409eff'
})

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
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    // 兼容性处理：如果浏览器不支持 timeZone 参数，使用默认设置
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }
}

// 加载会话列表
const loadSessions = async () => {
  try {
    const data = await chatApi.listSessions()
    sessions.value = data
    
    // 如果有会话
    if (sessions.value.length > 0) {
      // 优先检查URL中的sessionId参数
      const urlSessionId = route.query.sessionId
      if (urlSessionId) {
        const targetSession = sessions.value.find(s => s.id === Number(urlSessionId))
        if (targetSession) {
          selectSession(targetSession)
          return
        }
      }
      
      // 如果没有URL参数或没有找到对应的会话，选择第一个
      if (!activeSession.value) {
        selectSession(sessions.value[0])
      }
    }
  } catch (error) {
    console.error('加载会话列表失败:', error)
    ElMessage.error('加载会话列表失败')
  }
}

// 跳转到指定消息
const scrollToMessage = (messageId) => {
  nextTick(() => {
    const element = document.getElementById(`message-${messageId}`)
    if (element && chatContentRef.value) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  })
}

// 选择会话
const selectSession = async (session) => {
  activeSession.value = session
  selectedModel.value = session.modelName
  
  try {
    const data = await chatApi.getMessages(session.id)
    messages.value = data
    
    // 检查是否有消息ID需要跳转
    const messageId = route.query.messageId
    if (messageId) {
      nextTick(() => {
        scrollToMessage(messageId)
      })
    } else {
      scrollToBottom()
    }
    
    highlightAllCodeBlocks()
  } catch (error) {
    console.error('加载消息失败:', error)
    ElMessage.error('加载消息失败')
  }
}

// 创建会话
const createSession = async () => {
  if (!newSessionName.value.trim()) {
    ElMessage.warning('请输入会话名称')
    return
  }
  
  try {
    const data = await chatApi.createSession(newSessionName.value.trim(), newSessionModel.value)
    await loadSessions()
    const newSession = sessions.value.find(s => s.id === data.sessionId)
    if (newSession) {
      selectSession(newSession)
    }
    showCreateSessionDialog.value = false
    newSessionName.value = ''
    
    ElMessage({
      message: '会话创建成功',
      type: 'success'
    })
  } catch (error) {
    console.error('创建会话失败:', error)
    ElMessage.error('创建会话失败')
  }
}

// 编辑会话名称
const editSessionName = () => {
  if (activeSession.value) {
    renameSessionName.value = activeSession.value.sessionName
    showRenameDialog.value = true
  }
}

// 确认重命名
const confirmRename = async () => {
  if (!renameSessionName.value.trim()) {
    ElMessage.warning('请输入会话名称')
    return
  }
  
  if (activeSession.value) {
    try {
      await chatApi.updateSession(activeSession.value.id, renameSessionName.value.trim())
      activeSession.value.sessionName = renameSessionName.value.trim()
      await loadSessions()
      showRenameDialog.value = false
      
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

// 切换模型
const changeModel = () => {
  if (activeSession.value) {
    activeSession.value.modelName = selectedModel.value
  }
}

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || !activeSession.value || isLoading.value) return
  
  isLoading.value = true
  const tempInput = inputMessage.value
  inputMessage.value = ''
  
  // 在发送请求之前，先将用户消息追加到对话列表
  const tempUserMessage = {
    id: Date.now(),
    role: 'user',
    content: message,
    createdAt: new Date().toISOString(),
    tokenCount: inputTokenCount.value
  }
  messages.value.push(tempUserMessage)
  
  // 重置用户滚动状态
  userScrolled.value = false
  
  // 添加临时的AI消息用于流式渲染
  const tempAiMessage = {
    id: Date.now() + 1,
    role: 'assistant',
    content: '',
    createdAt: new Date().toISOString(),
    tokenCount: 0,
    isStreaming: true
  }
  messages.value.push(tempAiMessage)
  autoScrollToBottom()
  
  try {
    let fullResponse = ''
    
    // 发送流式消息
    await chatApi.chatCompletionStream(
      activeSession.value.id,
      selectedModel.value,
      message,
      (chunk) => {
        // 流式更新AI消息内容
        fullResponse += chunk
        const aiMessageIndex = messages.value.findIndex(m => m.id === tempAiMessage.id)
        if (aiMessageIndex !== -1) {
          messages.value[aiMessageIndex].content = fullResponse
          autoScrollToBottom()
        }
      },
      async (data) => {
        // 流式输出完成
        const aiMessageIndex = messages.value.findIndex(m => m.id === tempAiMessage.id)
        if (aiMessageIndex !== -1) {
          messages.value[aiMessageIndex].isStreaming = false
        }
        
        // 更新上下文状态
        contextStatus.value = data.contextStatus
        
        // 重新加载完整消息（确保token数等信息正确）
        await loadMessages()
        autoScrollToBottom()
      },
      (error) => {
        console.error('发送消息失败:', error)
        ElMessage.error('发送消息失败')
        // 失败时移除临时添加的消息
        messages.value = messages.value.filter(m => m.id !== tempUserMessage.id && m.id !== tempAiMessage.id)
        inputMessage.value = tempInput
      }
    )
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败')
    // 失败时移除临时添加的消息
    messages.value = messages.value.filter(m => m.id !== tempUserMessage.id && m.id !== tempAiMessage.id)
    inputMessage.value = tempInput
  } finally {
    isLoading.value = false
  }
}

// 加载消息
const loadMessages = async () => {
  if (activeSession.value) {
    try {
      const data = await chatApi.getMessages(activeSession.value.id)
      messages.value = data
      highlightAllCodeBlocks()
    } catch (error) {
      console.error('加载消息失败:', error)
    }
  }
}

// 滚动到顶部
const scrollToTop = () => {
  nextTick(() => {
    if (chatContentRef.value) {
      chatContentRef.value.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    }
  })
}

// 滚动到底部（强制滚动，用于按钮点击）
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContentRef.value) {
      userScrolled.value = false
      chatContentRef.value.scrollTo({
        top: chatContentRef.value.scrollHeight,
        behavior: 'smooth'
      })
    }
  })
}

// 自动滚动到底部（用于流式输出）
const autoScrollToBottom = () => {
  nextTick(() => {
    if (chatContentRef.value && !userScrolled.value) {
      chatContentRef.value.scrollTo({
        top: chatContentRef.value.scrollHeight,
        behavior: 'smooth'
      })
    }
  })
}

// 处理内容滚动
const handleContentScroll = () => {
  if (chatContentRef.value) {
    const { scrollTop, scrollHeight, clientHeight } = chatContentRef.value
    const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10
    
    if (!isAtBottom) {
      userScrolled.value = true
    } else {
      userScrolled.value = false
    }
  }
}

// 监听输入变化，计算token数
watch(inputMessage, (newValue) => {
  // 这里简化处理，实际应该使用tokenizer计算
  inputTokenCount.value = newValue.length
})

// 监听消息变化，触发代码高亮
watch(messages, () => {
  highlightAllCodeBlocks()
}, { deep: true })

// 生命周期钩子
onMounted(() => {
  // 初始化Mermaid配置
  mermaid.initialize({
    startOnLoad: true,
    theme: 'default'
  })
  loadSessions()
})

// 监听路由参数变化，当sessionId变化时切换会话
watch(
  () => route.query.sessionId,
  (newSessionId) => {
    if (newSessionId && sessions.value.length > 0) {
      const targetSession = sessions.value.find(s => s.id === Number(newSessionId))
      if (targetSession) {
        selectSession(targetSession)
      }
    }
  }
)
</script>

<style scoped>
.chat-page {
  padding: 0;
  margin: 0 -20px;
  width: calc(100% + 40px);
}

.chat-page h1 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 30px;
  padding: 0 20px;
}

.chat-container {
  display: grid;
  grid-template-columns: minmax(280px, 350px) 1fr;
  gap: 20px;
  min-height: 700px;
  max-width: 1600px;
  padding: 0 20px 0 0;
  margin: 0 auto;
}

/* 会话列表 */
.chat-sessions {
  background-color: #fafafa;
  border-radius: 0;
  box-shadow: none;
  border-right: 1px solid #e4e7ed;
  padding: 20px;
  height: fit-content;
  position: sticky;
  top: 20px;
}

.sessions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.sessions-header h2 {
  font-size: 1.2rem;
  color: #303133;
}

.session-search {
  margin-bottom: 20px;
}

.sessions-list {
  max-height: 500px;
  overflow-y: auto;
}

/* 直接给 el-list-item 添加高亮样式 */
.session-item {
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
  border-radius: 8px;
}

.session-item :deep(.el-list-item__content) {
  padding: 0 !important;
}

.session-info {
  padding: 12px 16px;
  border-radius: 8px;
  border: 2px solid transparent;
}

.session-item:hover .session-info {
  background-color: #f5f7fa;
}

.session-item.active .session-info {
  background-color: #ecf5ff;
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.3);
}

.session-info h3 {
  font-size: 1rem;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.session-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: #606266;
}

.model-tag {
  padding: 2px 8px;
  background-color: #ecf5ff;
  color: #409eff;
  border-radius: 10px;
}

/* 聊天主界面 */
.chat-main {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 700px;
  position: relative;
}

/* 聊天头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-title h2 {
  font-size: 1.5rem;
  color: #303133;
}

.chat-settings {
  display: flex;
  align-items: center;
  gap: 20px;
}

.context-status {
  min-width: 200px;
}

.status-text {
  font-size: 0.8rem;
  color: #606266;
  display: block;
  margin-bottom: 5px;
}

/* 聊天内容 */
.chat-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #fafafa;
  position: relative;
}

.floating-buttons {
  position: absolute;
  right: 30px;
  bottom: 170px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 10;
}

.floating-btn {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  width: 40px !important;
  height: 40px !important;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.floating-buttons .el-button + .el-button {
  margin-left: 0 !important;
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

.message-header .token-count {
  margin-left: auto;
  color: #909399;
}

.message-content {
  line-height: 1.6;
  color: #303133;
}

.markdown-body :deep(pre) {
  margin-top: 0;
  margin-bottom: 10px;
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 6px;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6) {
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body :deep(h1) {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body :deep(h3) {
  font-size: 1.25em;
}

.markdown-body :deep(h4) {
  font-size: 1em;
}

.markdown-body :deep(p) {
  margin-top: 0;
  margin-bottom: 10px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin-top: 0;
  margin-bottom: 10px;
  padding-left: 2em;
}

.markdown-body :deep(li) {
  margin-bottom: 4px;
}

.markdown-body :deep(code) {
  background-color: #f6f8fa;
  border-radius: 3px;
  font-size: 85%;
  padding: 0.2em 0.4em;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

.markdown-body :deep(pre) {
  margin-top: 0;
  margin-bottom: 10px;
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 6px;
}

.markdown-body :deep(pre code) {
  padding: 0;
  background-color: transparent;
  border: 0;
}

.markdown-body :deep(.hljs) {
  background: transparent;
  padding: 0;
}

.markdown-body :deep(blockquote) {
  margin: 0;
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
}

.markdown-body :deep(table) {
  border-spacing: 0;
  border-collapse: collapse;
  margin-top: 0;
  margin-bottom: 10px;
  width: 100%;
}

.markdown-body :deep(table th),
.markdown-body :deep(table td) {
  padding: 6px 13px;
  border: 1px solid #dfe2e5;
}

.markdown-body :deep(table tr) {
  background-color: #fff;
  border-top: 1px solid #c6cbd1;
}

.markdown-body :deep(table tr:nth-child(2n)) {
  background-color: #f6f8fa;
}

.markdown-body :deep(a) {
  color: #0366d6;
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(hr) {
  height: 0.25em;
  padding: 0;
  margin: 24px 0;
  background-color: #e1e4e8;
  border: 0;
}

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

/* 输入区域 */
.chat-input-area {
  padding: 20px;
  border-top: 1px solid #ebeef5;
  background-color: white;
}

.chat-input-area textarea {
  resize: none;
  margin-bottom: 0;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.input-info {
  margin-right: auto;
  font-size: 0.8rem;
  color: #909399;
}

/* 空状态 */
.empty-card,
.no-session-selected {
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content,
.no-session-content {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon,
.no-session-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.empty-content p,
.no-session-content p {
  color: #909399;
}

.no-session-selected {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .chat-container {
    grid-template-columns: 250px 1fr;
    gap: 20px;
  }
  
  .message-item {
    max-width: 90%;
  }
}

@media (max-width: 768px) {
  .chat-page h1 {
    font-size: 1.5rem;
  }
  
  .chat-container {
    grid-template-columns: 1fr;
    gap: 20px;
    min-height: 600px;
  }
  
  .chat-sessions {
    position: static;
    height: auto;
  }
  
  .sessions-list {
    max-height: 200px;
  }
  
  .chat-main {
    height: 500px;
  }
  
  .chat-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 15px;
  }
  
  .chat-settings {
    width: 100%;
    justify-content: space-between;
  }
  
  .message-item {
    max-width: 100%;
  }
  
  .chat-content {
    padding: 15px;
  }
  
  .chat-input-area {
    padding: 15px;
  }
}
</style>
