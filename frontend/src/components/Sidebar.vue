<template>
  <div class="pc-sidebar">
    <div class="sidebar-title">{{ sidebarTitle }}</div>

    <!-- 检查是否有菜单项 -->
    <div v-if="filteredMenuSections.length === 0" class="empty-menu">
      暂无可用菜单
    </div>

    <div class="sidebar-section" v-else v-for="section in filteredMenuSections" :key="section.title">
      <h3>{{ section.title }}</h3>
      <div class="option-list">
        <a
            href="#"
            class="option-item"
            :class="{ active: currentMenu === item.key }"
            v-for="item in section.items"
            :key="item.key"
            @click.prevent="handleMenuClick(item)"
        >
          <i :class="item.icon || 'el-icon-document'" />
          {{ item.label }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

// 定义角色常量
const ROLES = {
  ADMIN: 2,
  TEACHER: 1,
  STUDENT: 0
}

// 定义侧边栏标题映射
const SIDEBAR_TITLES = {
  [ROLES.ADMIN]: '运营管理中心',
  [ROLES.TEACHER]: '讲师中心',
  [ROLES.STUDENT]: '学生中心'
}

// 定义菜单结构 - 学生部分
const studentMenuSections = ref([
  {
    title: '学习中心',
    roles: [ROLES.STUDENT],
    items: [
      {
        key: 'mySubscribe',
        label: '我的订阅',
        icon: 'el-icon-reading',
        path: '/personalCenter/mySubscribe'
      },
      {
        key: 'myFavorite',
        label: '我的收藏',
        icon: 'el-icon-school',
        path: '/personalCenter/myFavorite'
      }
    ]
  },
  {
    title: '个人中心',
    roles: [ROLES.STUDENT],
    items: [
      {
        key: 'studentProfile',
        label: '个人资料',
        icon: 'el-icon-user',
        path: '/personalCenter/studentProfile'
      }
    ]
  }
])

// 定义菜单结构 - 讲师部分
const teacherMenuSections = ref([
  {
    title: '课程管理',
    roles: [ROLES.TEACHER],
    items: [
      {
        key: 'courseManagement',
        label: '我的课程',
        icon: 'el-icon-notebook-2',
        path: '/personalCenter/courseManagement'
      }
    ]
  },
  {
    title: '个人中心',
    roles: [ROLES.TEACHER],
    items: [
      {
        key: 'teacherProfile',
        label: '个人资料',
        icon: 'el-icon-user',
        path: '/personalCenter/teacherProfile'
      }
    ]
  }
])

// 定义菜单结构 - 管理员部分
const adminMenuSections = ref([
  {
    title: '运营管理',
    roles: [ROLES.ADMIN],
    items: [
      {
        key: 'invitationCode',
        label: '邀请码管理',
        icon: 'el-icon-key',
        path: '/personalCenter/invitationCode'
      },
      {
        key: 'adManagement',
        label: '广告管理',
        icon: 'el-icon-s-marketing',
        path: '/personalCenter/adManagement'
      }
    ]
  }
])

// 合并所有菜单
const menuSections = ref([
  ...studentMenuSections.value,
  ...teacherMenuSections.value,
  ...adminMenuSections.value
])

// 定义props接收用户角色
const props = defineProps({
  role: {
    type: Number,
    required: true
  }
})
console.log('当前角色:', props.role)
console.log(typeof props.role)
const router = useRouter()
const currentMenu = ref('')

// 根据角色计算侧边栏标题
const sidebarTitle = computed(() => {
  return SIDEBAR_TITLES[props.role] || '管理中心'
})

// 根据角色过滤菜单
const filteredMenuSections = computed(() => {
  return menuSections.value.filter(section =>
      section.roles.includes(props.role)
  )
})

// 初始化当前菜单
const initCurrentMenu = () => {
  if (filteredMenuSections.value.length > 0) {
    const firstSection = filteredMenuSections.value[0]
    if (firstSection.items.length > 0) {
      currentMenu.value = firstSection.items[0].key
      // 初始化时导航到第一个菜单对应的路由
      navigateToMenu(firstSection.items[0])
    }
  }
}

// 处理菜单点击事件 - 导航到对应路由
const handleMenuClick = (item) => {
  currentMenu.value = item.key
  navigateToMenu(item)
}

// 导航到菜单对应的路由
const navigateToMenu = (item) => {
  if (item.path) {
    router.push(item.path)
  } else {
    console.warn(`菜单 ${item.label} 未配置路由路径`)
  }
}

// 当角色变化时重新初始化菜单
watch(() => props.role, () => {
  initCurrentMenu()
})

// 组件挂载时初始化菜单
onMounted(() => {
  initCurrentMenu()
})
</script>

<style scoped>
.pc-sidebar {
  width: 240px;
  height: 600px;
  box-sizing: border-box;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e9e5;
  padding: 24px;
}

.sidebar-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.sidebar-section {
  margin-bottom: 32px;
}

.sidebar-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  position: relative;
  padding-left: 24px;
  text-align: left;
}

.sidebar-section h3::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 16px;
  background-color: #20c997;
  border-radius: 2px;
}

.option-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-item {
  padding: 10px 12px;
  color: #666;
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-item.active,
.option-item:hover {
  background-color: #f1f5f9;
  color: #20c997;
  font-weight: 500;
}

/* 图标样式 */
.el-icon-key {
  color: #94a3b8;
}
.el-icon-s-marketing {
  color: #f59e0b;
}
.el-icon-reading {
  color: #4096ff;
}
.el-icon-school {
  color: #67c23a;
}
.el-icon-notebook-2, .el-icon-user {
  color: #909399;
}

/* 空状态样式 */
.empty-menu {
  padding: 20px;
  text-align: center;
  color: #999;
}
</style>