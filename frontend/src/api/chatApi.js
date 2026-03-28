import api, { getVisitorId, convertObjectKeys, snakeToCamel } from './api'

export const chatApi = {
  // 会话管理
  createSession: (sessionName, modelName) => api.post('/chat/sessions', { sessionName, modelName }),
  listSessions: () => api.get('/chat/sessions'),
  getSession: (sessionId) => api.get(`/chat/sessions/${sessionId}`),
  updateSession: (sessionId, sessionName) => api.put(`/chat/sessions/${sessionId}`, { sessionName }),
  deleteSession: (sessionId) => api.delete(`/chat/sessions/${sessionId}`),
  
  // 消息管理
  getMessages: (sessionId) => api.get(`/chat/messages/${sessionId}`),
  deleteMessage: (messageId) => api.delete(`/chat/messages/${messageId}`),
  
  // 聊天功能
  chatCompletion: (sessionId, modelName, message) => api.post('/chat/completion', { sessionId, modelName, message }),
  
  // 流式聊天
  chatCompletionStream: async (sessionId, modelName, message, onChunk, onDone, onError) => {
    try {
      const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
      console.log('开始流式请求，模型:', modelName, 'baseURL:', baseURL)
      
      // 获取token和访客ID
      const token = localStorage.getItem('token')
      const visitorId = getVisitorId()
      const headers = {
        'Content-Type': 'application/json'
      }
      
      // 添加Authorization头
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }
      
      // 添加访客ID头
      headers['X-Visitor-ID'] = visitorId
      
      const response = await fetch(`${baseURL}/chat/completion/stream`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          session_id: sessionId,
          model_name: modelName,
          message: message
        })
      })
      
      if (!response.ok) {
        // 处理401错误（token过期或无效）
        if (response.status === 401) {
          localStorage.removeItem('token')
          window.location.href = '/login'
          return
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      console.log('响应开始')
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let firstChunkReceived = false
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          console.log('响应结束')
          break
        }
        
        const decodedValue = decoder.decode(value, { stream: true })
        console.log('收到数据:', decodedValue)
        buffer += decodedValue
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.trim().startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6).trim())
              console.log('解析后的数据:', data)
              
              if (data.type === 'chunk') {
                if (!firstChunkReceived) {
                  console.log('收到第一个 chunk，内容:', data.content)
                  firstChunkReceived = true
                }
                if (data.content) {
                  onChunk && onChunk(data.content)
                }
              } else if (data.type === 'done') {
                const camelData = convertObjectKeys(data, snakeToCamel)
                onDone && onDone(camelData)
              }
            } catch (e) {
              console.error('解析 SSE 数据失败:', e, 'line:', line)
            }
          }
        }
      }
    } catch (error) {
      console.error('流式请求错误:', error)
      onError && onError(error)
    }
  },
  
  // 配置信息
  getConfig: () => api.get('/chat/config'),
  
  // 备忘录功能
  createMemo: (sessionId, modelName) => api.post('/chat/memo', { sessionId, modelName }),
  listMemos: () => api.get('/chat/memos'),
  getMemo: (memoId) => api.get(`/chat/memos/${memoId}`),
  deleteMemo: (memoId) => api.delete(`/chat/memos/${memoId}`)
}