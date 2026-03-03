import axios from 'axios'

// 驼峰转下划线
const camelToSnake = (str) => {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
}

// 对象属性驼峰转下划线
const convertObjectKeys = (obj, converter) => {
  if (Array.isArray(obj)) {
    return obj.map(item => convertObjectKeys(item, converter))
  }
  if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      acc[converter(key)] = convertObjectKeys(obj[key], converter)
      return acc
    }, {})
  }
  return obj
}

// 下划线转驼峰
const snakeToCamel = (str) => {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
}

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 转换请求数据的驼峰为下划线
    if (config.data && typeof config.data === 'object') {
      config.data = convertObjectKeys(config.data, camelToSnake)
    }
    
    // 添加Authorization头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 转换响应数据的下划线为驼峰
    if (response.data && typeof response.data === 'object') {
      return convertObjectKeys(response.data, snakeToCamel)
    }
    return response.data
  },
  error => {
    // 统一错误处理
    console.error('API Error:', error)
    
    // 处理401错误（token过期或无效）
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      // 跳转到登录页面
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

// 统计信息API
export const statsApi = {
  getStats: () => api.get('/stats'),
  getModelStats: () => api.get('/stats/models'),
  getDailyStats: () => api.get('/stats/daily')
}

// 详情信息API
export const detailsApi = {
  getAllDetails: () => api.get('/details'),
  getSessionDetails: (sessionId) => api.get(`/details/session/${sessionId}`),
  getSessionsList: () => api.get('/details/sessions')
}

// 聊天API
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
      const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
      console.log('开始流式请求，模型:', modelName)
      
      // 获取token
      const token = localStorage.getItem('token')
      const headers = {
        'Content-Type': 'application/json'
      }
      
      // 添加Authorization头
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }
      
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

// 搜索API
export const searchApi = {
  search: (query) => api.post('/search', { query })
}

// 为了方便在组件中直接使用
api.search = (query) => api.post('/search', { query })

export default api
