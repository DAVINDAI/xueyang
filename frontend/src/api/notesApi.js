import api from './api'

export const notesApi = {
  createNote: (title, content) => api.post('/notes', { title, content }),
  listNotes: () => api.get('/notes'),
  getNote: (noteId) => api.get(`/notes/${noteId}`),
  updateNote: (noteId, title, content) => api.put(`/notes/${noteId}`, { title, content }),
  deleteNote: (noteId) => api.delete(`/notes/${noteId}`)
}