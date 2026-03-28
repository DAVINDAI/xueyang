import api from './api'

export const codingPlaygroundApi = {
  getProblem: (difficulty) => api.get(`/coding-playground/problem?difficulty=${difficulty}`),
  submitCode: (problemId, code) => api.post('/coding-playground/submit', { problem_id: problemId, code }),
  getUserAnswers: (problemId) => api.get(`/coding-playground/answers/${problemId}`)
}