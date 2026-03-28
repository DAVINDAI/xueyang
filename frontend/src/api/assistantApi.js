import api from './api'

export const assistantApi = {
  // 创建目标
  createGoal: (goalData) => api.post('/assistant/goals', goalData),

  // 获取目标列表
  getGoals: () => api.get('/assistant/goals'),

  // 分解目标
  decomposeGoal: (goalId) => api.post(`/assistant/goals/${goalId}/decompose`),

  // 获取任务列表
  getTasks: (params = {}) => api.get('/assistant/tasks', { params }),

  // 更新任务状态
  updateTaskStatus: (taskId, status) => api.put(`/assistant/tasks/${taskId}/status`, { status }),

  // 获取用户列表
  getUsers: () => api.get('/assistant/users')
}