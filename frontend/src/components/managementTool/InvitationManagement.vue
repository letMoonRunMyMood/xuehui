<template>
  <!-- 生成邀请码弹窗容器 -->
  <div class="invitation-generator-container">
    <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="ad-form"
    >
      <!-- 邮箱输入项 -->
      <el-form-item label="邮箱" prop="email" class="form-item">
        <el-input
            v-model="form.email"
            placeholder="请输入被邀请人的邮箱"
            clearable
            size="large"
        />
      </el-form-item>
    </el-form>

    <!-- 弹窗底部按钮区：取消左/确认右 布局 -->
    <div class="dialog-footer">
      <el-button size="large" @click="handleCancel">取消</el-button>
      <el-button 
          type="primary" 
          :loading="loading" 
          @click="handleGenerateCode"
          class="confirm-btn"
          size="large"
      >
        确认
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axiosInstance from "@/service/api.js";

// 定义向父组件传递的事件
const emit = defineEmits(['closeDialog', 'refreshCodes'])

// 表单数据
const form = reactive({
  email: ''
})

// 表单校验规则
const rules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
  ]
}

const formRef = ref(null)
const loading = ref(false)

// 生成邀请码核心逻辑
const handleGenerateCode = async () => {
  await formRef.value.validate((valid) => {
    if (!valid) return false

    loading.value = true
    axiosInstance.post('/api/admin/create-code', { email: form.email })
        .then(res => {
          if (res.data.success) {
            ElMessage.success('邀请码生成成功')
            emit('refreshCodes')
            emit('closeDialog')
            form.email = ''
          } else {
            ElMessage.error(res.data.message || '生成失败，请重试')
          }
        })
        .catch(error => {
          ElMessage.error('网络错误，请稍后再试')
          console.error('生成邀请码失败:', error)
        })
        .finally(() => {
          loading.value = false
        })

    return true
  })
}

// 取消按钮：关闭弹窗
const handleCancel = () => {
  emit('closeDialog')
}
</script>

<style scoped>
/* 弹窗容器样式：对齐主题规范 */
.invitation-generator-container {
  padding: 24px;
  width: 100%;
  box-sizing: border-box;
}

/* 表单样式：复用广告管理表单 */
.ad-form {
  width: 100%;
  margin-bottom: 16px;
}

/* 表单项布局 */
.form-item {
  width: 100%;
  margin-bottom: 20px !important;
  display: flex;
  align-items: center;
}

/* 表单标签样式 */
:deep(.el-form-item__label) {
  width: 120px;
  flex-shrink: 0;
  text-align: left;
  padding-top: 2px;
  font-size: 16px;
  color: #4b5563;
  font-weight: 500;
}

/* 输入框内容区布局 */
:deep(.el-form-item__content) {
  width: calc(100% - 120px);
  padding-left: 20px;
  box-sizing: border-box;
}

/* 输入框样式：主题规范 */
:deep(.el-input) {
  width: 100%;
  height: 36px;
  --el-input-border-color: #e5e7eb;
  --el-input-hover-border-color: #d1d5db;
  --el-input-focus-border-color: #22c55e;
  --el-input-text-color: #374151;
  --el-input-placeholder-text-color: #9ca3af;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: none;
  border: 1px solid #e5e7eb;
}

:deep(.el-input__wrapper:hover) {
  border-color: #d1d5db;
}

:deep(.el-input__wrapper:focus-within) {
  border-color: #22c55e;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

/* 底部按钮区：统一弹窗布局 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

/* 取消按钮样式 */
:deep(.dialog-footer .el-button:first-child) {
  padding: 0 20px;
  height: 36px;
  font-size: 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background-color: #f9fafb;
  color: #374151;
  transition: all 0.2s ease;
}

:deep(.dialog-footer .el-button:first-child:hover) {
  border-color: #d1d5db;
  background-color: #f3f4f6;
}

/* 确认按钮 */
:deep(.confirm-btn) {
  background-color: #22c55e !important;
  border-color: #22c55e !important;
  padding: 0 20px !important;
  height: 36px !important;
  font-size: 16px !important;
  border-radius: 8px !important;
  transition: all 0.2s ease-in-out;
  box-shadow: 0 2px 4px rgba(34, 197, 94, 0.15);
}

:deep(.confirm-btn:hover) {
  background-color: #16a34a !important;
  border-color: #16a34a !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(34, 197, 94, 0.2);
}

:deep(.confirm-btn:active) {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(34, 197, 94, 0.15);
}

/* 加载状态按钮样式 */
:deep(.confirm-btn.is-loading) {
  background-color: #22c55e !important;
  border-color: #22c55e !important;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: 0 2px 4px rgba(34, 197, 94, 0.15) !important;
}
</style>