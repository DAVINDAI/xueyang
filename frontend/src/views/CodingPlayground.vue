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
      
      <div v-if="evaluation.staticAnalysis" class="static-analysis">
        <h4>代码静态分析：</h4>
        <div class="analysis-item">
          <span class="analysis-label">语法检查：</span>
          <span :class="evaluation.staticAnalysis.syntaxError ? 'error' : 'success'">
            {{ evaluation.staticAnalysis.syntaxError ? '存在语法错误' : '语法正确' }}
          </span>
        </div>
        <div v-if="evaluation.staticAnalysis.syntaxError" class="syntax-error-details">
          <h5>语法错误详情：</h5>
          <div class="error-detail-item">
            <span class="error-detail-label">错误信息：</span>
            <span class="error-detail-value">{{ evaluation.staticAnalysis.syntaxErrorMessage }}</span>
          </div>
          <div class="error-detail-item">
            <span class="error-detail-label">错误位置：</span>
            <span class="error-detail-value">第 {{ evaluation.staticAnalysis.syntaxErrorLine }} 行，第 {{ evaluation.staticAnalysis.syntaxErrorOffset }} 列</span>
          </div>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">代码复杂度：</span>
          <span class="analysis-value">{{ evaluation.staticAnalysis.complexity }}</span>
        </div>
        <div v-if="evaluation.staticAnalysis.potentialIssues && evaluation.staticAnalysis.potentialIssues.length > 0" class="potential-issues">
          <h5>潜在问题：</h5>
          <ul>
            <li v-for="(issue, index) in evaluation.staticAnalysis.potentialIssues" :key="index" class="issue-item">{{ issue }}</li>
          </ul>
        </div>
        <div v-if="evaluation.staticAnalysis.codeStructure" class="code-structure">
          <h5>代码结构：</h5>
          <div v-if="evaluation.staticAnalysis.codeStructure.functions && evaluation.staticAnalysis.codeStructure.functions.length > 0" class="structure-section">
            <strong>函数：</strong>
            <ul>
              <li v-for="(func, index) in evaluation.staticAnalysis.codeStructure.functions" :key="index">
                {{ func.name }} (参数: {{ func.args.join(', ') }}) - 行{{ func.line }}
              </li>
            </ul>
          </div>
          <div v-if="evaluation.staticAnalysis.codeStructure.classes && evaluation.staticAnalysis.codeStructure.classes.length > 0" class="structure-section">
            <strong>类：</strong>
            <ul>
              <li v-for="(cls, index) in evaluation.staticAnalysis.codeStructure.classes" :key="index">
                {{ cls.name }} - 行{{ cls.line }}
              </li>
            </ul>
          </div>
          <div v-if="evaluation.staticAnalysis.codeStructure.imports && evaluation.staticAnalysis.codeStructure.imports.length > 0" class="structure-section">
            <strong>导入：</strong>
            <ul>
              <li v-for="(imp, index) in evaluation.staticAnalysis.codeStructure.imports" :key="index">{{ imp }}</li>
            </ul>
          </div>
        </div>
      </div>
      
      <div v-if="evaluation.executionResults" class="execution-results">
        <h4>本地运行结果：</h4>
        <div class="execution-status" :class="evaluation.executionResults.success ? 'success' : 'error'">
          {{ evaluation.executionResults.success ? '✓ 所有测试用例通过' : '✗ 部分测试用例失败' }}
        </div>
        <div v-if="evaluation.executionResults.outputs && evaluation.executionResults.outputs.length > 0" class="test-cases">
          <h5>测试用例结果：</h5>
          <div v-for="(output, index) in evaluation.executionResults.outputs" :key="index" class="test-case">
            <div class="test-input">
              <strong>输入：</strong>{{ output.input }}
            </div>
            <div class="test-expected">
              <strong>期望输出：</strong>{{ output.expected }}
            </div>
            <div class="test-actual" :class="output.actual === output.expected ? 'match' : 'mismatch'">
              <strong>实际输出：</strong>{{ output.actual }}
            </div>
            <div class="test-time">
              <strong>执行时间：</strong>{{ output.executionTime?.toFixed(4) || 0 }}秒
            </div>
          </div>
        </div>
        <div v-if="evaluation.executionResults.errors && evaluation.executionResults.errors.length > 0" class="execution-errors">
          <h5>运行错误：</h5>
          <ul>
            <li v-for="(error, index) in evaluation.executionResults.errors" :key="index" class="error-item">{{ error }}</li>
          </ul>
        </div>
      </div>
      
      <div v-if="evaluation.performanceMetrics" class="performance-metrics">
        <h4>性能指标：</h4>
        <div class="metric-item">
          <span class="metric-label">平均执行时间：</span>
          <span class="metric-value">{{ evaluation.performanceMetrics.averageExecutionTime?.toFixed(4) || 0 }}秒</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">时间复杂度：</span>
          <span class="metric-value">{{ evaluation.performanceMetrics.timeComplexity || 'Unknown' }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">空间复杂度：</span>
          <span class="metric-value">{{ evaluation.performanceMetrics.spaceComplexity || 'Unknown' }}</span>
        </div>
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
      
      <div v-if="evaluation.debugSuggestion && evaluation.debugSuggestion.debugHistory && evaluation.debugSuggestion.debugHistory.length > 0" class="debug-history">
        <h4>调试过程记录：</h4>
        <div v-for="(record, index) in evaluation.debugSuggestion.debugHistory" :key="index" class="history-item">
          <div class="history-header">
            <span class="history-step">步骤 {{ record.step }}</span>
            <span class="history-action" :class="'action-' + record.action">{{ getActionName(record.action) }}</span>
          </div>
          <div v-if="record.action === 'generate_fix'" class="history-content">
            <div class="history-section">
              <strong>输入代码：</strong>
              <pre>{{ record.inputCode }}</pre>
            </div>
            <div v-if="record.errors && record.errors.length > 0" class="history-section">
              <strong>错误：</strong>
              <ul>
                <li v-for="(error, errIndex) in record.errors" :key="errIndex" class="history-error">{{ error }}</li>
              </ul>
            </div>
            <div v-if="record.outputCode" class="history-section">
              <strong>输出代码：</strong>
              <pre>{{ record.outputCode }}</pre>
            </div>
            <div v-if="record.explanation" class="history-section">
              <strong>解释：</strong>
              <p>{{ record.explanation }}</p>
            </div>
            <div v-if="record.suggestions && record.suggestions.length > 0" class="history-section">
              <strong>建议：</strong>
              <ul>
                <li v-for="(suggestion, sugIndex) in record.suggestions" :key="sugIndex">{{ suggestion }}</li>
              </ul>
            </div>
          </div>
          <div v-if="record.action === 'test_fix'" class="history-content">
            <div class="history-section">
              <strong>输入代码：</strong>
              <pre>{{ record.inputCode }}</pre>
            </div>
            <div class="history-section">
              <strong>测试结果：</strong>
              <span :class="record.success ? 'success' : 'error'">
                {{ record.success ? '✓ 通过' : '✗ 失败' }}
              </span>
            </div>
            <div v-if="record.executionResults" class="history-section">
              <strong>执行结果：</strong>
              <div v-if="record.executionResults.outputs && record.executionResults.outputs.length > 0" class="history-outputs">
                <div v-for="(output, outIndex) in record.executionResults.outputs" :key="outIndex" class="history-output">
                  <span>输入: {{ output.input }}</span>
                  <span>期望: {{ output.expected }}</span>
                  <span :class="output.actual === output.expected ? 'match' : 'mismatch'">实际: {{ output.actual }}</span>
                </div>
              </div>
            </div>
            <div v-if="record.performanceMetrics" class="history-section">
              <strong>性能指标：</strong>
              <div>执行时间: {{ record.performanceMetrics.averageExecutionTime?.toFixed(4) || 0 }}秒</div>
              <div>时间复杂度: {{ record.performanceMetrics.timeComplexity || 'Unknown' }}</div>
            </div>
          </div>
          <div v-if="record.action === 'evaluate_fix'" class="history-content">
            <div class="history-section">
              <strong>输入代码：</strong>
              <pre>{{ record.inputCode }}</pre>
            </div>
            <div class="history-section">
              <strong>评估结果：</strong>
              <span :class="record.isCorrect ? 'success' : 'error'">
                {{ record.isCorrect ? '✓ 正确' : '✗ 不正确' }}
              </span>
            </div>
            <div class="history-section">
              <strong>质量评分：</strong>
              <span>{{ record.qualityScore }}/100</span>
            </div>
            <div v-if="record.errors && record.errors.length > 0" class="history-section">
              <strong>错误：</strong>
              <ul>
                <li v-for="(error, errIndex) in record.errors" :key="errIndex" class="history-error">{{ error }}</li>
              </ul>
            </div>
            <div v-if="record.suggestions && record.suggestions.length > 0" class="history-section">
              <strong>建议：</strong>
              <ul>
                <li v-for="(suggestion, sugIndex) in record.suggestions" :key="sugIndex">{{ suggestion }}</li>
              </ul>
            </div>
            <div v-if="record.explanation" class="history-section">
              <strong>解释：</strong>
              <p>{{ record.explanation }}</p>
            </div>
          </div>
          <div v-if="record.action === 'optimize_code'" class="history-content">
            <div class="history-section">
              <strong>输入代码：</strong>
              <pre>{{ record.inputCode }}</pre>
            </div>
            <div v-if="record.outputCode" class="history-section">
              <strong>优化后代码：</strong>
              <pre>{{ record.outputCode }}</pre>
            </div>
            <div v-if="record.explanation" class="history-section">
              <strong>优化解释：</strong>
              <p>{{ record.explanation }}</p>
            </div>
          </div>
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

// 获取操作名称
const getActionName = (action) => {
  const actionNames = {
    'generate_fix': '生成修复',
    'test_fix': '测试修复',
    'evaluate_fix': '评估修复',
    'optimize_code': '优化代码'
  }
  return actionNames[action] || action
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

.performance-metrics {
  margin: 15px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e9ecef;
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-label {
  font-weight: 600;
  color: #495057;
}

.metric-value {
  color: #28a745;
  font-family: 'Courier New', Courier, monospace;
}

.static-analysis {
  margin: 15px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.analysis-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e9ecef;
}

.analysis-item:last-child {
  border-bottom: none;
}

.analysis-label {
  font-weight: 600;
  color: #495057;
}

.analysis-value {
  color: #007bff;
  font-family: 'Courier New', Courier, monospace;
}

.analysis-item .success {
  color: #28a745;
  font-weight: 600;
}

.analysis-item .error {
  color: #dc3545;
  font-weight: 600;
}

.potential-issues {
  margin-top: 15px;
}

.potential-issues ul {
  margin-left: 20px;
}

.issue-item {
  color: #dc3545;
  padding: 5px 0;
}

.syntax-error-details {
  margin-top: 15px;
  padding: 12px;
  background-color: #fff3cd;
  border-radius: 4px;
  border: 1px solid #ffeeba;
}

.syntax-error-details h5 {
  color: #856404;
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 600;
}

.error-detail-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #ffeeba;
}

.error-detail-item:last-child {
  border-bottom: none;
}

.error-detail-label {
  font-weight: 600;
  color: #856404;
}

.error-detail-value {
  color: #dc3545;
  font-family: 'Courier New', Courier, monospace;
}

.code-structure {
  margin-top: 15px;
}

.structure-section {
  margin-bottom: 15px;
}

.structure-section ul {
  margin-left: 20px;
}

.execution-results {
  margin: 15px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.execution-status {
  font-size: 16px;
  font-weight: bold;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  text-align: center;
}

.execution-status.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.execution-status.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.test-cases {
  margin-top: 15px;
}

.test-case {
  background-color: #ffffff;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 10px;
  border: 1px solid #dee2e6;
}

.test-input,
.test-expected,
.test-actual,
.test-time {
  padding: 5px 0;
  border-bottom: 1px solid #e9ecef;
}

.test-input:last-child,
.test-expected:last-child,
.test-actual:last-child,
.test-time:last-child {
  border-bottom: none;
}

.test-actual.match {
  color: #28a745;
}

.test-actual.mismatch {
  color: #dc3545;
}

.execution-errors {
  margin-top: 15px;
}

.execution-errors ul {
  margin-left: 20px;
}

.error-item {
  color: #dc3545;
  padding: 5px 0;
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

.debug-history {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.history-item {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #ffffff;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e9ecef;
}

.history-step {
  font-weight: 600;
  color: #495057;
  font-size: 16px;
}

.history-action {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.history-action.action-generate_fix {
  background-color: #e7f3ff;
  color: #004085;
}

.history-action.action-test_fix {
  background-color: #ffc107;
  color: #856404;
}

.history-action.action-evaluate_fix {
  background-color: #17a2b8;
  color: #ffffff;
}

.history-action.action-optimize_code {
  background-color: #28a745;
  color: #ffffff;
}

.history-content {
  margin-top: 10px;
}

.history-section {
  margin-bottom: 12px;
}

.history-section strong {
  display: block;
  margin-bottom: 5px;
  color: #495057;
  font-weight: 600;
}

.history-section pre {
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  border: 1px solid #e9ecef;
  margin-top: 5px;
}

.history-section p {
  margin: 5px 0;
  color: #495057;
}

.history-section ul {
  margin-left: 20px;
}

.history-error {
  color: #dc3545;
  padding: 3px 0;
}

.history-outputs {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-output {
  display: flex;
  gap: 10px;
  padding: 5px;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-size: 13px;
}

.history-output span.match {
  color: #28a745;
  font-weight: 600;
}

.history-output span.mismatch {
  color: #dc3545;
  font-weight: 600;
}

.history-section .success {
  color: #28a745;
  font-weight: 600;
}

.history-section .error {
  color: #dc3545;
  font-weight: 600;
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