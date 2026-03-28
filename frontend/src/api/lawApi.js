import axios from 'axios';

// 创建 axios 实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api', // 后端 API 地址
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

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

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 添加Authorization头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
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

// 获取已下载的法律文档列表
export const getAvailableLawDocs = async () => {
  try {
    const response = await api.get('/law/documents');
    return response;
  } catch (error) {
    console.error('获取法律文档列表失败:', error);
    throw error;
  }
};

// 下载法律文档
export const downloadLawDoc = (filename) => {
  // 直接通过浏览器下载
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api';
  window.open(`${baseURL}/law/download?filename=${encodeURIComponent(filename)}`, '_blank');
};

// 下载法律PDF文档
export const downloadLawPdf = async (lawUrl) => {
  try {
    const response = await api.get('/law/download', {
      params: { law_url: lawUrl }
    });
    return response;
  } catch (error) {
    console.error('下载法律文档失败:', error);
    throw error;
  }
};

// 清理法律文档存储目录
export const cleanupLawDocs = async () => {
  try {
    const response = await api.get('/law/cleanup');
    return response;
  } catch (error) {
    console.error('清理法律文档失败:', error);
    throw error;
  }
};
