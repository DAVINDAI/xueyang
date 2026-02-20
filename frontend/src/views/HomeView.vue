<template>
  <div class="home">
    <div class="hero">
      <h1>欢迎使用 LangGraph Chat</h1>
      <p>一个基于大语言模型的智能聊天和数据分析平台</p>
    </div>
    
    <div class="features">
      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>统计信息</h3>
        <p>查看历史对话的统计数据，包括会话数量、消息数量、模型使用情况和每日消息趋势等。</p>
        <router-link to="/stats" class="btn">查看统计</router-link>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📋</div>
        <h3>详情查看</h3>
        <p>浏览和管理所有聊天会话，查看详细的对话内容和分析结果。</p>
        <router-link to="/details" class="btn">查看详情</router-link>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">💬</div>
        <h3>大模型聊天</h3>
        <p>使用GLM 5和Qwen Plus等先进大语言模型进行智能对话，支持上下文管理和自动压缩。</p>
        <router-link to="/chat" class="btn">开始聊天</router-link>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📄</div>
        <h3>简历优化</h3>
        <p>上传PDF简历，根据职位描述智能优化简历内容，提供面试准备建议，助你成功获得面试机会。</p>
        <router-link to="/resume" class="btn">优化简历</router-link>
      </div>
    </div>
    
    <div class="tech-stack">
      <h2>技术栈</h2>
      <div class="tech-tags">
        <span class="tech-tag">Vue 3</span>
        <span class="tech-tag">FastAPI</span>
        <span class="tech-tag">LangChain</span>
        <span class="tech-tag">SQLite</span>
        <span class="tech-tag">Element Plus</span>
        <span class="tech-tag">ECharts</span>
        <span class="tech-tag">Docker</span>
      </div>
    </div>
  </div>
</template>

<script setup>
// 首页组件
</script>

<style scoped>
.home {
  min-height: calc(100vh - 140px);
  padding: 40px 0;
}

.hero {
  text-align: center;
  margin-bottom: 60px;
}

.hero h1 {
  font-size: 3rem;
  color: #303133;
  margin-bottom: 20px;
}

.hero p {
  font-size: 1.2rem;
  color: #606266;
  margin-bottom: 40px;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 60px;
}

.feature-card {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 1.5rem;
  color: #303133;
  margin-bottom: 15px;
}

.feature-card p {
  color: #606266;
  margin-bottom: 25px;
  line-height: 1.6;
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #66b1ff;
}

.tech-stack {
  text-align: center;
  margin-top: 60px;
}

.tech-stack h2 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 30px;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 15px;
}

.tech-tag {
  padding: 8px 16px;
  background-color: #ecf5ff;
  color: #409eff;
  border-radius: 20px;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero h1 {
    font-size: 2rem;
  }
  
  .hero p {
    font-size: 1rem;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
  
  .feature-card {
    padding: 20px;
  }
  
  .tech-stack h2 {
    font-size: 1.5rem;
  }
}
</style>
