<template>
  <div class="coding-playground">
    <h1>编码操场</h1>
    
    <!-- 难度选择 -->
    <div class="difficulty-selector">
      <label>难度：</label>
      <select v-model="difficulty" @change="loadProblem">
        <option value="1">简单</option>
        <option value="2">中等</option>
        <option value="3">困难</option>
      </select>
      <button @click="loadProblem" class="refresh-btn">刷新题目</button>
    </div>
    
    <!-- 题目展示 -->
    <div v-if="problem" class="problem-container">
      <h2>{{ problem.title }}</h2>
      <div class="problem-description">
        <p>{{ problem.description }}</p>
      </div>
      
      <!-- 示例 -->
      <div class="examples">
        <h3>示例：</h3>
        <div v-for="(example, index) in problem.examples" :key="index" class="example-item">
          <div class="example-input">
            <strong>输入：</strong>{{ example.input }}
          </div>
          <div class="example-output">
            <strong>输出：</strong>{{ example.output }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 代码编辑器 -->
    <div class="code-editor">
      <h3>你的代码：</h3>
      <textarea 
        v-model="userCode" 
        placeholder="请输入你的代码..." 
        rows="15"
      ></textarea>
      <button @click="submitCode" class="submit-btn" :disabled="!problem || !userCode">
        提交代码
      </button>
    </div>
    
    <!-- 评估结果 -->
    <div v-if="evaluation" class="evaluation-result">
      <h3>评估结果：</h3>
      <div class="evaluation-status" :class="evaluation.is_correct ? 'correct' : 'incorrect'">
        {{ evaluation.is_correct ? '代码正确！' : '代码存在问题' }}
      </div>
      
      <div v-if="evaluation.errors && evaluation.errors.length > 0" class="errors">
        <h4>存在的问题：</h4>
        <ul>
          <li v-for="(error, index) in evaluation.errors" :key="index">{{ error }}</li>
        </ul>
      </div>
      
      <div v-if="evaluation.suggestions && evaluation.suggestions.length > 0" class="suggestions">
        <h4>改进建议：</h4>
        <ul>
          <li v-for="(suggestion, index) in evaluation.suggestions" :key="index">{{ suggestion }}</li>
        </ul>
      </div>
      
      <div v-if="evaluation.quality_score" class="quality-score">
        <h4>代码质量评分：{{ evaluation.quality_score }}/100</h4>
      </div>
      
      <div v-if="evaluation.explanation" class="explanation">
        <h4>详细解释：</h4>
        <p>{{ evaluation.explanation }}</p>
      </div>
      
      <div v-if="evaluation.finalCode" class="final-code">
        <h4>你的代码：</h4>
        <pre>{{ evaluation.finalCode }}</pre>
      </div>
      
      <div v-if="evaluation.debugSuggestion" class="debug-suggestion">
        <h4>调试建议：</h4>
        <div v-if="evaluation.debugSuggestion.isFixed" class="fixed-success">
          ✓ 调试成功！
        </div>
        <div v-else class="fixed-failed">
          ✗ 调试失败
        </div>
        <div v-if="evaluation.debugSuggestion.suggestedFix" class="suggested-code">
          <h5>建议的修复代码：</h5>
          <pre>{{ evaluation.debugSuggestion.suggestedFix }}</pre>
        </div>
      </div>
      
      <div class="debug-info">
        <p>调试次数：{{ evaluation.debugSuggestion?.debugAttempts || 0 }}/5</p>
      </div>
    </div>
    
    <!-- 用户答题历史 -->
    <div v-if="userAnswers.length > 0" class="user-answers">
      <h3>答题历史：</h3>
      <div v-for="(answer, index) in userAnswers" :key="answer.id" class="answer-item">
        <div class="answer-header">
          <span class="answer-index">提交 #{{ index + 1 }}</span>
          <span class="answer-time">{{ formatDate(answer.createdAt) }}</span>
        </div>
        <div class="answer-code">
          <pre>{{ answer.userCode }}</pre>
        </div>
        <div v-if="answer.evaluationResult" class="answer-evaluation" :class="answer.evaluationResult.isCorrect ? 'correct' : 'incorrect'">
          {{ answer.evaluationResult.isCorrect ? '代码正确！' : '代码存在问题' }}
        </div>
        <div v-if="answer.evaluationResult && answer.evaluationResult.qualityScore" class="answer-quality">
          代码质量评分：{{ answer.evaluationResult.qualityScore }}/100
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      加载中...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { codingPlaygroundApi } from '../api'

// 响应式数据
const difficulty = ref(1)
const problem = ref(null)
const userCode = ref('')
const evaluation = ref(null)
const loading = ref(false)
const userAnswers = ref([])

// 安全的日期格式化函数
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return isNaN(date.getTime()) ? '' : date.toLocaleString()
}

// 加载题目
const loadProblem = async () => {
  console.log('开始加载题目，难度:', difficulty.value)
  loading.value = true
  evaluation.value = null
  userCode.value = ''
  userAnswers.value = []
  
  try {
    const data = await codingPlaygroundApi.getProblem(difficulty.value)
    console.log('获取题目成功，数据:', data)
    
    if (data.success && data.problem) {
      problem.value = data.problem
      console.log('设置 problem:', problem.value)
      // 获取用户答题历史
      console.log('准备获取答题历史，problemId:', data.problem.id)
      await loadUserAnswers(data.problem.id)
    } else {
      console.error('获取题目失败，data:', data)
      alert('获取题目失败')
    }
  } catch (error) {
    console.error('获取题目失败:', error)
    alert('获取题目失败: ' + (error.message || '网络错误'))
  } finally {
    loading.value = false
    console.log('加载题目完成，userAnswers:', userAnswers.value)
  }
}

// 加载用户答题历史
const loadUserAnswers = async (problemId) => {
  try {
    console.log('开始获取答题历史，problemId:', problemId)
    const data = await codingPlaygroundApi.getUserAnswers(problemId)
    console.log('获取答题历史成功，数据:', data)
    if (data.success) {
      userAnswers.value = data.answers
      console.log('更新 userAnswers:', userAnswers.value)
    }
  } catch (error) {
    console.error('获取答题历史失败:', error)
  }
}

// 提交代码
const submitCode = async () => {
  if (!problem.value || !userCode.value) return
  
  loading.value = true
  
  try {
    const data = await codingPlaygroundApi.submitCode(
      problem.value.id,
      userCode.value
    )
    
    if (data.success) {
      evaluation.value = data.evaluation
      // 重新加载用户答题历史
      await loadUserAnswers(problem.value.id)
    } else {
      alert('提交失败')
    }
  } catch (error) {
    console.error('提交代码失败:', error)
    alert('提交代码失败: ' + (error.message || '网络错误'))
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载题目
onMounted(() => {
  loadProblem()
})
</script>

<style scoped>
.coding-playground {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #333;
  margin-bottom: 30px;
}

.difficulty-selector {
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.difficulty-selector select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.refresh-btn, .submit-btn {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.refresh-btn:hover, .submit-btn:hover {
  background-color: #45a049;
}

.submit-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.problem-container {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  border: 1px solid #ddd;
}

.problem-description {
  margin: 20px 0;
  line-height: 1.6;
}

.examples {
  margin-top: 20px;
}

.example-item {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
}

.example-input, .example-output {
  margin: 5px 0;
}

.code-editor {
  margin-bottom: 30px;
}

.code-editor textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  resize: vertical;
  margin-bottom: 10px;
}

.evaluation-result {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.evaluation-status {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  padding: 10px;
  border-radius: 4px;
}

.evaluation-status.correct {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.evaluation-status.incorrect {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.errors, .suggestions {
  margin: 15px 0;
}

.errors ul, .suggestions ul {
  margin-left: 20px;
}

.final-code {
  margin-top: 20px;
}

.final-code pre {
  background-color: #f0f0f0;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
}

.debug-info {
  margin-top: 20px;
  font-style: italic;
  color: #666;
}

.debug-suggestion {
  margin-top: 20px;
  padding: 15px;
  background-color: #f0f8ff;
  border-radius: 4px;
  border: 1px solid #b3d9ff;
}

.fixed-success {
  background-color: #d4edda;
  color: #155724;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  border: 1px solid #c3e6cb;
  font-weight: bold;
}

.fixed-failed {
  background-color: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  border: 1px solid #f5c6cb;
  font-weight: bold;
}

.suggested-code {
  margin-top: 15px;
}

.suggested-code pre {
  background-color: #f8f8f8;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  border: 1px solid #e0e0e0;
  margin-top: 10px;
}

.loading {
  text-align: center;
  padding: 20px;
  font-size: 16px;
  color: #666;
}

/* 用户答题历史样式 */
.user-answers {
  margin-top: 30px;
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.answer-item {
  background-color: #f0f0f0;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 15px;
  border: 1px solid #e0e0e0;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
  color: #666;
}

.answer-index {
  font-weight: bold;
}

.answer-code {
  margin: 10px 0;
}

.answer-code pre {
  background-color: #f8f8f8;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  border: 1px solid #e0e0e0;
}

.answer-evaluation {
  padding: 8px;
  border-radius: 4px;
  font-weight: bold;
  margin: 10px 0;
}

.answer-evaluation.correct {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.answer-evaluation.incorrect {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.answer-quality {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}
</style>