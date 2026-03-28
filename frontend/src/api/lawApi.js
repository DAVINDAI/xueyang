import api, { getVisitorId } from './api'

export const lawApi = {
  // 获取已下载的法律文档列表
  getAvailableLawDocs: async () => {
    try {
      const response = await api.get('/law/documents')
      return response
    } catch (error) {
      console.error('获取法律文档列表失败:', error)
      throw error
    }
  },

  // 下载法律文档
  downloadLawDoc: (filename) => {
    // 直接通过浏览器下载
    const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
    window.open(`${baseURL}/law/download?filename=${encodeURIComponent(filename)}`, '_blank')
  },

  // 下载法律PDF文档
  downloadLawPdf: async (lawUrl) => {
    try {
      const response = await api.get('/law/download', {
        params: { law_url: lawUrl }
      })
      return response
    } catch (error) {
      console.error('下载法律文档失败:', error)
      throw error
    }
  },

  // 清理法律文档存储目录
  cleanupLawDocs: async () => {
    try {
      const response = await api.get('/law/cleanup')
      return response
    } catch (error) {
      console.error('清理法律文档失败:', error)
      throw error
    }
  }
}
