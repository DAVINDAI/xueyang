import api, { getVisitorId } from './api'

const BASE = '/api/coding-playground'

export const codingPlaygroundApi = {
  getProblem: (difficulty) => api.get(`/coding-playground/problem?difficulty=${difficulty}`),
  submitCode: (problemId, code) => api.post('/coding-playground/submit', { problem_id: problemId, code }),
  getUserAnswers: (problemId) => api.get(`/coding-playground/answers/${problemId}`),
  hilStart: (problemId, code) => api.post('/coding-playground/hil/start', { problem_id: problemId, code }),
  hilResume: (threadId, approved) => api.post('/coding-playground/hil/resume', { thread_id: threadId, approved }),

  // ──────────── SSE 流式版（使用原生 fetch，不走 axios） ────────────

  /**
   * 流式启动 HIL 评估，返回 ReadableStream reader。
   * 调用方自行消费 SSE 事件：
   *   {type: "node", node: "...", executed: [...]}
   *   {type: "interrupt", thread_id, current_node, payload, executed_nodes}
   *   {type: "done", final_code, report, executed_nodes}
   */
  hilStartStream: (problemId, code) => {
    const token = localStorage.getItem('token')
    const headers = { 'Content-Type': 'application/json' }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    } else {
      headers['X-Visitor-ID'] = getVisitorId()
    }

    return fetch(`${BASE}/hil/start`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ problem_id: problemId, code, stream: true }),
    })
  },

  /**
   * 流式恢复 HIL 评估，返回 ReadableStream reader。
   */
  hilResumeStream: (threadId, approved) => {
    const token = localStorage.getItem('token')
    const headers = { 'Content-Type': 'application/json' }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    } else {
      headers['X-Visitor-ID'] = getVisitorId()
    }

    return fetch(`${BASE}/hil/resume`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ thread_id: threadId, approved, stream: true }),
    })
  },
}