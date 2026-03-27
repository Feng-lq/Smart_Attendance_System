// web_client/src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// UI Framework & Styles / UI 框架与核心样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import '@/assets/global.css' 

// Icons / 全局图标库
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

// Critical Sequence: Pinia MUST be registered before Router
// 核心时序：必须在 router 之前挂载 Pinia。
app.use(createPinia())

app.use(router)
app.use(ElementPlus)

// Globally register all Element Plus icons for development agility
// 遍历并全局注册所有 Element Plus 图标，提升开发环境的敏捷度
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Mount the Vue instance to the DOM
// 将 Vue 实例挂载到真实的 DOM 节点上
app.mount('#app')