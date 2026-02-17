import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 引入Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入ECharts
import * as echarts from 'echarts'

const app = createApp(App)

// 注册Element Plus
app.use(ElementPlus)

// 注册路由
app.use(router)

// 全局注册ECharts
app.config.globalProperties.$echarts = echarts

app.mount('#app')
