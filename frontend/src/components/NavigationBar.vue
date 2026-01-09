<template>
  <div class="pc-header">
    <div class="pc-header-inner">
      <div class="pc-logo" @click="goToHome">
        <div class="logo">学 汇</div>
      </div>

      <ul class="pc-nav">
        <li
            v-for="item in navItems"
            :key="item.path"
            :class="{ active: isActive(item.path) }"
            @click="switchNav(item.path)"
        >
          {{ item.title }}
        </li>
      </ul>

      <div class="search-container" :style="{ visibility: isCourseCenter ? 'hidden' : 'visible' }">
        <input
            v-model="searchValue"
            type="link"
            placeholder="输入课程名或讲师名来搜索课程..."
            class="search-input"
            @keyup.enter="handleSearch"
        />
        <button class="search-icon-btn" @click="handleSearch">
          <svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="feather feather-search">
            <circle cx="11" cy="11" r="8" fill="none" stroke="black" stroke-width="2" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" fill="none" stroke="black"/>
          </svg>
        </button>
      </div>

      <div class="user-avatar-container" @click="toggleLoginMenu">
        <div v-if="isAvatarLoading" class="avatar-circle loading">
          <div class="spinner"></div>
        </div>
        <div v-else class="avatar-circle" 
             :style="{ backgroundImage: `url(${finalAvatarUrl})` }">
        </div>
        <div v-if="showLoginMenu" class="login-menu">
          <a href="#" class="menu-item" @click="handleLogout">退出账号</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import axiosInstance from "@/service/api.js";
import { fixCoverPath } from '@/utils/format.js'
import eventBus, { EVENT_TYPES } from '@/utils/eventBus.js'

const router = useRouter()
const route = useRoute()

const showLoginMenu = ref(false)
const searchValue = ref('')
const rawAvatarUrl = ref('')
const finalAvatarUrl = ref('')
const isAvatarLoading = ref(false)
const defaultAvatar = ref("static/default/default_avatar.jpg")
const fixedDefaultAvatar = computed(() => fixCoverPath(defaultAvatar.value))

const avatarCache = new Map()
const userInfoCache = new Map()
let abortController = null

const isCourseCenter = computed(() => {
  return route.path === '/course' || route.path.startsWith('/course/')
})

const navItems = computed(() => {
  const role = sessionStorage.getItem('role') || '0'
  return role === '2'
      ? [
        { path: '/home', title: '首页' },
        { path: '/course', title: '课程中心' },
        { path: '/statistics', title: '数据统计' },
        { path: '/personalCenter', title: '运营管理' }
      ]
      : [
        { path: '/home', title: '首页' },
        { path: '/course', title: '课程中心' },
        { path: '/personalCenter', title: '个人中心' }
      ]
})

const isActive = (targetPath) => {
  return route.path === targetPath || route.path.startsWith(`${targetPath}/`)
}

const switchNav = (path) => router.push(path)
const goToHome = () => router.push('/home')

const handleLogout = async () => {
  showLoginMenu.value = false
  try {
    await axiosInstance.post('/api/auth/logout', {}) 
    sessionStorage.clear()
    avatarCache.clear()
    userInfoCache.clear()
    await preloadImage(fixedDefaultAvatar.value)
    finalAvatarUrl.value = fixedDefaultAvatar.value
    ElMessage.success('已退出登录')
    router.push('/auth')
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
}

const handleSearch = () => {
  if (searchValue.value.trim()) {
    router.push({ path: '/course', query: { keyword: searchValue.value, page: 1 } })
    searchValue.value = ''
  }
}

const toggleLoginMenu = () => (showLoginMenu.value = !showLoginMenu.value)

const preloadImage = (imgUrl) => {
  if (avatarCache.has(imgUrl)) {
    return avatarCache.get(imgUrl)
  }

  const promise = new Promise((resolve) => {
    if (!imgUrl) {
      avatarCache.set(imgUrl, Promise.resolve(false))
      resolve(false)
      return
    }

    const img = new Image()
    img.src = imgUrl
    img.onload = () => {
      avatarCache.set(imgUrl, Promise.resolve(true))
      resolve(true)
    }
    img.onerror = () => {
      preloadImage(fixedDefaultAvatar.value).then(() => {
        avatarCache.set(imgUrl, Promise.resolve(false))
        resolve(false)
      })
    }
  })

  avatarCache.set(imgUrl, promise)
  return promise
}

const loadUserAvatar = async (forceRefresh = false) => {
  if (abortController) abortController.abort()
  abortController = new AbortController()

  isAvatarLoading.value = true
  try {
    const role = sessionStorage.getItem('role') || '0'
    const userId = sessionStorage.getItem('id')
    const cacheKey = `${role}_${userId}`

    if (role === '2') {
      await preloadImage(fixedDefaultAvatar.value)
      finalAvatarUrl.value = fixedDefaultAvatar.value
      isAvatarLoading.value = false
      return
    }

    if (!role || !userId) {
      await preloadImage(fixedDefaultAvatar.value)
      finalAvatarUrl.value = fixedDefaultAvatar.value
      isAvatarLoading.value = false
      return
    }

    if (forceRefresh) {
      userInfoCache.delete(cacheKey);
      avatarCache.clear();
    }

    let targetAvatarUrl = fixedDefaultAvatar.value
    if (!forceRefresh && userInfoCache.has(cacheKey)) {
      targetAvatarUrl = userInfoCache.get(cacheKey)
    } else {
      const { apiUrl, params } = role === '0'
          ? { apiUrl: '/api/student/get-student-info', params: { student_id: userId } }
          : { apiUrl: '/api/teacher/get-teacher-info', params: { teacher_id: userId } }

      const response = await axiosInstance.get(apiUrl, {
        params,
        signal: abortController.signal,
      })

      if (response.data.success) {
        const backendAvatar = response.data.data?.avatar || ''
        targetAvatarUrl = fixCoverPath(backendAvatar) || fixedDefaultAvatar.value
        userInfoCache.set(cacheKey, targetAvatarUrl)
        setTimeout(() => userInfoCache.delete(cacheKey), 5 * 60 * 1000)
      }
    }

    const isLoaded = await preloadImage(targetAvatarUrl)
    finalAvatarUrl.value = isLoaded ? targetAvatarUrl : fixedDefaultAvatar.value
  } catch (error) {
    await preloadImage(fixedDefaultAvatar.value)
    finalAvatarUrl.value = fixedDefaultAvatar.value

    if (error.name !== 'AbortError') {
      ElMessage.error(error.response?.status === 408 ? '请求超时' : '获取头像失败')
    }
  } finally {
    isAvatarLoading.value = false
    abortController = null
  }
}

const listenAvatarUpdate = () => {
  eventBus.on(EVENT_TYPES.AVATAR_UPDATED, () => {
    loadUserAvatar(true);
  });
};

onMounted(() => {
  preloadImage(fixedDefaultAvatar.value)
  loadUserAvatar()
  listenAvatarUpdate()
})

watch([
  () => sessionStorage.getItem('role'),
  () => sessionStorage.getItem('id')
], () => {
  loadUserAvatar()
}, { immediate: false })

onUnmounted(() => {
  if (abortController) abortController.abort()
  eventBus.off(EVENT_TYPES.AVATAR_UPDATED)
})
</script>

<style scoped>
.pc-header {
  background-color: #fff;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.pc-header-inner {
  max-width: 1400px;
  height: 64px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
}

.pc-logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-right: 30px;
}

.logo {
  font-size: 22px;
  font-weight: 600;
  color: #2e7d32;
  padding: 8px 16px;
}

.pc-nav {
  display: flex;
  gap: 32px;
  list-style: none;
  padding: 0;
  margin-right: auto;
  margin-left: auto;
}

.pc-nav li {
  cursor: pointer;
  font-size: 18px;
  color: #333;
  padding-bottom: 4px;
  transition: all 0.3s ease;
  position: relative;
  font-weight: 500;
}

.pc-nav li.active {
  color: #206644;
}

.pc-nav li.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #20c997;
}

.search-container {
  display: flex;
  align-items: center;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 0 10px;
  height: 40px;
  min-width: 300px;
  margin-right: 30px;
  transition: all 0.3s ease;
}

.search-input {
  background: transparent;
  border: none;
  outline: none;
  font-size: 14px;
  color: #495057;
  width: 100%;
  padding: 0 8px;
}

.search-icon-btn {
  background: none;
  border: none;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #666;
  transition: all 0.2s ease;
  padding: 0;
}

.search-icon-btn:hover {
  color: #20c997;
  transform: scale(1.1);
}

.search-icon-btn svg {
  width: 20px;
  height: 20px;
}

.user-avatar-container {
  position: relative;
  cursor: pointer;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
}

.avatar-circle.loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: #20c997;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-menu {
  position: absolute;
  top: 52px;
  right: 0;
  width: 130px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 8px 0;
  z-index: 100;
  border: 1px solid #e9ecef;
}

.menu-item {
  display: block;
  padding: 8px 16px;
  color: #495057;
  text-decoration: none;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.menu-item:hover {
  background-color: #f1f3f5;
}

@media (max-width: 768px) {
  .pc-header-inner {
    padding: 0 16px;
  }
  .search-container {
    min-width: 180px;
    margin-right: 15px;
  }
  .avatar-circle {
    width: 36px;
    height: 36px;
  }
}
</style>