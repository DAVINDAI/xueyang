import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 300000,
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 统一错误处理
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 简历优化API
export const resumeApi = {
  /**
   * 优化简历
   * @param {FormData} formData - 包含简历文件和职位描述的FormData
   * @returns {Promise} - 返回优化结果
   */
  optimizeResume: (formData) => {
    return api.post('/resume/optimize', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  /**
   * 下载优化后的简历
   * @param {string} resumeId - 简历ID
   * @returns {Promise} - 返回文件流
   */
  downloadResume: (resumeId) => {
    return api.get(`/resume/download/${resumeId}`, {
      responseType: 'blob'
    })
  }
}

export default resumeApi
