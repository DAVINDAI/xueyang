<template>
  <div class="app">
    <header class="app-header">
      <img src="/xy1000.png" alt="Logo" class="logo" />
      <nav class="nav">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/chat" class="nav-link">对话<br>连接</router-link>
        <router-link to="/law" class="nav-link">法律<br>助手</router-link>
        <router-link to="/assistant" class="nav-link">协助<br>助手</router-link>
        <router-link to="/communication" class="nav-link">沟通<br>助手</router-link>
        <router-link to="/coding-playground" class="nav-link">编码<br>操场</router-link>
        <router-link to="/notes" class="nav-link">笔记<br>管理</router-link>
        <router-link to="/memo" class="nav-link">备忘<br>录</router-link>
        <router-link to="/resume" class="nav-link">简历<br>优化</router-link>
        <router-link to="/resume/list" class="nav-link">优化<br>历史</router-link>
        <router-link to="/details" class="nav-link">学习<br>详情</router-link>
      </nav>
      <SearchBar />
      <div v-if="isUserLoggedIn" class="user-info">
        <span class="user-phone">{{ username }}</span>
        <el-button type="danger" size="small" @click="handleLogout">注销</el-button>
      </div>
      <div v-else class="login-btn">
        <router-link to="/login" class="nav-link">管理员登录</router-link>
      </div>
    </header>
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade"  mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer class="app-footer">
      <p>© 2026 学氧助手. All rights reserved.</p>
      <p class="beian">
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">浙ICP备2026013828号-1</a>
      </p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import SearchBar from './components/SearchBar.vue';
import { authApi } from './api';

const router = useRouter();
const route = useRoute();
const username = ref('');

// 使用ref来存储登录状态，以便手动更新
const loginStatus = ref(authApi.isLoggedIn());
const isUserLoggedIn = computed(() => loginStatus.value);
const isHomePage = computed(() => route.path === '/');

const getUsername = () => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      username.value = payload.sub || '';
    } catch (error) {
      console.error('解析token失败:', error);
    }
  }
};

const handleLogout = () => {
  authApi.logout();
  username.value = '';
  // 更新登录状态
  loginStatus.value = authApi.isLoggedIn();
  ElMessage.success('注销成功');
  router.push('/login');
};

// 监听路由变化，在路由跳转后重新获取用户名和登录状态
watch(() => route.path, () => {
  // 更新登录状态
  loginStatus.value = authApi.isLoggedIn();
  if (isUserLoggedIn.value) {
    getUsername();
  }
});

onMounted(() => {
  // 更新登录状态
  loginStatus.value = authApi.isLoggedIn();
  if (isUserLoggedIn.value) {
    getUsername();
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
  gap: 8px;
  flex: 1;
  margin: 0 10px;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-start;
}

.search-bar {
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 15px;
  border-left: 1px solid rgba(255, 255, 255, 0.2);
}

.user-phone {
  color: white;
  font-size: 14px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 6px 10px;
  transition: all 0.3s ease;
  font-size: 14px;
  display: inline-flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 2px;
  width: 58px;
  height: 40px;
  white-space: normal;
  margin: 0;
  line-height: 1.2;
  position: relative;
}

.nav-link:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 30%;
  bottom: 30%;
  width: 1.5px;
  background-color: rgba(255, 255, 255, 0.3);
}

/* 针对不同长度的导航项进行特殊处理 */
/* 所有导航项统一宽度为58px */

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
  border-radius: 4px;
}

.router-link-active {
  background-color: rgba(255, 255, 255, 0.15);
  font-weight: 600;
  border-radius: 4px;
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

.app-footer .beian {
  margin-top: 8px;
  font-size: 12px;
}

.app-footer .beian a {
  color: #909399;
  text-decoration: none;
}

.app-footer .beian a:hover {
  color: #fff;
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
    gap: 6px;
    margin: 5px 0;
    order: 3;
    width: 100%;
    justify-content: flex-start;
  }
  
  .nav-link {
    padding: 4px 8px;
    font-size: 13px;
    height: 36px;
    width: 58px;
    gap: 2px;
    line-height: 1.2;
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
