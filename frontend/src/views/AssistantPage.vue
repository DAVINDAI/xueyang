<template>
  <div class="assistant-page">
    <h1>协助助手</h1>
    
    <!-- 顶部区域：Markdown编辑器和创建任务按钮 -->
    <div class="top-section">
      <div class="editor-container">
        <h2>目标设定</h2>
        <div class="form-group">
          <label for="goal-title">目标标题</label>
          <input 
            type="text" 
            id="goal-title" 
            v-model="newGoal.title" 
            placeholder="输入目标标题"
            class="form-control"
          />
        </div>
        <div class="form-group">
          <label for="goal-description">目标描述</label>
          <textarea 
            id="goal-description" 
            v-model="newGoal.description" 
            placeholder="输入目标描述（Markdown格式）"
            class="form-control markdown-editor"
            rows="6"
          ></textarea>
        </div>
        <button 
          @click="createGoal" 
          class="btn btn-primary"
          :disabled="!newGoal.title || !newGoal.description"
        >
          创建任务
        </button>
      </div>
      
      <!-- 用户列表 -->
      <div class="users-container">
        <h2>相关人员</h2>
        <div class="user-list">
          <div 
            v-for="user in users" 
            :key="user.username"
            class="user-item"
          >
            <div class="user-info">
              <span class="username">{{ user.username }}</span>
              <span class="user-role">{{ user.role }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部区域：任务列表 -->
    <div class="bottom-section">
      <h2>任务列表</h2>
      <div class="task-filters">
        <select v-model="taskFilter" class="form-control">
          <option value="all">所有任务</option>
          <option value="my">我的任务</option>
        </select>
      </div>
      <div class="tasks-container">
        <div 
          v-for="task in filteredTasks" 
          :key="task.id"
          class="task-item"
          :class="{ 'task-high': task.priority === '高', 'task-medium': task.priority === '中', 'task-low': task.priority === '低' }"
        >
          <div class="task-header">
            <h3>{{ task.title }}</h3>
            <div class="task-meta">
              <span class="task-assignee">{{ task.assigneeRole }} - {{ task.assignee }}</span>
              <span class="task-priority">{{ task.priority }}</span>
            </div>
          </div>
          <div class="task-description">{{ task.description }}</div>
          <div class="task-footer">
            <select 
              v-model="task.status" 
              @change="updateTaskStatus(task.id, task.status)"
              class="form-control status-select"
            >
              <option value="待处理">待处理</option>
              <option value="进行中">进行中</option>
              <option value="已完成">已完成</option>
            </select>
            <span class="task-created">{{ formatDate(task.createdAt) }}</span>
          </div>
        </div>
        <div v-if="filteredTasks.length === 0" class="no-tasks">
          暂无任务
        </div>
      </div>
    </div>
    
    <!-- 目标列表 -->
    <div class="goals-section">
      <h2>目标列表</h2>
      <div class="goals-container">
        <div 
          v-for="goal in goals" 
          :key="goal.id"
          class="goal-item"
          :class="{ 'goal-completed': goal.status === '已分解' }"
        >
          <div class="goal-header">
            <h3>{{ goal.title }}</h3>
            <span class="goal-status">{{ goal.status }}</span>
          </div>
          <div class="goal-meta">
            <span class="goal-creator">创建人：{{ goal.createdBy }}</span>
            <span class="goal-date">{{ formatDate(goal.createdAt) }}</span>
          </div>
          <div class="goal-actions">
            <button 
              v-if="goal.status === '待分解' && userRole === '总裁'"
              @click="decomposeGoal(goal.id)"
              class="btn btn-success"
            >
              分解目标
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { assistantApi } from '../api'

export default {
  name: 'AssistantPage',
  data() {
    return {
      newGoal: {
        title: '',
        description: ''
      },
      goals: [],
      tasks: [],
      users: [],
      taskFilter: 'all',
      userRole: ''
    }
  },
  computed: {
    filteredTasks() {
      if (this.taskFilter === 'my') {
        const currentUser = localStorage.getItem('username')
        return this.tasks.filter(task => task.assignee === currentUser)
      }
      return this.tasks
    }
  },
  mounted() {
    this.loadData()
    this.getUserRole()
  },
  methods: {
    async loadData() {
      try {
        console.log('开始加载数据')
        // 加载用户列表
        const usersData = await assistantApi.getUsers()
        console.log('用户列表数据:', usersData)
        this.users = usersData
        
        // 加载目标列表
        const goalsData = await assistantApi.getGoals()
        console.log('目标列表数据:', goalsData)
        this.goals = goalsData
        
        // 加载任务列表
        const tasksData = await assistantApi.getTasks()
        console.log('任务列表数据:', tasksData)
        this.tasks = tasksData
      } catch (error) {
        console.error('加载数据失败:', error)
      }
    },
    
    getUserRole() {
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      this.userRole = userInfo.role || ''
    },
    
    async createGoal() {
      try {
        await assistantApi.createGoal(this.newGoal)
        this.newGoal = { title: '', description: '' }
        await this.loadData()
        alert('目标创建成功！')
      } catch (error) {
        console.error('创建目标失败:', error)
        alert('创建目标失败，请重试')
      }
    },
    
    async decomposeGoal(goalId) {
      try {
        const result = await assistantApi.decomposeGoal(goalId)
        await this.loadData()
        alert(`目标分解成功，生成了 ${result.taskCount} 个任务`)
      } catch (error) {
        console.error('分解目标失败:', error)
        alert('分解目标失败，请重试')
      }
    },
    
    async updateTaskStatus(taskId, status) {
      try {
        await assistantApi.updateTaskStatus(taskId, status)
        // 刷新任务列表
        const tasksData = await assistantApi.getTasks()
        this.tasks = tasksData
      } catch (error) {
        console.error('更新任务状态失败:', error)
        alert('更新任务状态失败，请重试')
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString()
    }
  }
}
</script>

<style scoped>
.assistant-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.top-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.editor-container {
  max-width: 800px;
}

.users-container {
  max-width: 400px;
}

.users-container h2 {
  margin-top: 0;
}

.user-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.user-item {
  background: white;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.user-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-role {
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.form-group {
  margin-bottom: 15px;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.markdown-editor {
  font-family: 'Courier New', monospace;
  resize: vertical;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.users-container {
  max-width: 400px;
}

.users-container h2 {
  margin-top: 0;
}

.bottom-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.task-filters {
  margin-bottom: 15px;
}

.tasks-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.task-item {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-left: 4px solid #6c757d;
}

.task-high {
  border-left-color: #dc3545;
}

.task-medium {
  border-left-color: #ffc107;
}

.task-low {
  border-left-color: #28a745;
}

.task-header {
  margin-bottom: 10px;
}

.task-header h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.task-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

.task-description {
  margin-bottom: 10px;
  font-size: 14px;
  line-height: 1.4;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #666;
}

.status-select {
  width: 100px;
  font-size: 12px;
}

.no-tasks {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  color: #666;
  background: white;
  border-radius: 8px;
}

.goals-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.goals-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-top: 10px;
}

.goal-item {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.goal-completed {
  border-left: 4px solid #28a745;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.goal-header h3 {
  margin: 0;
  font-size: 16px;
}

.goal-status {
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.goal-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
}

.goal-actions {
  margin-top: 10px;
}
</style>