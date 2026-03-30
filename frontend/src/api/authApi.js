import api, { getVisitorId } from './api'

export const authApi = {
  /**
   * 登录
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @returns {Promise}
   */
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password })
    // 存储token到localStorage（响应拦截器已经将下划线转换为驼峰）
    if (response.accessToken) {
      localStorage.setItem('token', response.accessToken)
      // 登录成功后清除访客ID
      localStorage.removeItem('visitorId')
    }
    return response
  },

  /**
   * 注销
   */
  logout: () => {
    localStorage.removeItem('token')
    // 登出后重新生成访客ID
    localStorage.removeItem('visitorId')
    // 生成新的访客ID
    const generateVisitorId = () => {
      return 'visitor_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now()
    }
    localStorage.setItem('visitorId', generateVisitorId())
  },

  /**
   * 获取当前登录状态
   * @returns {boolean}
   */
  isLoggedIn: () => {
    return !!localStorage.getItem('token')
  },

  /**
   * 获取当前用户信息
   * @returns {Promise}
   */
  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response
  }
}