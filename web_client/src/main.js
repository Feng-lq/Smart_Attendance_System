// web_client/src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia' // 🔥 必须引入这个
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入所有图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

// 🔥 关键步骤：注册 Pinia
// 注意：最好在 router 之前注册
app.use(createPinia())

app.use(router)
app.use(ElementPlus)

// 自动注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')