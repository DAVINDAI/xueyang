<template>
  <div class="communication-page">
    <h1>沟通助手</h1>
    
    <div class="message-input-section">
      <h2>发送消息</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="receiverId">接收者</label>
          <div class="checkbox-group">
            <label v-for="user in userList" :key="user.username" class="checkbox-label">
              <input 
                type="checkbox" 
                :value="user.username" 
                v-model="formData.receiverId"
                @change="watchReceiverId"
              >
              {{ user.username }} ({{ user.role }})
            </label>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group half">
            <label for="originalContent">原始消息</label>
            <textarea id="originalContent" v-model="formData.originalContent" rows="4" required></textarea>
          </div>
          
          <div class="form-group half">
            <label>润色后的消息</label>
            <textarea v-model="formData.polishedContent" rows="4" readonly></textarea>
          </div>
        </div>
        
        <div class="button-group">
          <button type="button" class="btn btn-primary" @click="polishMessage" :disabled="isPolishing">
            {{ isPolishing ? '润色中...' : '润色消息' }}
          </button>
          <button type="submit" class="btn btn-success" :disabled="!formData.polishedContent || isSending">
            {{ isSending ? '发送中...' : '发送消息' }}
          </button>
        </div>
      </form>
    </div>
    
    <!-- 发送者信息 -->
    <div class="user-info-section">
      <h2>发送者信息</h2>
      <div class="user-info-card">
        <div class="user-info-item inline">
          <div>
            <label>ID:</label>
            <span>{{ formData.senderId }}</span>
          </div>
          <div>
            <label>角色:</label>
            <span>{{ formData.senderRole }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 消息列表区域 -->
    <div class="message-list-section">
      <h2>消息历史</h2>
      <div class="filter-section">
        <input type="text" v-model="filter.userId" placeholder="用户ID">
        <select v-model="filter.role">
          <option value="">所有角色</option>
          <option value="sender">发送者</option>
          <option value="receiver">接收者</option>
        </select>
        <button class="btn btn-info" @click="loadMessages">刷新</button>
      </div>
      
      <div class="message-list">
        <div v-for="message in messages" :key="message.id" class="message-item" @click="viewMessageDetail(message.id)">
          <div class="message-header">
            <span class="sender">{{ message.senderId }}</span>
            <span class="arrow">→</span>
            <span class="receiver">{{ message.receiverId }}</span>
            <span class="status" :class="message.status">{{ message.status }}</span>
          </div>
          <div class="message-content">
            <p class="original">{{ message.originalContent }}</p>
            <p class="polished">{{ message.polishedContent }}</p>
          </div>
          <div class="message-meta">
            <span class="roles">{{ message.senderRole }} → {{ message.receiverRole }}</span>
            <span class="time">{{ message.createdAt }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 消息详情模态框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>消息详情</h3>
          <button class="close-btn" @click="closeDetailModal">&times;</button>
        </div>
        <div class="modal-body" v-if="selectedMessage">
          <div class="message-info">
            <p><strong>发送者:</strong> {{ selectedMessage.senderId }} ({{ selectedMessage.senderRole }})</p>
            <p><strong>接收者:</strong> {{ selectedMessage.receiverId }} ({{ selectedMessage.receiverRole }})</p>
            <p><strong>状态:</strong> {{ selectedMessage.status }}</p>
            <p><strong>时间:</strong> {{ selectedMessage.createdAt }}</p>
          </div>
          
          <div class="message-content">
            <h4>原始消息</h4>
            <p>{{ selectedMessage.originalContent }}</p>
            <h4>润色后的消息</h4>
            <div class="polished-message-box" :class="{ 'has-content': selectedMessage.polishedContent && selectedMessage.polishedContent.trim() }">
              <template v-if="selectedMessage.polishedContent && selectedMessage.polishedContent.trim()">
                <p>{{ selectedMessage.polishedContent }}</p>
              </template>
              <template v-else>
                <div class="empty-polished">
                  <span class="ai-icon">✨</span>
                  <p>系统将根据您的角色和场景自动润色此消息</p>
                  <p class="hint">发送消息后，润色版本将显示在这里</p>
                </div>
              </template>
            </div>
          </div>
          
          <div class="suggestions-section" v-if="selectedMessage.replySuggestions.length > 0">
            <h4>回复建议</h4>
            <ul>
              <li v-for="(suggestion, index) in selectedMessage.replySuggestions" :key="index">
                {{ suggestion.content }}
                <button class="btn btn-sm btn-primary" @click="useReplySuggestion(suggestion.content)">使用</button>
              </li>
            </ul>
          </div>
          
          <div class="suggestions-section" v-if="selectedMessage.actionSuggestions.length > 0">
            <h4>行动建议</h4>
            <ul>
              <li v-for="(suggestion, index) in selectedMessage.actionSuggestions" :key="index">
                {{ suggestion.content }}
              </li>
            </ul>
          </div>
          
          <div class="suggestions-section" v-if="!selectedMessage.replySuggestions.length">
            <button class="btn btn-primary" @click="generateSuggestions" :disabled="isGeneratingSuggestions">
              {{ isGeneratingSuggestions ? '生成中...' : '生成回复建议' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { communicationApi } from '../api'
import { authApi } from '../api/authApi'

export default {
  name: 'CommunicationPage',
  setup() {
    const currentUser = ref(null)
    const userList = ref([])
    const formData = ref({
      senderId: '',
      receiverId: [], // 改为数组以支持多选
      originalContent: '',
      polishedContent: '',
      senderRole: '',
      receiverRole: '',
      modelName: 'qwen-plus'
    })
    
    const customSenderRole = ref('')
    const customReceiverRole = ref('')
    const isPolishing = ref(false)
    const isSending = ref(false)
    const isGeneratingSuggestions = ref(false)
    
    // 监听接收者ID变化，自动填充接收者角色
    const watchReceiverId = () => {
      // 当选择多个接收者时，我们可以根据第一个选中的用户来设置接收者角色
      // 或者可以考虑如果选择了多个不同角色的用户，可能需要设置通用角色
      if (formData.value.receiverId.length > 0) {
        const firstSelectedUser = userList.value.find(user => user.username === formData.value.receiverId[0])
        if (firstSelectedUser) {
          formData.value.receiverRole = firstSelectedUser.role
        }
      } else {
        // 如果没有选择任何接收者，清空接收者角色
        formData.value.receiverRole = ''
      }
    }
    
    // 加载当前用户信息
    const loadCurrentUser = async () => {
      try {
        const response = await authApi.getCurrentUser()
        currentUser.value = response
        formData.value.senderId = response.username
        formData.value.senderRole = response.role
      } catch (error) {
        console.error('获取当前用户信息失败:', error)
        // 如果获取用户信息失败，显示默认值
        currentUser.value = {
          username: 'guest',
          role: '用户'
        }
        formData.value.senderId = currentUser.value.username
        formData.value.senderRole = currentUser.value.role
      }
    }
    
    // 加载用户列表
    const loadUsers = async () => {
      try {
        console.log('开始加载用户列表...')
        const result = await communicationApi.getUsers()
        console.log('API返回结果:', result)
        console.log('数据类型:', typeof result, Array.isArray(result))
        
        // 根据拦截器处理后的数据结构进行处理
        // 拦截器会返回转换后的数据
        if (result) {
          // 确保 result 是数组
          if (Array.isArray(result)) {
            userList.value = result
            console.log('设置为数组，长度:', result.length)
          } else if (result.data && Array.isArray(result.data)) {
            userList.value = result.data
            console.log('从 result.data 设置，长度:', result.data.length)
          } else {
            console.warn('数据结构不符合预期:', result)
            userList.value = []
          }
        } else {
          console.warn('API返回空数据')
          userList.value = []
        }
        
        console.log('userList 最终值:', userList.value)
      } catch (error) {
        console.error('加载用户列表失败:', error)
      }
    }
    
    const messages = ref([])
    const filter = ref({
      userId: '',
      role: ''
    })
    
    const showDetailModal = ref(false)
    const selectedMessage = ref(null)
    
    const roles = ref([])
    
    // 加载角色列表
    const loadRoles = async () => {
      try {
        const response = await communicationApi.getRoles()
        roles.value = response.data
      } catch (error) {
        console.error('加载角色列表失败:', error)
        // 降级处理：如果接口请求失败，使用默认角色列表
        roles.value = [
          { roleName: '总裁', description: '公司最高领导者，负责公司战略决策和整体管理' },
          { roleName: '市场', description: '负责公司市场推广、品牌建设和客户关系管理' },
          { roleName: '运营', description: '负责公司日常运营管理和流程优化' },
          { roleName: '研发', description: '负责公司产品研发、技术创新和系统维护' },
          { roleName: '财务', description: '负责公司财务管理、预算控制和财务报表' },
          { roleName: '用户', description: '系统普通用户，使用各种功能和服务' }
        ]
      }
    }
    
    // 加载消息列表
    const loadMessages = async () => {
      try {
        const response = await communicationApi.getMessages(filter.value.userId, filter.value.role)
        messages.value = response.data
        console.log('Messages loaded:', messages.value)
        if (messages.value && messages.value.length > 0) {
          console.log('First message:', messages.value[0])
          console.log('First message polishedContent:', messages.value[0].polishedContent)
        }
      } catch (error) {
        console.error('加载消息失败:', error)
      }
    }
    
    // 润色消息
    const polishMessage = async () => {
      try {
        isPolishing.value = true
        
        const senderRole = formData.value.senderRole === '自定义' ? customSenderRole.value : formData.value.senderRole
        const receiverRole = formData.value.receiverRole === '自定义' ? customReceiverRole.value : formData.value.receiverRole
        
        const response = await communicationApi.polishMessage(
          formData.value.senderId,
          formData.value.receiverId,
          formData.value.originalContent,
          senderRole,
          receiverRole,
          formData.value.modelName
        )
        
        formData.value.polishedContent = response.data.polishedContent
      } catch (error) {
        console.error('润色消息失败:', error)
      } finally {
        isPolishing.value = false
      }
    }
    
    // 发送消息
    const handleSubmit = async () => {
      try {
        isSending.value = true
        
        const senderRole = formData.value.senderRole === '自定义' ? customSenderRole.value : formData.value.senderRole
        const receiverRole = formData.value.receiverRole === '自定义' ? customReceiverRole.value : formData.value.receiverRole
        
        // 向每个选中的接收者发送消息
        for (const receiverId of formData.value.receiverId) {
          await communicationApi.sendMessage(
            formData.value.senderId,
            receiverId,
            formData.value.originalContent,
            formData.value.polishedContent,
            senderRole,
            receiverRole
          )
        }
        
        // 重置表单
        formData.value = {
          senderId: formData.value.senderId,
          receiverId: [], // 重置为为空数组
          originalContent: '',
          polishedContent: '',
          senderRole: formData.value.senderRole,
          receiverRole: formData.value.receiverRole,
          modelName: formData.value.modelName
        }
        
        // 重新加载消息列表
        await loadMessages()
      } catch (error) {
        console.error('发送消息失败:', error)
      } finally {
        isSending.value = false
      }
    }
    
    // 查看消息详情
    const viewMessageDetail = async (messageId) => {
      try {
        const response = await communicationApi.getMessage(messageId)
        selectedMessage.value = response.data
        console.log('Selected message:', selectedMessage.value)
        console.log('Has polishedContent:', selectedMessage.value.polishedContent)
        console.log('polishedContent type:', typeof selectedMessage.value.polishedContent)
        console.log('polishedContent length:', selectedMessage.value.polishedContent?.length)
        showDetailModal.value = true
      } catch (error) {
        console.error('获取消息详情失败:', error)
      }
    }
    
    // 关闭详情模态框
    const closeDetailModal = () => {
      showDetailModal.value = false
      selectedMessage.value = null
    }
    
    // 生成回复建议
    const generateSuggestions = async () => {
      try {
        isGeneratingSuggestions.value = true
        
        const response = await communicationApi.getSuggestions(
          selectedMessage.value.id,
          selectedMessage.value.receiverRole,
          formData.value.modelName
        )
        
        // 重新获取消息详情，包含新生成的建议
        await viewMessageDetail(selectedMessage.value.id)
      } catch (error) {
        console.error('生成回复建议失败:', error)
      } finally {
        isGeneratingSuggestions.value = false
      }
    }
    
    // 使用回复建议
    const useReplySuggestion = (content) => {
      // 将建议内容填充到原始消息输入框
      formData.value.originalContent = content
      formData.value.polishedContent = ''
      closeDetailModal()
    }
    
    // 初始化
    onMounted(async () => {
      await loadCurrentUser()
      await loadUsers()
      await loadRoles()
      await loadMessages()
    })
    
    return {
      formData,
      userList,
      customSenderRole,
      customReceiverRole,
      isPolishing,
      isSending,
      isGeneratingSuggestions,
      messages,
      filter,
      showDetailModal,
      selectedMessage,
      roles,
      loadUsers,
      loadMessages,
      watchReceiverId,
      polishMessage,
      handleSubmit,
      viewMessageDetail,
      closeDetailModal,
      generateSuggestions,
      useReplySuggestion
    }
  }
}
</script>

<style scoped>
.communication-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.user-info-section {
  background: linear-gradient(135deg, #e6f7ff 0%, #e8f5e8 100%);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05), 
              0 1px 2px rgba(0, 0, 0, 0.04),
              inset 0 1px 0 rgba(255, 255, 255, 0.3);
  margin-top: 40px;
}

.user-info-card {
  display: flex;
  justify-content: center;
}

.user-info-item.inline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.user-info-item.inline > div {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 10px;
}

.user-info-item.inline label {
  margin-right: 8px;
  font-weight: 600;
  color: #2c5f4e;
}

.user-info-item.inline span {
  color: #333;
}

.user-info-section h2 {
  color: #2c5f4e;
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 22px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.user-info-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.user-info-item.inline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.user-info-item.inline > div {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 0 10px;
}

.user-info-item.inline > div:first-child {
  border-right: 1px solid rgba(44, 95, 78, 0.2);
}

.user-info-item.inline label {
  margin-right: 8px;
  font-weight: 600;
  color: #2c5f4e;
  min-width: 40px;
}

.user-info-item.inline span {
  color: #333;
  flex: 1;
}

.user-info-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.user-info-item.inline {
  display: flex;
  justify-content: center;
  gap: 20px;
  background: none;
  padding: 0;
  margin-bottom: 0;
}

.user-info-item.inline label {
  margin-right: 5px;
  width: auto;
}

.user-info-item.inline > div:first-child label {
  margin-left: 0;
}

.user-info-item.inline > div:last-child label {
  margin-left: 10px;
}

.user-info-item.inline span {
  flex: 1;
  width: auto;
}

.user-info-item.inline > div {
  display: flex;
  align-items: center;
  flex: 1;
  padding: 0 10px;
}

.user-info-item.inline > div:first-child {
  border-right: 1px solid rgba(255, 255, 255, 0.5);
}

.user-info-item.inline > div:last-child {
  justify-content: flex-end;
}

.user-info-item:last-child {
  margin-bottom: 0;
}

.user-info-item:hover {
  background: rgba(255, 255, 255, 0.9);
}

.user-info-item label {
  font-weight: 600;
  margin-right: 10px;
  width: 80px;
  color: #667eea;
  font-size: 14px;
}

.user-info-item span {
  flex: 1;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  color: #333;
  font-weight: 500;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-input-section,
.message-list-section {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.message-list-section {
  background: linear-gradient(135deg, #e6f7ff 0%, #e8f5e8 100%);
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05), 
              0 1px 2px rgba(0, 0, 0, 0.04),
              inset 0 1px 0 rgba(255, 255, 255, 0.3);
  color: #2c5f4e;
}

.message-list-section h2 {
  color: #2c5f4e;
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message-list-section .filter-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 15px;
  align-items: center;
}

.message-list-section .filter-section input,
.message-list-section .filter-section select {
  flex: 1;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 6px;
  background: white;
  color: #2c5f4e;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-list-section .filter-section input:focus,
.message-list-section .filter-section select:focus {
  outline: none;
  border-color: #2c5f4e;
  box-shadow: 0 0 0 3px rgba(44, 95, 78, 0.2), 
              inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-list-section .btn-info {
  background: linear-gradient(135deg, #b3e5fc 0%, #c8e6c9 100%);
  border: 1px solid rgba(44, 95, 78, 0.3);
  color: #2c5f4e;
  font-weight: 600;
  border-radius: 6px;
  padding: 10px 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.message-list-section .btn-info:hover {
  background: linear-gradient(135deg, #81d4fa 0%, #a5d6a7 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.message-input-section {
  background: linear-gradient(135deg, #e6f7ff 0%, #e8f5e8 100%);
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05), 
              0 1px 2px rgba(0, 0, 0, 0.04),
              inset 0 1px 0 rgba(255, 255, 255, 0.3);
  color: #2c5f4e;
}

.message-input-section h2 {
  color: #2c5f4e;
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message-input-section .form-group label {
  color: #2c5f4e;
  font-weight: 500;
  font-size: 15px;
  margin-bottom: 8px;
}

.message-input-section .form-group input,
.message-input-section .form-group select,
.message-input-section .form-group textarea {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: #333;
  border-radius: 6px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-input-section .form-group input:focus,
.message-input-section .form-group select:focus,
.message-input-section .form-group textarea:focus {
  outline: none;
  border-color: white;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3), 
              inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-input-section .checkbox-group {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 15px;
  backdrop-filter: blur(10px);
}

.message-input-section .checkbox-label {
  background: rgba(255, 255, 255, 0.9);
  color: #2c5f4e;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  font-weight: 500;
}

.message-input-section .checkbox-label:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.message-input-section .checkbox-label input[type="checkbox"] {
  accent-color: #667eea;
}

.message-input-section .btn {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.message-input-section .btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25);
}

.message-input-section .btn-primary {
  background: linear-gradient(135deg, #b3e5fc 0%, #c8e6c9 100%);
  border: 1px solid rgba(44, 95, 78, 0.3);
  color: #2c5f4e;
  font-weight: 600;
}

.message-input-section .btn-success {
  background: linear-gradient(135deg, #81d4fa 0%, #a5d6a7 100%);
  border: 1px solid rgba(44, 95, 78, 0.3);
  color: #2c5f4e;
  font-weight: 600;
}

.form-group {
  margin-bottom: 15px;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.form-group.half {
  flex: 1;
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

/* 复选框组样式 */
.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.checkbox-label:hover {
  background: #e9ecef;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
  transform: scale(1.2);
  cursor: pointer;
}

.form-group textarea {
  resize: vertical;
}

.button-group {
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 10px;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-info {
  background-color: #17a2b8;
  color: white;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.filter-section {
  margin-bottom: 15px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-section input,
.filter-section select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.message-list {
  max-height: 400px;
  overflow-y: auto;
}

.message-item {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 1);
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
}

.sender {
  color: #007bff;
}

.arrow {
  margin: 0 10px;
  color: #666;
}

.receiver {
  color: #28a745;
}

.status {
  margin-left: auto;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: normal;
}

.status.pending {
  background-color: #ffc107;
  color: #212529;
}

.status.sent {
  background-color: #28a745;
  color: white;
}

.status.delivered {
  background-color: #007bff;
  color: white;
}

.message-content {
  margin-bottom: 10px;
}

.original {
  margin-bottom: 5px;
  color: #666;
  font-style: italic;
}

.polished {
  margin: 0;
  color: #333;
}

.message-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ddd;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  line-height: 1.6;
}

.message-info {
  margin-bottom: 20px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.suggestions-section {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #ddd;
}

.suggestions-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.suggestions-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestions-section li {
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.suggestions-section li button {
  margin-left: 10px;
}

.polished-message-box {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border: 2px dashed #a0a0a0;
  border-radius: 8px;
  padding: 20px;
  margin: 15px 0;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.polished-message-box.has-content {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  border: 2px solid #4caf50;
  flex-direction: column;
  align-items: stretch;
}

.polished-message-box.has-content p {
  margin: 0;
  color: #2e7d32;
  font-size: 15px;
  line-height: 1.6;
}

.empty-polished {
  text-align: center;
  color: #666;
}

.empty-polished .ai-icon {
  font-size: 36px;
  display: block;
  margin-bottom: 10px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.empty-polished p {
  margin: 5px 0;
  font-size: 14px;
}

.empty-polished .hint {
  color: #888;
  font-size: 12px;
  font-style: italic;
}

.modal-body h4 {
  color: #667eea;
  margin-top: 20px;
  margin-bottom: 10px;
  font-size: 16px;
  font-weight: 600;
}

.modal-body h4:first-of-type {
  margin-top: 0;
}

.modal-body p {
  background: #f9f9f9;
  padding: 12px;
  border-radius: 6px;
  margin: 8px 0;
  line-height: 1.6;
  color: #333;
}

.modal-body .message-info p {
  margin: 8px 0;
  background: #f0f4f8;
  border-left: 3px solid #667eea;
  padding-left: 12px;
}
</style>
