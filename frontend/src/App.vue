<template>
  <div class="app">
    <header class="app-header">
      <img src="/xy.png" alt="Logo" class="logo" />
      <nav class="nav">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/stats" class="nav-link">统计信息</router-link>
        <router-link to="/details" class="nav-link">详情查看</router-link>
        <router-link to="/chat" class="nav-link">大模型聊天</router-link>
        <router-link to="/memo" class="nav-link">备忘录</router-link>
      </nav>
    </header>
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer class="app-footer">
      <p>© 2026 LangGraph Chat. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup>
// App组件
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f5f5;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: #409eff;
  color: white;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo {
  height: 48px;
  width: auto;
  object-fit: contain;
}

.nav {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 500;
}

.app-main {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  background-color: #303133;
  color: #909399;
  text-align: center;
  padding: 20px;
  margin-top: auto;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 10px;
  }
  
  .nav {
    gap: 10px;
  }
  
  .nav-link {
    padding: 6px 12px;
    font-size: 14px;
  }
  
  .app-main {
    padding: 10px;
  }
}
</style>
