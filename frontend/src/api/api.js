import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 生成唯一访客ID
const generateVisitorId = () => {
  return 'visitor_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now()
}

// 获取或创建访客ID
const getVisitorId = () => {
  let visitorId = localStorage.getItem('visitorId')
  if (!visitorId) {
    visitorId = generateVisitorId()
    localStorage.setItem('visitorId', visitorId)
  }
  return visitorId
}

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

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 转换请求数据的驼峰为下划线（FormData对象不转换）
    if (config.data && typeof config.data === 'object' && !(config.data instanceof FormData)) {
      config.data = convertObjectKeys(config.data, camelToSnake)
    }
    
    // 添加Authorization头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      // 登录状态下不添加访客ID
    } else {
      // 未登录状态下添加访客ID头
      const visitorId = getVisitorId()
      config.headers['X-Visitor-ID'] = visitorId
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
    
    // 确保错误对象包含后端返回的消息
    if (error.response && error.response.data && error.response.data.message) {
      error.message = error.response.data.message
    }
    
    return Promise.reject(error)
  }
)

// 导出工具函数
export { getVisitorId, convertObjectKeys, snakeToCamel, camelToSnake }

export default api