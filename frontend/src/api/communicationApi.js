import api, { convertObjectKeys, snakeToCamel } from './api'

export const communicationApi = {
  // 获取用户列表
  getUsers: () => 
    api.get('/communication/users'),
  
  // 消息润色
  polishMessage: (senderId, receiverId, originalContent, senderRole, receiverRole, modelName) => 
    api.post('/communication/polish', {
      senderId,
      receiverId,
      originalContent,
      senderRole,
      receiverRole,
      modelName
    }),
  
  // 发送消息
  sendMessage: (senderId, receiverId, originalContent, polishedContent, senderRole, receiverRole) => 
    api.post('/communication/messages', {
      senderId,
      receiverId,
      originalContent,
      polishedContent,
      senderRole,
      receiverRole
    }),
  
  // 获取消息列表
  getMessages: (userId, role, limit = 20, offset = 0) => 
    api.get('/communication/messages', {
      params: {
        userId,
        role,
        limit,
        offset
      }
    }),
  
  // 获取消息详情
  getMessage: (messageId) => 
    api.get(`/communication/messages/${messageId}`),
  
  // 删除消息
  deleteMessage: (messageId) => 
    api.delete(`/communication/messages/${messageId}`),
  
  // 获取回复建议
  getSuggestions: (messageId, receiverRole, modelName) => 
    api.post('/communication/suggestions', {
      messageId,
      receiverRole,
      modelName
    }),
  
  // 角色管理
  createRole: (roleName, description) => 
    api.post('/communication/roles', {
      roleName,
      description
    }),
  
  getRoles: () => 
    api.get('/communication/roles'),
  
  getRole: (roleName) => 
    api.get(`/communication/roles/${roleName}`),
  
  updateRole: (roleName, description) => 
    api.put(`/communication/roles/${roleName}`, {
      description
    }),
  
  deleteRole: (roleName) => 
    api.delete(`/communication/roles/${roleName}`)
}
