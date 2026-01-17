import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      // 保持不变，这允许你使用 @/api/attendance 这种简写
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // --- 新增配置项 ---
  server: {
    port: 5173,      // 固定前端端口
    proxy: {
      // 配置代理，解决开发环境下的跨域问题
      '/api': {
        target: 'http://127.0.0.1:8000', // 你的 FastAPI 后端地址
        changeOrigin: true,
        // 如果后端接口没有 /api 前缀（但你的后端已经加了），则不需要 rewrite
        // rewrite: (path) => path.replace(/^\/api/, '') 
      },
      // 配置静态资源代理（可选）
      '/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})