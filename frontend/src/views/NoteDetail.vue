<template>
  <div class="note-detail-page">
    <div class="page-header">
      <el-button type="text" @click="goBack" class="back-btn">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <div class="header-actions">
        <el-button type="primary" @click="editNote">
          <el-icon><Edit /></el-icon> 编辑
        </el-button>
        <el-button type="danger" @click="deleteNote">
          <el-icon><Delete /></el-icon> 删除
        </el-button>
      </div>
    </div>

    <div class="note-content" v-loading="loading">
      <template v-if="note">
        <h1 class="note-title">{{ note.title }}</h1>
        <div class="note-meta">
          <span class="meta-item">
            <el-icon><Clock /></el-icon>
            更新于：{{ formatTime(note.updatedAt) }}
          </span>
          <span class="meta-item" v-if="note.createdAt">
            <el-icon><Calendar /></el-icon>
            创建于：{{ formatTime(note.createdAt) }}
          </span>
        </div>
        <div class="note-body markdown-body" v-html="renderMarkdown(note.content)"></div>
      </template>
      <el-empty v-else-if="!loading" description="笔记不存在" />
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editingNote ? '编辑笔记' : '创建笔记'"
      width="800px"
      top="5vh"
    >
      <div class="edit-dialog-content">
        <el-input
          v-model="editForm.title"
          placeholder="请输入笔记标题"
          class="edit-title-input"
        />
        
        <div class="edit-markdown-editor">
          <el-tabs v-model="editActiveTab">
            <el-tab-pane label="编辑">
              <textarea
                v-model="editForm.content"
                placeholder="请输入笔记内容（支持 Markdown 格式）"
                class="edit-markdown-textarea"
              ></textarea>
            </el-tab-pane>
            <el-tab-pane label="预览">
              <div class="edit-markdown-preview" v-html="renderMarkdown(editForm.content)"></div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { notesApi } from '../api'
import { ArrowLeft, Edit, Delete, Clock, Calendar } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

const note = ref(null)
const loading = ref(true)
const editDialogVisible = ref(false)
const editingNote = ref(null)
const editActiveTab = ref('edit')

const editForm = ref({
  title: '',
  content: ''
})

// 加载笔记详情
const loadNote = async () => {
  try {
    loading.value = true
    const data = await notesApi.getNote(route.params.id)
    note.value = data
  } catch (error) {
    console.error('加载笔记失败:', error)
    ElMessage.error('加载笔记失败')
  } finally {
    loading.value = false
  }
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  try {
    return date.toLocaleString('zh-CN', {
      timeZone: 'Asia/Macau',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

// 渲染 Markdown
const renderMarkdown = (content) => {
  if (!content) return ''
  
  // 转义 HTML 特殊字符
  let html = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // 代码块（必须在其他规则之前处理）
  html = html.replace(/```(\w*)\n?([\s\S]*?)```/gim, (match, lang, code) => {
    return `<pre class="code-block"><code class="language-${lang}">${code.trim()}</code></pre>`
  })
  
  // 行内代码
  html = html.replace(/`([^`]+)`/gim, '<code class="inline-code">$1</code>')
  
  // 标题
  html = html
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
    .replace(/^##### (.*$)/gim, '<h5>$1</h5>')
    .replace(/^###### (.*$)/gim, '<h6>$1</h6>')
  
  // 粗体和斜体
  html = html
    .replace(/\*\*\*(.*)\*\*\*/gim, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    .replace(/~~(.*)~~/gim, '<del>$1</del>')
  
  // 链接和图片
  html = html
    .replace(/!\[([^\]]*)\]\(([^\)]+)\)/gim, '<img src="$2" alt="$1" class="markdown-image">')
    .replace(/\[([^\]]+)\]\(([^\)]+)\)/gim, '<a href="$2" target="_blank" class="markdown-link">$1</a>')
  
  // 引用
  html = html.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
  
  // 无序列表
  html = html.replace(/^[-*+] (.*$)/gim, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
  
  // 有序列表
  html = html.replace(/^\d+\. (.*$)/gim, '<ol><li>$1</li></ol>')
  
  // 分割线
  html = html.replace(/^---$/gim, '<hr>')
  
  // 换行
  html = html.replace(/\n/g, '<br>')
  
  // 清理多余的空白标签
  html = html.replace(/<br><\/li>/g, '</li>')
  html = html.replace(/<br><\/blockquote>/g, '</blockquote>')
  
  return html
}

// 返回列表页
const goBack = () => {
  router.push('/notes')
}

// 编辑笔记
const editNote = () => {
  if (!note.value) return
  editingNote.value = note.value
  editForm.value.title = note.value.title
  editForm.value.content = note.value.content
  editDialogVisible.value = true
  editActiveTab.value = 'edit'
}

// 保存编辑
const saveEdit = async () => {
  if (!editForm.value.title) {
    ElMessage.warning('请输入笔记标题')
    return
  }
  
  try {
    await notesApi.updateNote(editingNote.value.id, editForm.value.title, editForm.value.content)
    ElMessage.success('笔记更新成功')
    editDialogVisible.value = false
    await loadNote()
  } catch (error) {
    console.error('更新笔记失败:', error)
    ElMessage.error('更新笔记失败')
  }
}

// 删除笔记
const deleteNote = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这篇笔记吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await notesApi.deleteNote(note.value.id)
    ElMessage.success('笔记删除成功')
    router.push('/notes')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除笔记失败:', error)
      ElMessage.error('删除笔记失败')
    }
  }
}

// 生命周期钩子
onMounted(() => {
  loadNote()
})
</script>

<style scoped>
.note-detail-page {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.back-btn {
  font-size: 14px;
  padding: 8px 12px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.note-content {
  background: #fff;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.note-title {
  font-size: 2rem;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
  line-height: 1.4;
}

.note-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
}

.meta-item .el-icon {
  font-size: 14px;
}

.note-body {
  font-size: 16px;
  line-height: 1.8;
  color: #303133;
}

/* Markdown 样式 */
.markdown-body {
  word-wrap: break-word;
}

.markdown-body h1 {
  font-size: 2rem;
  margin: 30px 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
  color: #303133;
}

.markdown-body h2 {
  font-size: 1.6rem;
  margin: 25px 0 15px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
  color: #303133;
}

.markdown-body h3 {
  font-size: 1.3rem;
  margin: 20px 0 12px 0;
  color: #303133;
}

.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  font-size: 1.1rem;
  margin: 15px 0 10px 0;
  color: #303133;
}

.markdown-body p {
  margin: 15px 0;
}

.markdown-body strong {
  font-weight: 600;
  color: #303133;
}

.markdown-body em {
  font-style: italic;
  color: #606266;
}

.markdown-body del {
  text-decoration: line-through;
  color: #909399;
}

.markdown-body a {
  color: #409eff;
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}

.markdown-body ul,
.markdown-body ol {
  margin: 15px 0;
  padding-left: 30px;
}

.markdown-body li {
  margin: 8px 0;
  line-height: 1.6;
}

.markdown-body blockquote {
  margin: 20px 0;
  padding: 15px 20px;
  background-color: #f5f7fa;
  border-left: 4px solid #409eff;
  color: #606266;
  border-radius: 0 4px 4px 0;
}

.markdown-body pre {
  margin: 20px 0;
  padding: 0;
  background-color: #282c34;
  border-radius: 6px;
  overflow: hidden;
}

.markdown-body pre code {
  display: block;
  padding: 20px;
  overflow-x: auto;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #abb2bf;
}

.markdown-body .inline-code {
  padding: 3px 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 0.9em;
  color: #e74c3c;
}

.markdown-body .markdown-image {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  margin: 20px 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.markdown-body hr {
  margin: 30px 0;
  border: none;
  border-top: 2px solid #ebeef5;
}

/* 编辑对话框 */
.edit-dialog-content {
  padding: 10px 0;
}

.edit-title-input {
  margin-bottom: 20px;
}

.edit-markdown-editor {
  height: 500px;
}

.edit-markdown-textarea {
  width: 100%;
  height: 450px;
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: none;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.edit-markdown-textarea:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.edit-markdown-preview {
  width: 100%;
  height: 450px;
  padding: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow-y: auto;
  line-height: 1.8;
  background-color: #fafafa;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .note-detail-page {
    padding: 15px;
  }
  
  .note-content {
    padding: 25px 20px;
  }
  
  .note-title {
    font-size: 1.5rem;
  }
  
  .note-meta {
    flex-direction: column;
    gap: 10px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .header-actions .el-button {
    flex: 1;
  }
}
</style>
