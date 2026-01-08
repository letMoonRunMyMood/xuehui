<template>
  <div class="admin-dashboard">
    <NavigationBar :currentNav="currentNav" />
    <div class="content-wrapper">
      <div class="pc-main">
        <div class="sidebar-container">
          <SidebarMenu :role="role" @menuChange="handleMenuChange" />
        </div>
        <div class="content-area">
          <div v-if="isLoading" class="loading提示">
            加载中...
          </div>
          <router-view v-else />
        </div>
      </div>
    </div>

    <!-- 页脚：添加footer-fixed类（对应home的写法） -->
    <Footer class="footer-fixed" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import NavigationBar from '../components/NavigationBar.vue'
import SidebarMenu from '../components/Sidebar.vue'
import Footer from '../components/Footer.vue'

const props = defineProps({
  role: { type: Number, required: true }
})

const currentNav = ref('invitationCode')
const isLoading = ref(false)
const router = useRouter()
let routeWatcher = null

onMounted(() => {
  // 组件内监听
  routeWatcher = watch(
    () => router.currentRoute,
    (to, from) => {
      if (from.path.includes('personalCenter') || to.path.includes('personalCenter')) {
        isLoading.value = true
        setTimeout(() => {
          isLoading.value = false
        }, 300)
      }
    },
    { immediate: false }
  )
})

// 清理监听，避免内存泄漏
onUnmounted(() => {
  if (routeWatcher) routeWatcher()
})

const handleMenuChange = (menuKey) => {
  currentNav.value = menuKey
  router.push(`/personalCenter/${menuKey}`)
}
</script>

<style scoped>
/* 核心修改：外层容器完全对齐home.vue的pc-container */
.admin-dashboard {
  width: 100%;
  height: 100vh; /* 替换原min-height，强制占满视口（home核心逻辑） */
  background-color: #f0f7f4;
  display: flex; /* 新增：flex垂直布局 */
  flex-direction: column; /* 新增：子元素垂直排列 */
  overflow: hidden; /* 新增：避免容器本身滚动 */
}

/* 核心新增：中间内容包裹层（对应home的content-wrapper） */
.content-wrapper {
  flex: 1; /* 填充除页脚外的所有空间 */
  overflow-y: auto; /* 内容超出时滚动 */
  padding-bottom: 20px; /* 避免内容贴页脚（home同款） */
}

/* 以下样式完全保留，无任何修改 */
.pc-main {
  max-width: 1440px;
  margin: 20px auto;
  display: flex;
  gap: 30px;
  padding: 0 24px;
}

.sidebar-container {
  width: 240px;
  height: 600px;
  flex-shrink: 0;
}

.content-area {
  width: 1200px;
  height: 600px;
  position: relative;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e9e5;
}

.loading提示 {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 16px;
  color: #666;
  padding: 20px;
}

.footer-fixed {
  width: 100%;
  margin-top: auto; 
}
</style>