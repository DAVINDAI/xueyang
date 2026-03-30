import api from './api'

/**
 * 解析API - 用于解析用户输入并返回对应的路由
 */
export const parseApi = {
  /**
   * 解析用户输入内容
   * @param {string} inputText - 用户输入的内容
   * @returns {Promise} 包含解析结果的Promise
   */
  parseInput: async (inputText) => {
    try {
      const response = await api.post('/parse/parse-input', {
        inputText: inputText
      })
      return response
    } catch (error) {
      console.error('解析用户输入失败:', error)
      throw error
    }
  }
}
