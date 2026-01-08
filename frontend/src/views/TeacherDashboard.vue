<template>
  <div :class="`${roleType}-dashboard`">
    <NavigationBar :currentNav="currentNav" :role="role" />
    
    <!-- 中间内容包裹层：填充空间并支持滚动 -->
    <div class="content-wrapper">
      <div class="pc-main">
        <div class="sidebar-container">
          <SidebarMenu :role="role" @menuChange="handleMenuChange" />
        </div>
        <div class="content-area">
          <div v-if="isLoading" class="loading-indicator">
            <div class="spinner"></div>
            <p>加载中...</p>
          </div>
          <router-view v-else />
        </div>
      </div>
    </div>
    
    <Footer class="footer-fixed" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import NavigationBar from '../components/NavigationBar.vue'
import SidebarMenu from '../components/Sidebar.vue'
import Footer from '../components/Footer.vue'

// 接收角色参数，限制仅接受讲师角色值（1）
const props = defineProps({
  role: { 
    type: Number, 
    required: true,
    validator: (value) => value === 1 
  }
})

// 计算角色类型标识
const roleType = computed(() => {
  switch (props.role) {
    case 1: return 'teacher'
    default: return 'teacher'
  }
})

const router = useRouter()
const route = useRoute()

// 初始化当前导航：优先从路由取，默认课程管理
const currentNav = ref(route.path.split('/').pop() || 'courseManagement')
const isLoading = ref(false)
let routeWatcher = null // 存储路由监听实例，用于后续销毁

// 监听路由变化，触发加载状态和导航更新
onMounted(() => {
  routeWatcher = watch(
    () => router.currentRoute,
    (to, from) => { 
      if (from.path.includes('personalCenter') || to.path.includes('personalCenter')) {
        currentNav.value = to.path.split('/').pop() || 'courseManagement'
        isLoading.value = true
        // 模拟加载延迟，300ms后关闭加载态
        setTimeout(() => {
          isLoading.value = false
        }, 300)
      }
    },
    { immediate: false }
  )
})

// 组件卸载时销毁路由监听，避免内存泄漏
onUnmounted(() => {
  if (routeWatcher) routeWatcher()
})

// 菜单切换：更新导航并跳转对应路由
const handleMenuChange = (menuKey) => {
  currentNav.value = menuKey
  router.push(`/personalCenter/${menuKey}`)
}
</script>

<style scoped>
[class$="-dashboard"] {
  width: 100%;
  height: 100vh;
  background-color: #f5f7fa;
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 填充剩余空间，内容超出时纵向滚动 */
.content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 20px; /* 避免内容贴合页脚 */
}

.pc-main {
  max-width: 1440px;
  margin: 20px auto 0;
  display: flex;
  gap: 30px;
  padding: 0 24px;
}

.sidebar-container {
  width: 240px;
  height: 600px;
  flex-shrink: 0; /* 固定宽度，不被挤压 */
}

.content-area {
  width: 1200px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e9e5;
  padding: 0 24px;
  height: 600px;
  position: relative;
}

/* 加载状态：全屏居中覆盖 */
.loading-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
  border-radius: 12px;
}

/* 加载动画：旋转圆圈 */
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e5e5;
  border-radius: 50%;
  border-top-color: #2b6a3d;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 页脚固定：自动推至容器底部 */
.footer-fixed {
  width: 100%;
  margin-top: auto;
}
</style>