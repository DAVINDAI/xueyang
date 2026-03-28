import api from './api'

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
  },
  
  /**
   * 获取所有优化结果
   * @returns {Promise} - 返回优化结果列表
   */
  getOptimizations: () => {
    return api.get('/resume/optimizations')
  },
  
  /**
   * 获取单个优化结果
   * @param {number} optimizationId - 优化结果ID
   * @returns {Promise} - 返回优化结果
   */
  getOptimization: (optimizationId) => {
    return api.get(`/resume/optimizations/${optimizationId}`)
  },
  
  /**
   * 删除优化结果
   * @param {number} optimizationId - 优化结果ID
   * @returns {Promise} - 返回删除结果
   */
  deleteOptimization: (optimizationId) => {
    return api.delete(`/resume/optimizations/${optimizationId}`)
  }
}

export default resumeApi
