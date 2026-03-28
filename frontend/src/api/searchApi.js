import api from './api'

export const searchApi = {
  search: (query) => api.post('/search', { query })
}

// 为了方便在组件中直接使用
api.search = (query) => api.post('/search', { query })