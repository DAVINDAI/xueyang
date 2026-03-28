<template>
  <div class="resume-list">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <el-icon><DocumentCopy /></el-icon>
          <span>优化历史</span>
        </div>
      </template>
      
      <div class="search-bar">
        <el-button type="primary" @click="navigateToOptimizer">
          <el-icon><Plus /></el-icon>
          新的优化
        </el-button>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索职位标题"
          prefix-icon="Search"
          style="width: 300px; margin-left: 20px"
          @keyup.enter="loadOptimizations"
        />
      </div>
      
      <div v-loading="loading" class="table-container">
        <el-empty v-if="!loading && optimizations.length === 0" description="暂无优化记录" />
        
        <el-table v-else :data="optimizations" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="jobTitle" label="职位标题">
            <template #default="scope">
              <el-tooltip :content="scope.row.jobTitle" placement="top">
                <div class="job-title">{{ scope.row.jobTitle }}</div>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column label="行业" width="150">
            <template #default="scope">
              <el-tag size="small">{{ getIndustry(scope.row.industryAnalysis) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="匹配度" width="120">
            <template #default="scope">
              <div class="matching-score">
                {{ getAverageMatchingScore(scope.row.matchingAnalysis) }}%
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" width="180">
            <template #default="scope">
              <span>{{ formatDate(scope.row.createdAt) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="scope">
              <el-button size="small" type="primary" @click="viewDetails(scope.row.id)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button size="small" type="danger" @click="confirmDelete(scope.row.id)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="优化详情"
      width="80%"
      destroy-on-close
    >
      <div v-if="currentOptimization" class="optimization-details">
        <h3>{{ currentOptimization.jobTitle }}</h3>
        <div class="detail-section">
          <h4>行业分析</h4>
          <div class="markdown-content" v-html="renderMarkdown(currentOptimization.industryAnalysis)"></div>
        </div>
        <div class="detail-section">
          <h4>优化建议</h4>
          <ul>
            <li v-for="(suggestion, index) in currentOptimization.optimizationSuggestions" :key="index">
              {{ suggestion }}
            </li>
          </ul>
        </div>
        <div class="detail-section">
          <h4>匹配度分析</h4>
          <el-descriptions :column="2">
            <el-descriptions-item label="核心技能">
              {{ currentOptimization.matchingAnalysis?.coreSkills || '0%' }}
            </el-descriptions-item>
            <el-descriptions-item label="工作经验">
              {{ currentOptimization.matchingAnalysis?.workExperience || '0%' }}
            </el-descriptions-item>
            <el-descriptions-item label="教育背景">
              {{ currentOptimization.matchingAnalysis?.education || '0%' }}
            </el-descriptions-item>
            <el-descriptions-item label="行业适配度">
              {{ currentOptimization.matchingAnalysis?.industryFit || '0%' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        <div class="detail-section" v-if="currentOptimization.interviewPreparation">
          <h4>面试建议</h4>
          <div class="markdown-content" v-html="renderMarkdown(currentOptimization.interviewPreparation)"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentCopy, Plus, Search, View, Delete } from '@element-plus/icons-vue'
import { marked } from 'marked'
import { resumeApi } from '../api'

const router = useRouter()
const loading = ref(false)
const optimizations = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const dialogVisible = ref(false)
const currentOptimization = ref(null)

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

// 导航到优化页面
const navigateToOptimizer = () => {
  router.push('/resume')
}

// 加载优化结果
const loadOptimizations = async () => {
  loading.value = true
  try {
    const response = await resumeApi.getOptimizations()
    let data = response.data || []
    
    // 搜索过滤
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      data = data.filter(item => 
        item.jobTitle.toLowerCase().includes(keyword)
      )
    }
    
    optimizations.value = data
    total.value = data.length
  } catch (error) {
    console.error('加载优化结果失败:', error)
    ElMessage.error(error.message || '加载优化结果失败')
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetails = async (id) => {
  try {
    const response = await resumeApi.getOptimization(id)
    currentOptimization.value = response.data
    dialogVisible.value = true
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error(error.message || '获取详情失败')
  }
}

// 确认删除
const confirmDelete = (id) => {
  ElMessageBox.confirm('确定要删除这条记录吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await deleteOptimization(id)
  }).catch(() => {
    // 取消删除
  })
}

// 删除优化结果
const deleteOptimization = async (id) => {
  try {
    await resumeApi.deleteOptimization(id)
    ElMessage.success('删除成功')
    await loadOptimizations()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error(error.message || '删除失败')
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 提取行业
const getIndustry = (industryAnalysis) => {
  if (!industryAnalysis) return '未知'
  // 简单提取行业名称
  const lines = industryAnalysis.split('\n')
  for (const line of lines) {
    if (line.includes('行业')) {
      return line.substring(0, 20)
    }
  }
  return '未知'
}

// 计算平均匹配度
const getAverageMatchingScore = (matchingAnalysis) => {
  if (!matchingAnalysis) return 0
  const scores = []
  Object.values(matchingAnalysis).forEach(value => {
    if (typeof value === 'string') {
      const score = parseInt(value.replace('%', ''))
      if (!isNaN(score)) {
        scores.push(score)
      }
    }
  })
  if (scores.length === 0) return 0
  const average = scores.reduce((sum, score) => sum + score, 0) / scores.length
  return Math.round(average)
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadOptimizations()
}

const handleCurrentChange = (current) => {
  currentPage.value = current
  loadOptimizations()
}

// 生命周期
onMounted(() => {
  loadOptimizations()
})
</script>

<style scoped>
.resume-list {
  max-width: 1200px;
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

.search-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.table-container {
  margin-bottom: 20px;
}

.job-title {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.matching-score {
  font-weight: bold;
  color: #409EFF;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.optimization-details {
  line-height: 1.6;
}

.optimization-details h3 {
  margin-bottom: 20px;
  color: #303133;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section h4 {
  margin-bottom: 10px;
  color: #409EFF;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 5px;
}

.detail-section ul {
  padding-left: 20px;
}

.detail-section li {
  margin-bottom: 5px;
}

.markdown-content {
  line-height: 1.8;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3 {
  margin-top: 15px;
  margin-bottom: 10px;
}

.markdown-content p {
  margin: 10px 0;
}

.markdown-content ul,
.markdown-content ol {
  margin: 10px 0;
  padding-left: 30px;
}
</style>
