<template>
  <div class="role-based-container">
    <div v-if="roleValue === 2">
      <AdministerDashboard :role="roleValue"/>
    </div>
    <div v-else-if="roleValue === 1">
      <TeacherDashboard :role="roleValue"/>
    </div>
    <div v-else-if="roleValue === 0">
      <StudentDashboard :role="roleValue"/>
    </div>
    <div v-else class="unknown-role">
      <el-message type="warning">身份验证失败，请重新登录</el-message>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import TeacherDashboard from './TeacherDashboard.vue'
import StudentDashboard from './StudentDashboard.vue'
import AdministerDashboard from "./AdministerDashboard.vue";

const router = useRouter()
const route = useRoute()

const roleString = ref(sessionStorage.getItem('role') || '')
const roleValue = computed(() => {
  const num = parseInt(roleString.value, 10)
  return isNaN(num) ? null : num
})

const defaultSubRoute = computed(() => {
  console.log('Determining default sub-route for role:', roleValue.value)
  switch (roleValue.value) {
    case 0: return 'mySubscribe'
    case 1: return 'courseManagement'
    case 2: return 'invitationCode'
    default: return ''
  }
})

const checkRoleAndNavigate = () => {
  if (roleValue.value === null || ![0, 1, 2].includes(roleValue.value)) {
    router.push({
      path: '/auth',
      query: { type: 'login', redirect: route.fullPath }
    })
    return
  }

  if (route.path === '/personalCenter' && !route.params.pathMatch) {
    router.push(`/personalCenter/${defaultSubRoute.value}`)
  }
}

onMounted(() => {
  checkRoleAndNavigate()
})

watch(
  () => sessionStorage.getItem('role'),
  (newRole) => {
    roleString.value = newRole
    checkRoleAndNavigate()
  }
)
</script>

<style scoped>
.role-based-container {
  width: 100%;
  min-height: 100vh;
}

.unknown-role {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 18px;
  color: #666;
}
</style>