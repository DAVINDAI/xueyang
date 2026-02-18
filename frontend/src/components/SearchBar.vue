<template>
  <div class="search-bar">
    <div class="search-input-container">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="搜索内容..."
        class="search-input"
        @keyup.enter="handleSearch"
      />
      <button class="search-button" @click="handleSearch">
        搜索
      </button>
    </div>
    <div v-if="searchResults.length > 0" class="search-results">
      <h3>搜索结果</h3>
      <ul>
        <li v-for="(result, index) in searchResults" :key="index">
          <a :href="result.url" target="_blank">{{ result.title }}</a>
          <p>{{ result.content }}</p>
        </li>
      </ul>
    </div>
    <div v-if="loading" class="search-loading">
      搜索中...
    </div>
    <div v-if="error" class="search-error">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api/index.js';

const searchQuery = ref('');
const searchResults = ref([]);
const loading = ref(false);
const error = ref('');

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    return;
  }
  
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
  padding: 16px;
  z-index: 1000;
  max-height: 400px;
  overflow-y: auto;
}

.search-results h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
}

.search-results ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.search-results li {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.search-results li:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.search-results a {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
}

.search-results a:hover {
  text-decoration: underline;
}

.search-results p {
  color: #606266;
  font-size: 12px;
  margin: 0;
  line-height: 1.4;
}

.search-loading {
  margin-top: 8px;
  color: #909399;
  font-size: 14px;
}

.search-error {
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