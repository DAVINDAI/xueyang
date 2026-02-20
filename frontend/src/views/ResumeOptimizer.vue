<template>
  <div class="resume-optimizer">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>简历优化工具</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="80px">
        <!-- PDF文件上传 -->
        <el-form-item label="上传简历" required>
          <el-upload
            class="upload-demo"
            drag
            :action="''"
            :auto-upload="false"
            :on-change="handleFileChange"
            :multiple="false"
            accept=".pdf"
            :limit="1"
            :file-list="fileList"
            :disabled="loading"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">
              将PDF文件拖到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip text-danger">
                仅支持PDF格式文件，大小不超过10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <!-- 职位描述输入 -->
        <el-form-item label="职位描述" required>
          <el-input
            v-model="form.jobDescription"
            type="textarea"
            :rows="6"
            placeholder="请输入详细的职位描述，包括职责、要求、技能等"
            :disabled="loading"
          />
        </el-form-item>
        
        <!-- 提交按钮 -->
        <el-form-item>
          <el-button 
            type="primary" 
            @click="submitForm" 
            :loading="loading"
            :disabled="!canSubmit"
          >
            <el-icon v-if="!loading"><RefreshRight /></el-icon>
            <span>{{ loading ? '优化中...' : '开始优化' }}</span>
          </el-button>
          <el-button @click="resetForm" :disabled="loading">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 结果展示区域 -->
    <el-card v-if="result" class="result-card" :loading="loading">
      <template #header>
        <div class="card-header">
          <el-icon><Check /></el-icon>
          <span>优化结果</span>
        </div>
      </template>
      
      <div class="result-content">
        <!-- 行业分析 -->
        <el-collapse v-model="activeNames">
          <el-collapse-item title="行业分析" name="1">
            <div class="markdown-content" v-html="renderMarkdown(result.industryAnalysis)"></div>
          </el-collapse-item>
          
          <!-- 优化后的简历 -->
          <el-collapse-item title="优化后的简历" name="2">
            <div class="markdown-content" v-html="renderMarkdown(result.optimizedResume)"></div>
            <el-button type="success" size="small" @click="downloadResume" style="margin-top: 10px">
              <el-icon><Download /></el-icon>
              下载优化简历
            </el-button>
          </el-collapse-item>
          
          <!-- 优化建议 -->
          <el-collapse-item title="优化建议" name="3">
            <ul class="suggestions-list">
              <li v-for="(suggestion, index) in result.optimizationSuggestions" :key="index">
                {{ suggestion }}
              </li>
            </ul>
          </el-collapse-item>
          
          <!-- 匹配度分析 -->
          <el-collapse-item title="匹配度分析" name="4">
            <el-descriptions :column="2">
              <el-descriptions-item label="核心技能匹配度">
                <el-progress 
                  :percentage="parsePercentage(result.matchingAnalysis.coreSkills)" 
                  :color="getProgressColor(result.matchingAnalysis.coreSkills)"
                />
                <span class="percentage">{{ result.matchingAnalysis.coreSkills }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="工作经验匹配度">
                <el-progress 
                  :percentage="parsePercentage(result.matchingAnalysis.workExperience)" 
                  :color="getProgressColor(result.matchingAnalysis.workExperience)"
                />
                <span class="percentage">{{ result.matchingAnalysis.workExperience }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="教育背景匹配度">
                <el-progress 
                  :percentage="parsePercentage(result.matchingAnalysis.education)" 
                  :color="getProgressColor(result.matchingAnalysis.education)"
                />
                <span class="percentage">{{ result.matchingAnalysis.education }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="行业适配度">
                <el-progress 
                  :percentage="parsePercentage(result.matchingAnalysis.industryFit)" 
                  :color="getProgressColor(result.matchingAnalysis.industryFit)"
                />
                <span class="percentage">{{ result.matchingAnalysis.industryFit }}</span>
              </el-descriptions-item>
            </el-descriptions>
          </el-collapse-item>
          
          <!-- 面试准备建议 -->
          <el-collapse-item title="面试准备建议" name="5">
            <div class="markdown-content" v-html="renderMarkdown(result.interviewPreparation)"></div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Upload, RefreshRight, Check, Download } from '@element-plus/icons-vue'
import { resumeApi } from '../api/resumeApi'
import { marked } from 'marked'

// 表单数据
const form = ref({
  jobDescription: ''
})

// 文件列表
const fileList = ref([])
const selectedFile = ref(null)

// 加载状态
const loading = ref(false)

// 结果数据
const result = ref(null)

// 折叠面板状态
const activeNames = ref(['1'])

// 计算是否可以提交
const canSubmit = computed(() => {
  return selectedFile.value && form.value.jobDescription.trim()
})

// 处理文件选择
const handleFileChange = (file) => {
  // 验证文件类型
  if (!file.name.endsWith('.pdf')) {
    ElMessage.error('仅支持PDF格式文件')
    return
  }
  
  // 验证文件大小（10MB）
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return
  }
  
  selectedFile.value = file.raw
  fileList.value = [file]
}

// 提交表单
const submitForm = async () => {
  if (!canSubmit.value) return
  
  loading.value = true
  
  try {
    const formData = new FormData()
    formData.append('resume', selectedFile.value)
    formData.append('job_description', form.value.jobDescription)
    
    const response = await resumeApi.optimizeResume(formData)
    result.value = normalizeResult(response.data)
    
    ElMessage.success('简历优化成功！')
  } catch (error) {
    console.error('优化失败:', error)
    ElMessage.error('简历优化失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  form.value.jobDescription = ''
  fileList.value = []
  selectedFile.value = null
  result.value = null
  activeNames.value = ['1']
}

// 安全访问嵌套属性
const safeGet = (obj, path, defaultValue = '') => {
  return path.split('.').reduce((current, key) => {
    return current && current[key] !== undefined ? current[key] : defaultValue
  }, obj)
}

// 解析百分比
const parsePercentage = (value) => {
  if (!value) return 0
  if (typeof value === 'string') {
    const num = parseInt(value.replace('%', ''))
    return isNaN(num) ? 0 : num
  }
  return typeof value === 'number' ? value : 0
}

// 获取进度条颜色
const getProgressColor = (value) => {
  const percentage = parsePercentage(value)
  if (percentage >= 80) return '#67C23A'
  if (percentage >= 60) return '#E6A23C'
  return '#F56C6C'
}

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true
})

// 渲染 Markdown
const renderMarkdown = (text) => {
  if (!text) return ''
  return marked.parse(text)
}

// 验证并规范化结果数据
const normalizeResult = (data) => {
  if (!data) return null
  
  return {
    industryAnalysis: safeGet(data, 'industryAnalysis', '暂无行业分析'),
    optimizedResume: safeGet(data, 'optimizedResume', '暂无优化后的简历'),
    optimizationSuggestions: Array.isArray(data.optimizationSuggestions) 
      ? data.optimizationSuggestions 
      : ['暂无优化建议'],
    matchingAnalysis: {
      coreSkills: safeGet(data, 'matchingAnalysis.coreSkills', '0%'),
      workExperience: safeGet(data, 'matchingAnalysis.workExperience', '0%'),
      education: safeGet(data, 'matchingAnalysis.education', '0%'),
      industryFit: safeGet(data, 'matchingAnalysis.industryFit', '0%')
    },
    interviewPreparation: safeGet(data, 'interviewPreparation', '暂无面试准备建议')
  }
}

// 下载简历
const downloadResume = () => {
  // 实现下载逻辑
  ElMessage.info('下载功能开发中')
}
</script>

<style scoped>
.resume-optimizer {
  max-width: 900px;
  margin: 20px auto;
  padding: 0 20px;
}

.card-container {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
}

.result-card {
  margin-top: 30px;
}

.result-content {
  line-height: 1.6;
}

.suggestions-list {
  list-style: none;
  padding: 0;
}

.suggestions-list li {
  margin-bottom: 10px;
  padding-left: 20px;
  position: relative;
}

.suggestions-list li::before {
  content: '•';
  color: #409EFF;
  font-weight: bold;
  position: absolute;
  left: 0;
}

.percentage {
  margin-left: 10px;
  font-weight: bold;
}

.text-danger {
  color: #F56C6C;
}

:deep(.el-collapse-item__content) {
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

/* Markdown 内容样式 */
.markdown-content {
  line-height: 1.8;
  color: #303133;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  margin-top: 20px;
  margin-bottom: 10px;
  font-weight: 600;
  color: #303133;
}

.markdown-content h1 {
  font-size: 24px;
  border-bottom: 2px solid #409EFF;
  padding-bottom: 10px;
}

.markdown-content h2 {
  font-size: 20px;
  border-bottom: 1px solid #dcdfe6;
  padding-bottom: 8px;
}

.markdown-content h3 {
  font-size: 18px;
}

.markdown-content p {
  margin: 10px 0;
}

.markdown-content ul,
.markdown-content ol {
  margin: 10px 0;
  padding-left: 30px;
}

.markdown-content li {
  margin: 5px 0;
}

.markdown-content code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #f56c6c;
}

.markdown-content pre {
  background-color: #2d2d2d;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 15px 0;
}

.markdown-content pre code {
  background-color: transparent;
  color: #f8f8f2;
  padding: 0;
}

.markdown-content blockquote {
  border-left: 4px solid #409EFF;
  padding-left: 15px;
  margin: 15px 0;
  color: #606266;
  background-color: #ecf5ff;
  padding: 10px 15px;
  border-radius: 0 4px 4px 0;
}

.markdown-content a {
  color: #409EFF;
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

.markdown-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid #dcdfe6;
  padding: 10px;
  text-align: left;
}

.markdown-content th {
  background-color: #f5f7fa;
  font-weight: 600;
}
</style>
