import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/main.css'

// 创建Vue应用实例
const app = createApp(App)

// 安装插件
app.use(router)
app.use(ElementPlus)

// 挂载应用
app.mount('#app')