import api from './api'

export const detailsApi = {
  getAllDetails: () => api.get('/details'),
  getSessionDetails: (sessionId) => api.get(`/details/session/${sessionId}`),
  getSessionsList: () => api.get('/details/sessions')
}