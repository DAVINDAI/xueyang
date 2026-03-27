<template>
  <div class="law-page">
    <h1>法律文档</h1>
    
    <div class="law-docs-container">
      <div v-if="loading" class="loading">
        <el-icon><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      
      <el-table v-else :data="lawDocs" style="width: 100%" :fit="true">
        <el-table-column prop="filename" label="文件名" min-width="200">
          <template #default="scope">
            <span class="filename">{{ scope.row.filename }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="文件大小" min-width="100">
          <template #default="scope">
            <span>{{ formatFileSize(scope.row.file_size) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="150">
          <template #default="scope">
            <span>{{ formatDate(scope.row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="100">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleDownload(scope.row.filename)">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Loading, Document, Download } from '@element-plus/icons-vue';
import { getAvailableLawDocs, downloadLawDoc } from '../api/lawApi';

const lawDocs = ref([]);
const loading = ref(true);

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 格式化日期
const formatDate = (timestamp) => {
  const date = new Date(timestamp * 1000);
  return date.toLocaleString();
};

// 处理下载
const handleDownload = (filename) => {
  try {
    downloadLawDoc(filename);
    ElMessage.success('开始下载法律文档');
  } catch (error) {
    ElMessage.error('下载失败，请重试');
  }
};

// 加载法律文档列表
const loadLawDocs = async () => {
  loading.value = true;
  try {
    const docs = await getAvailableLawDocs();
    lawDocs.value = docs;
  } catch (error) {
    ElMessage.error('获取法律文档列表失败');
    console.error('获取法律文档列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 组件挂载时加载数据
onMounted(() => {
  loadLawDocs();
});
</script>

<style scoped>
.law-page {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.law-page h1 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

.law-docs-container {
  width: 100%;
}

.loading, .empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #999;
}

.loading span, .empty span {
  margin-left: 10px;
}

.filename {
  font-weight: 500;
  color: #333;
}

.el-table {
  margin-top: 20px;
  width: 100% !important;
  border-radius: 8px;
  overflow: hidden;
}

.el-table__body {
  table-layout: auto !important;
  width: 100% !important;
}

/* 美化表头 */
.el-table th {
  background-color: #f5f7fa !important;
  font-weight: 600 !important;
  color: #333 !important;
  height: 48px !important;
  text-align: center !important;
}

/* 美化表格行 */
.el-table td {
  height: 48px !important;
  text-align: center !important;
  vertical-align: middle !important;
}

/* 美化表格行 hover 效果 */
.el-table__row:hover {
  background-color: #f0f9ff !important;
}

/* 美化下载按钮 */
.el-button--primary {
  background-color: #409eff !important;
  border-color: #409eff !important;
}

.el-button--primary:hover {
  background-color: #66b1ff !important;
  border-color: #66b1ff !important;
}

/* 美化文件名显示 */
.filename {
  font-weight: 500;
  color: #333;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .law-page {
    padding: 10px;
  }
  
  .law-page h1 {
    font-size: 20px;
  }
  
  .loading, .empty {
    padding: 20px;
  }
}
</style>
