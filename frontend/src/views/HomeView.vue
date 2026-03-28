<template>
  <div class="home">
    <div class="hero">
      <h1>学氧学习助手</h1>
      <p class="tagline">让学习像呼吸一样自然</p>
      <p class="description">我们致力于通过人工智能技术，为每一位学习者提供个性化、智能化的学习支持，成为您的终身学习伙伴。</p>
      
      <div class="search-container">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索内容..."
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <button class="search-btn" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </button>
        </div>
      </div>
      
      <div class="core-values">
        <div class="value-item">
          <div class="value-icon">📚</div>
          <p>学无止境</p>
        </div>
        <div class="value-item">
          <div class="value-icon">🌱</div>
          <p>氧气般自然</p>
        </div>
        <div class="value-item">
          <div class="value-icon">🤖</div>
          <p>科技赋能</p>
        </div>
      </div>
      <!-- 暂时隐藏网站进化功能 -->
      <!-- <div class="evolution-section">
        <el-button type="primary" @click="evolveWebsite" :loading="isLoading" size="large">
          <el-icon><Refresh /></el-icon> 网站进化
        </el-button>
        <p class="evolution-hint">点击按钮启动网站自动进化，让AI为您优化网站体验</p>
      </div> -->
      
      <!-- 暂时隐藏进化结果对话框 -->
      <!-- <el-dialog
        v-model="resultDialogVisible"
        title="网站进化结果"
        width="80%"
      >
        <div v-if="evolutionResult" class="evolution-result">
          <el-collapse>
            <el-collapse-item title="用户体验建议">
              <div v-html="renderMarkdown(evolutionResult.user_experience)"></div>
            </el-collapse-item>
            <el-collapse-item title="交互设计建议">
              <div v-html="renderMarkdown(evolutionResult.interaction_design)"></div>
            </el-collapse-item>
            <el-collapse-item title="视觉设计建议">
              <div v-html="renderMarkdown(evolutionResult.visual_design)"></div>
            </el-collapse-item>
            <el-collapse-item title="前端实现建议">
              <div v-html="renderMarkdown(evolutionResult.frontend_implementation)"></div>
            </el-collapse-item>
            <el-collapse-item title="后端实现建议">
              <div v-html="renderMarkdown(evolutionResult.backend_implementation)"></div>
            </el-collapse-item>
          </el-collapse>
        </div>
        <div v-else>
          <p>正在生成进化建议...</p>
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="resultDialogVisible = false">关闭</el-button>
          </span>
        </template>
      </el-dialog> -->
    </div>
    <div class="notice-section">
      <div class="notice-box">
        <div class="notice-icon">⚠️</div>
        <div class="notice-content">
          <p>网站最多支持10个匿名用户使用，新用户数据会覆盖早期用户数据，如需长期使用请使用管理员账号登录，如有问题请发邮件至 <a href="mailto:davindai@foxmail.com" class="email-link">davindai@foxmail.com</a></p>
        </div>
      </div>
    </div>
    <div class="feature-section">
      <h2 class="section-title">学习工具</h2>
      <div class="features">
        <div class="feature-card">
          <div class="feature-icon">💬</div>
          <h3>智能学习助手</h3>
          <p>基于先进大语言模型的智能问答系统，为你解答学习中的各种问题，提供个性化的学习建议。</p>
          <router-link to="/chat" class="btn">开始对话</router-link>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>学习数据分析</h3>
          <p>追踪你的学习进度和习惯，提供详细的学习数据统计和分析，帮助你优化学习策略。</p>
          <router-link to="/stats" class="btn">查看分析</router-link>
        </div>
      </div>
    </div>
    
    <div class="feature-section">
      <h2 class="section-title">知识管理</h2>
      <div class="features">
        <div class="feature-card">
          <div class="feature-icon">📝</div>
          <h3>智能笔记管理</h3>
          <p>使用Markdown编辑器创建和管理个人笔记，支持知识整理和分类，让你的学习内容井井有条。</p>
          <router-link to="/notes" class="btn">管理笔记</router-link>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">📋</div>
          <h3>学习备忘录</h3>
          <p>快速记录学习中的重要信息和待办事项，帮助你保持学习的连续性和专注度。</p>
          <router-link to="/memo" class="btn">查看备忘录</router-link>
        </div>
      </div>
    </div>
    
    <div class="feature-section">
      <h2 class="section-title">职业发展</h2>
      <div class="features">
        <div class="feature-card">
          <div class="feature-icon">📄</div>
          <h3>简历优化</h3>
          <p>上传PDF简历，根据职位描述智能优化简历内容，提供面试准备建议，助你在求职路上脱颖而出。</p>
          <router-link to="/resume" class="btn">优化简历</router-link>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">📁</div>
          <h3>优化历史</h3>
          <p>查看和管理你的简历优化历史记录，跟踪每次优化的变化和进步。</p>
          <router-link to="/resume/list" class="btn">查看历史</router-link>
        </div>
      </div>
    </div>
    
    <div class="user-scenarios">
      <h2 class="section-title">目标用户</h2>
      <div class="scenarios-container">
        <div class="scenario-card">
          <div class="scenario-icon">📚</div>
          <h3>在校学生</h3>
          <p>课程辅导、作业答疑、知识点解析，帮助你轻松应对学业挑战</p>
        </div>
        
        <div class="scenario-card">
          <div class="scenario-icon">💼</div>
          <h3>职场人士</h3>
          <p>技能提升、职业规划、简历优化，助你在职场中脱颖而出</p>
        </div>
        
        <div class="scenario-card">
          <div class="scenario-icon">🌱</div>
          <h3>终身学习者</h3>
          <p>知识管理、学习规划、兴趣探索，陪伴你在学习的道路上不断前行</p>
        </div>
      </div>
    </div>
    
    <div class="tech-stack">
      <h2>技术栈</h2>
      <div class="tech-tags">
        <span class="tech-tag">Vue 3</span>
        <span class="tech-tag">Vite</span>
        <span class="tech-tag">Element Plus</span>
        <span class="tech-tag">FastAPI</span>
        <span class="tech-tag">JWT</span>
        <span class="tech-tag">LangGraph</span>
        <span class="tech-tag">Docker</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { evolutionApi } from '../api/index.js'
import { Refresh } from '@element-plus/icons-vue'
import { marked } from 'marked'

const router = useRouter()

const searchQuery = ref('良法善治')

const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  
  router.push({
    path: '/chat',
    query: { q: searchQuery.value }
  })
}

const isLoading = ref(false)
const resultDialogVisible = ref(false)
const evolutionResult = ref(null)

// 进化网站
const evolveWebsite = async () => {
  isLoading.value = true
  try {
    const response = await evolutionApi.evolve()
    evolutionResult.value = response
    resultDialogVisible.value = true
  } catch (error) {
    console.error('进化失败:', error)
    // 显示错误提示
  } finally {
    isLoading.value = false
  }
}

// 渲染Markdown
const renderMarkdown = (content) => {
  if (!content) return ''
  return marked(content)
}
</script>

<style scoped>
.home {
  min-height: calc(100vh - 140px);
  padding: 40px 0;
}

.hero {
  text-align: center;
  margin-bottom: 60px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #e6f7ee 0%, #e6f0ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.hero h1 {
  font-size: 3.5rem;
  color: #2c7a4c;
  margin-bottom: 20px;
  font-weight: 700;
}

.hero .tagline {
  font-size: 1.5rem;
  color: #4a90e2;
  margin-bottom: 20px;
  font-weight: 500;
}

.hero .description {
  font-size: 1.1rem;
  color: #5a5a5a;
  margin-bottom: 40px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.search-container {
  margin: 40px auto;
  max-width: 800px;
}

.search-box {
  display: flex;
  gap: 15px;
  background-color: white;
  padding: 15px;
  border-radius: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

.search-box:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 1.1rem;
  padding: 12px 20px;
  background-color: transparent;
  color: #333;
}

.search-input::placeholder {
  color: #999;
}

.search-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 32px;
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
}

.search-btn:hover {
  background: linear-gradient(135deg, #357abd 0%, #2c5a8a 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(74, 144, 226, 0.4);
}

.search-btn:active {
  transform: translateY(0);
}

.core-values {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 30px;
}

.value-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  transition: transform 0.3s ease;
}

.value-item:hover {
  transform: translateY(-5px);
}

.value-icon {
  font-size: 2.5rem;
}

.value-item p {
  margin: 0;
  font-size: 1rem;
  color: #333;
  font-weight: 500;
}

.feature-section {
  margin-bottom: 60px;
}

.section-title {
  font-size: 2rem;
  color: #2c7a4c;
  text-align: center;
  margin-bottom: 40px;
  font-weight: 600;
  position: relative;
}

.section-title::after {
  content: '';
  display: block;
  width: 80px;
  height: 4px;
  background-color: #4a90e2;
  margin: 10px auto 0;
  border-radius: 2px;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.feature-card {
  background-color: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-top: 4px solid #4a90e2;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.feature-icon {
  font-size: 3.5rem;
  margin-bottom: 20px;
  color: #2c7a4c;
}

.feature-card h3 {
  font-size: 1.5rem;
  color: #2c7a4c;
  margin-bottom: 15px;
  font-weight: 600;
}

.feature-card p {
  color: #5a5a5a;
  margin-bottom: 25px;
  line-height: 1.6;
}

.btn {
  display: inline-block;
  padding: 12px 24px;
  background-color: #4a90e2;
  color: white;
  text-decoration: none;
  border-radius: 25px;
  transition: all 0.3s ease;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
}

.btn:hover {
  background-color: #357abd;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.4);
}

.tech-stack {
  text-align: center;
  margin-top: 60px;
  padding: 40px 20px;
  background-color: #f8f9fa;
  border-radius: 12px;
}

.tech-stack h2 {
  font-size: 2rem;
  color: #2c7a4c;
  margin-bottom: 30px;
  font-weight: 600;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 15px;
}

.tech-tag {
  padding: 10px 20px;
  background-color: white;
  color: #4a90e2;
  border-radius: 25px;
  font-size: 0.9rem;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease;
}

.tech-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.user-scenarios {
  margin-bottom: 60px;
}

.scenarios-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.scenario-card {
  background-color: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-top: 4px solid #2c7a4c;
}

.scenario-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.scenario-icon {
  font-size: 3.5rem;
  margin-bottom: 20px;
  color: #4a90e2;
}

.scenario-card h3 {
  font-size: 1.5rem;
  color: #2c7a4c;
  margin-bottom: 15px;
  font-weight: 600;
}

.scenario-card p {
  color: #5a5a5a;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero h1 {
    font-size: 2.5rem;
  }
  
  .hero .tagline {
    font-size: 1.2rem;
  }
  
  .hero .description {
    font-size: 1rem;
  }
  
  .search-container {
    margin: 30px auto;
    padding: 0 15px;
  }
  
  .search-box {
    flex-direction: column;
    gap: 10px;
    padding: 12px;
  }
  
  .search-input {
    font-size: 1rem;
    padding: 10px 15px;
  }
  
  .search-btn {
    width: 100%;
    justify-content: center;
    padding: 10px 24px;
  }
  
  .core-values {
    flex-direction: column;
    gap: 20px;
  }
  
  .value-item {
    padding: 15px;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
  
  .feature-card {
    padding: 20px;
  }
  
  .scenarios-container {
    grid-template-columns: 1fr;
  }
  
  .scenario-card {
    padding: 20px;
  }
  
  .tech-stack h2 {
    font-size: 1.5rem;
  }
}

/* 提示文案样式 */
.notice-section {
  margin-bottom: 40px;
  text-align: center;
}

.notice-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  padding: 20px;
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.notice-icon {
  font-size: 1.6rem;
  flex-shrink: 0;
}

.notice-content {
  flex: 1;
  text-align: center;
}

.notice-content p {
  margin: 0;
  color: #856404;
  line-height: 1.2;
  font-size: 0.8rem;
}

.email-link {
  color: #4a90e2;
  text-decoration: none;
  font-weight: 500;
}

.email-link:hover {
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .notice-box {
    flex-direction: column;
    gap: 10px;
    padding: 15px;
  }
  
  .notice-icon {
    font-size: 1.5rem;
  }
  
  .notice-content p {
    font-size: 0.85rem;
    text-align: center;
  }
}
</style>
