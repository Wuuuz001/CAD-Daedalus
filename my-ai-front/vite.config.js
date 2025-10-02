// vite.config.js
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // --- 添加下面这个 server 部分 ---
  server: {
    proxy: {
      // 这个配置意味着：所有以 '/api' 开头的请求
      // 都会被Vite开发服务器自动转发到 target 指定的地址
      '/api': {
        target: 'http://localhost:3001', // 这里必须是你的后端服务器地址！
        changeOrigin: true, // 必须设置为true
      }
    }
  }
})