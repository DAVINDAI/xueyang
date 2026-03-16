<template>
  <div class="home">
    <div class="hero">
      <h1>学氧学习助手</h1>
      <p class="tagline">让学习像呼吸一样自然</p>
      <p class="description">我们致力于通过人工智能技术，为每一位学习者提供个性化、智能化的学习支持，成为您的终身学习伙伴。</p>
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
import { evolutionApi } from '../api/index.js'
import { Refresh } from '@element-plus/icons-vue'
import { marked } from 'marked'

// 响应式数据
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
</style>
