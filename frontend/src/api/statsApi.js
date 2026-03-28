import api from './api'

export const statsApi = {
  getStats: () => api.get('/stats'),
  getModelStats: () => api.get('/stats/models'),
  getDailyStats: () => api.get('/stats/daily')
}