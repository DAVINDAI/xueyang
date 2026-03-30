<template>
  <div class="notes-page">
    <h1>笔记管理</h1>
    
    <div class="notes-container">
      <!-- 笔记列表 -->
      <div class="notes-list">
        <el-card v-if="notes.length === 0" class="empty-card">
          <div class="empty-content">
            <el-icon class="empty-icon"><Document /></el-icon>
            <p>暂无笔记，点击右侧按钮创建新笔记</p>
          </div>
        </el-card>
        
        <div v-else class="notes-grid">
          <el-card 
            v-for="note in notes" 
            :key="note.id"
            class="note-card"
            @click="editNote(note)"
          >
            <template #header>
              <div class="note-header">
                <h3>{{ note.title }}</h3>
                <span class="note-time">{{ formatTime(note.updatedAt) }}</span>
              </div>
            </template>
            
            <div class="note-preview">
              <div v-html="previewContent(note.content)"></div>
            </div>
            
            <div class="note-footer">
              <el-button link size="small" @click.stop="viewNote(note.id)">
                <el-icon><Document /></el-icon> 查看
              </el-button>
              <el-button link size="small" @click.stop="deleteNote(note.id)">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
              <el-button type="primary" size="small" @click.stop="editNote(note)">
                编辑
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
      
      <!-- 编辑器 -->
      <div class="editor-panel">
        <el-card class="editor-card">
          <template #header>
            <div class="editor-header">
              <h3>{{ editingNote ? '编辑笔记' : '创建笔记' }}</h3>
              <el-button type="success" @click="saveNote">
                {{ editingNote ? '保存' : '创建' }}
              </el-button>
            </div>
          </template>
          
          <div class="editor-content">
            <el-input
              v-model="form.title"
              placeholder="请输入笔记标题"
              class="title-input"
            />
            
            <div class="markdown-editor">
              <el-tabs v-model="activeTab">
                <el-tab-pane label="编辑">
                  <textarea
                    v-model="form.content"
                    placeholder="请输入笔记内容（支持Markdown格式）"
                    class="markdown-textarea"
                  ></textarea>
                </el-tab-pane>
                <el-tab-pane label="预览">
                  <div class="markdown-preview" v-html="renderMarkdown(form.content)"></div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { notesApi } from '../api'
import { Document, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

const notes = ref([])
const editingNote = ref(null)
const activeTab = ref('edit')

const form = ref({
  title: '',
  content: ''
})

// 加载笔记列表
const loadNotes = async () => {
  try {
    const data = await notesApi.listNotes()
    notes.value = data
  } catch (error) {
    console.error('加载笔记失败:', error)
    ElMessage.error(error.message || '加载笔记失败')
  }
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  try {
    return date.toLocaleString('zh-CN', {
      timeZone: 'Asia/Macau',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

// 预览内容（简单处理）
const previewContent = (content) => {
  if (!content) return ''
  // 简单的Markdown转HTML
  let preview = content
    .replace(/^# (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h4>$1</h4>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    .replace(/\n/g, '<br>')
  // 截取前100个字符
  return preview.length > 100 ? preview.substring(0, 100) + '...' : preview
}

// 渲染Markdown
const renderMarkdown = (content) => {
  if (!content) return ''
  // 简单的Markdown转HTML
  let html = content
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\(([^\)]+)\)/gim, '<a href="$2" target="_blank">$1</a>')
    .replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>')
    .replace(/^- (.*$)/gim, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
    .replace(/\n/g, '<br>')
  return html
}

// 保存笔记
const saveNote = async () => {
  if (!form.value.title) {
    ElMessage.warning('请输入笔记标题')
    return
  }
  
  try {
    if (editingNote.value) {
      // 更新笔记
      await notesApi.updateNote(editingNote.value.id, form.value.title, form.value.content)
      ElMessage.success('笔记更新成功')
    } else {
      // 创建笔记
      await notesApi.createNote(form.value.title, form.value.content)
      ElMessage.success('笔记创建成功')
    }
    
    // 重置表单
    resetForm()
    // 重新加载笔记列表
    await loadNotes()
  } catch (error) {
    console.error('保存笔记失败:', error)
    ElMessage.error(error.message || '保存笔记失败')
  }
}

// 查看笔记详情
const viewNote = (noteId) => {
  router.push(`/notes/${noteId}`)
}

// 编辑笔记
const editNote = (note) => {
  editingNote.value = note
  form.value.title = note.title
  form.value.content = note.content
  activeTab.value = 'edit'
}

// 删除笔记
const deleteNote = async (noteId) => {
  try {
    await notesApi.deleteNote(noteId)
    ElMessage.success('笔记删除成功')
    // 重新加载笔记列表
    await loadNotes()
    // 如果正在编辑被删除的笔记，重置表单
    if (editingNote.value && editingNote.value.id === noteId) {
      resetForm()
    }
  } catch (error) {
    console.error('删除笔记失败:', error)
    ElMessage.error(error.message || '删除笔记失败')
  }
}

// 重置表单
const resetForm = () => {
  editingNote.value = null
  form.value.title = ''
  form.value.content = ''
  activeTab.value = 'edit'
}

// 生命周期钩子
onMounted(() => {
  loadNotes()
})
</script>

<style scoped>
.notes-page {
  padding: 0;
  margin: 0 -20px;
  width: calc(100% + 40px);
}

.notes-page h1 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 30px;
  padding: 0 20px;
}

.notes-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.notes-list {
  grid-column: 1;
}

.editor-panel {
  grid-column: 2;
}

.notes-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.note-card {
  cursor: pointer;
  transition: all 0.3s;
}

.note-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.note-header h3 {
  font-size: 1.1rem;
  font-weight: 500;
  color: #303133;
  margin: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.note-time {
  font-size: 0.8rem;
  color: #909399;
  margin-left: 10px;
}

.note-preview {
  margin: 15px 0;
  line-height: 1.6;
  color: #606266;
  min-height: 80px;
}

.note-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.empty-card {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.empty-content {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.empty-content p {
  color: #909399;
}

.editor-card {
  height: 100%;
  min-height: 600px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-header h3 {
  font-size: 1.1rem;
  font-weight: 500;
  color: #303133;
  margin: 0;
}

.editor-content {
  margin-top: 20px;
}

.title-input {
  margin-bottom: 20px;
}

.markdown-editor {
  height: 500px;
}

.markdown-textarea {
  width: 100%;
  height: 450px;
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: none;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.6;
}

.markdown-textarea:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.markdown-preview {
  width: 100%;
  height: 450px;
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow-y: auto;
  line-height: 1.6;
}

.markdown-preview h1 {
  font-size: 1.5rem;
  margin: 20px 0 10px 0;
  padding: 0;
}

.markdown-preview h2 {
  font-size: 1.3rem;
  margin: 15px 0 8px 0;
  padding: 0;
}

.markdown-preview h3 {
  font-size: 1.1rem;
  margin: 12px 0 6px 0;
  padding: 0;
}

.markdown-preview pre {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 10px 0;
}

.markdown-preview code {
  background-color: #f5f7fa;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.9rem;
}

.markdown-preview ul {
  margin: 10px 0;
  padding-left: 20px;
}

.markdown-preview li {
  margin-bottom: 4px;
}

.markdown-preview a {
  color: #409eff;
  text-decoration: none;
}

.markdown-preview a:hover {
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .notes-container {
    grid-template-columns: 1fr;
  }
  
  .notes-list,
  .editor-panel {
    grid-column: 1;
  }
  
  .editor-card {
    min-height: 500px;
  }
  
  .markdown-editor {
    height: 400px;
  }
  
  .markdown-textarea,
  .markdown-preview {
    height: 350px;
  }
}

@media (max-width: 768px) {
  .notes-page h1 {
    font-size: 1.5rem;
  }
  
  .notes-container {
    padding: 0 10px;
  }
  
  .note-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .note-footer {
    flex-direction: column;
    align-items: stretch;
  }
  
  .editor-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
}
</style>