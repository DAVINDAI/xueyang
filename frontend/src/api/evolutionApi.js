import api from './api'

export const evolutionApi = {
  evolve: () => api.post('/evolution')
}