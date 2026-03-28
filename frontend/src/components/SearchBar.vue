<template>
  <div class="search-bar" ref="searchBarRef">
    <div class="search-input-container">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="搜索内容..."
        class="search-input"
        @keyup.enter="handleSearch"
        @focus="isFocused = true"
      />
      <button class="search-button" @click="handleSearch">
        搜索
      </button>
    </div>
    <div v-if="isFocused && searchResults.length > 0" class="search-results">
      <div v-if="semanticResults.length > 0">
        <h3 class="results-header semantic-header">
          <el-icon><ChatDotRound /></el-icon> 语义搜索
        </h3>
        <ul>
          <li v-for="(result, index) in semanticResults" :key="`semantic-${index}`" class="result-item semantic-result" @click="jumpToChat(result.sessionId, result.messageId)">
            <div class="result-title">{{ result.title }}</div>
            <p class="result-content">{{ result.content }}</p>
            <div class="result-meta">
              <span class="result-time">{{ formatTime(result.createdAt) }}</span>
              <span v-if="result.score" class="result-score">相似度: {{ (result.score * 100).toFixed(1) }}%</span>
            </div>
          </li>
        </ul>
      </div>
      <div v-if="localResults.length > 0">
        <h3 class="results-header local-header">
          <el-icon><ChatDotRound /></el-icon> 本地聊天记录
        </h3>
        <ul>
          <li v-for="(result, index) in localResults" :key="`local-${index}`" class="result-item local-result" @click="jumpToChat(result.sessionId, result.messageId)">
            <div class="result-title">{{ result.title }}</div>
            <p class="result-content">{{ result.content }}</p>
            <span class="result-time">{{ formatTime(result.createdAt) }}</span>
          </li>
        </ul>
      </div>
      <div v-if="webResults.length > 0">
        <h3 class="results-header web-header">
          <el-icon><Connection /></el-icon> 网络搜索
        </h3>
        <ul>
          <li v-for="(result, index) in webResults" :key="`web-${index}`" class="result-item web-result">
            <a :href="result.url" target="_blank" class="result-title">{{ result.title }}</a>
            <p class="result-content">{{ result.content }}</p>
          </li>
        </ul>
      </div>
    </div>
    <div v-if="isFocused && loading" class="search-loading">
      搜索中...
    </div>
    <div v-if="isFocused && error" class="search-error">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import { ChatDotRound, Connection } from '@element-plus/icons-vue';

const router = useRouter();
const searchBarRef = ref(null);
const searchQuery = ref('良法善治');
const searchResults = ref([]);
const loading = ref(false);
const error = ref('');
const isFocused = ref(false);

const semanticResults = computed(() => {
  return searchResults.value.filter(r => r.type === 'semantic');
});

const localResults = computed(() => {
  return searchResults.value.filter(r => r.type === 'local');
});

const webResults = computed(() => {
  return searchResults.value.filter(r => r.type === 'web');
});

const formatTime = (timeStr) => {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  try {
    return date.toLocaleString('zh-CN', {
      timeZone: 'Asia/Macau',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    return date.toLocaleString('zh-CN');
  }
};

const jumpToChat = (sessionId, messageId) => {
  isFocused.value = false;
  router.push({
    path: '/chat',
    query: { sessionId, messageId }
  });
};

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    return;
  }
  
  // 确保搜索结果区域显示
  isFocused.value = true;
  loading.value = true;
  error.value = '';
  
  try {
    const response = await api.search(searchQuery.value);
    searchResults.value = response.results || [];
  } catch (err) {
    error.value = '搜索失败，请重试';
    console.error('Search error:', err);
  } finally {
    loading.value = false;
  }
};

const handleClickOutside = (event) => {
  if (searchBarRef.value && !searchBarRef.value.contains(event.target)) {
    isFocused.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.search-bar {
  position: relative;
  width: 100%;
  max-width: 400px;
}

.search-input-container {
  display: flex;
  width: 100%;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px 0 0 4px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #409eff;
}

.search-button {
  padding: 0 16px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-button:hover {
  background-color: #66b1ff;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  background-color: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 12px 16px;
  z-index: 1000;
  max-height: 500px;
  overflow-y: auto;
}

.results-header {
  margin: 8px 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.semantic-header {
  color: #e6a23c;
}

.local-header {
  color: #67c23a;
}

.web-header {
  color: #409eff;
}

.search-results ul {
  list-style: none;
  padding: 0;
  margin: 0 0 16px 0;
}

.search-results ul:last-child {
  margin-bottom: 0;
}

.result-item {
  margin-bottom: 12px;
  padding: 10px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.result-item:last-child {
  margin-bottom: 0;
}

.semantic-result {
  background-color: #fdf6ec;
  cursor: pointer;
}

.semantic-result:hover {
  background-color: #faecd8;
}

.local-result {
  background-color: #f0f9eb;
  cursor: pointer;
}

.local-result:hover {
  background-color: #e1f3d8;
}

.web-result {
  background-color: #ecf5ff;
}

.result-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
  color: #303133;
}

.web-result .result-title {
  color: #409eff;
  text-decoration: none;
}

.web-result .result-title:hover {
  text-decoration: underline;
}

.result-content {
  color: #606266;
  font-size: 12px;
  margin: 0 0 6px 0;
  line-height: 1.5;
}

.result-time {
  font-size: 11px;
  color: #909399;
}

.result-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
}

.result-score {
  font-size: 11px;
  color: #e6a23c;
  font-weight: 500;
}

.search-loading {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  color: #909399;
  font-size: 14px;
}

.search-error {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  color: #f56c6c;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-bar {
    max-width: 300px;
  }
  
  .search-input {
    font-size: 13px;
    padding: 6px 10px;
  }
  
  .search-button {
    padding: 0 12px;
    font-size: 13px;
  }
}
</style>