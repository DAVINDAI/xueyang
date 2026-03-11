<template>
  <div class="app">
    <header class="app-header">
      <img src="/xy.png" alt="Logo" class="logo" />
      <nav class="nav">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/chat" class="nav-link">对话连接</router-link>
        <router-link to="/stats" class="nav-link">统计信息</router-link>
        <router-link to="/details" class="nav-link">详情查看</router-link>
        <router-link to="/notes" class="nav-link">笔记管理</router-link>
        <router-link to="/memo" class="nav-link">备忘录</router-link>
        <router-link to="/resume" class="nav-link">简历优化</router-link>
        <router-link to="/resume/list" class="nav-link">优化历史</router-link>
      </nav>
      <SearchBar />
      <div v-if="isLoggedIn" class="user-info">
        <span class="user-phone">{{ userPhone }}</span>
        <el-button type="danger" size="small" @click="handleLogout">注销</el-button>
      </div>
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
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import SearchBar from './components/SearchBar.vue';
import { logout, isLoggedIn } from './api/authApi';

const router = useRouter();
const userPhone = ref('');

const isUserLoggedIn = computed(() => isLoggedIn());

const getUserPhone = () => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      userPhone.value = payload.sub || '';
    } catch (error) {
      console.error('解析token失败:', error);
    }
  }
};

const handleLogout = () => {
  logout();
  userPhone.value = '';
  ElMessage.success('注销成功');
  router.push('/login');
};

onMounted(() => {
  if (isUserLoggedIn.value) {
    getUserPhone();
  }
});
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
  background-color: #90EE90;
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
  flex: 1;
  margin: 0 20px;
}

.search-bar {
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 20px;
  border-left: 1px solid rgba(255, 255, 255, 0.2);
}

.user-phone {
  color: white;
  font-size: 14px;
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
    flex-wrap: wrap;
    height: auto;
    min-height: 60px;
    padding: 10px;
  }
  
  .nav {
    gap: 10px;
    margin: 10px 0;
    order: 3;
    width: 100%;
    justify-content: center;
  }
  
  .nav-link {
    padding: 6px 12px;
    font-size: 14px;
  }
  
  .search-bar {
    order: 2;
    max-width: 300px;
  }
  
  .app-main {
    padding: 10px;
  }
}
</style>
