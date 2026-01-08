<template>
  <div class="invitation-code-management">
    <!-- 页面标题和操作按钮 -->
    <div class="page-header">
      <h2 class="page-title">邀请码管理</h2>
      <el-button type="success" @click="openCreateDialog" class="create-btn">
        <span>生成邀请码</span>
      </el-button>
    </div>

    <!-- 筛选区域 -->
    <div class="course-filter">
      <input v-model="searchKey" placeholder="搜索邮箱/邀请码" class="search-input" />
      <el-button @click="filterCodes" class="filter-item-button">筛选</el-button>
    </div>

    <!-- 邀请码列表 -->
    <div class="code-list">
      <h3 class="section-title">邀请码列表</h3>
      <div class="code-table-container">
        <el-table
            :data="paginatedCodes"
            border
            stripe
            style="width: 100%;"
            v-loading="isLoading"
            :header-cell-style="{ background: '#f8f9fa' }"
            :row-style="{ height: '50px' }"
        >
          <el-table-column prop="id" label="ID" width="120" align="center" />
          <el-table-column prop="email" label="关联邮箱" width="300" align="center" />
          <el-table-column prop="invitation_code" label="邀请码" width="320" align="center" />
          <el-table-column prop="created_at" label="创建时间" width="210" align="center" />
          <el-table-column label="操作" width="185" align="center">
            <template #default="scope">
              <el-button
                  type="text"
                  size="small"
                  @click="copyCode(scope.row.invitation_code)"
                  class="action-button copy-btn"
              >
                <el-icon><DocumentCopy /></el-icon>复制
              </el-button>
              <el-button
                  type="danger"
                  size="small"
                  @click="deleteCode(scope.row.id)"
                  class="action-button delete-btn"
              >
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 空状态提示 -->
    <div class="empty-state" v-if="filteredCodes.length === 0 && !isLoading">
      <div class="empty-icon placeholder-icon">
        <span class="icon">○</span>
      </div>
      <p class="empty-text">暂无邀请码数据</p>
      <p class="empty-tip" v-if="role === '2'">点击右上角「生成邀请码」按钮创建新邀请码</p>
    </div>

    <!-- 分页组件 -->
    <div class="pagination-container" v-if="filteredCodes.length > 0">
      <el-pagination
          class="pagination"
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredCodes.length"
          layout="prev, pager, next"
          background
          @current-change="handlePageChange"
      />
    </div>

    <!-- 生成邀请码弹窗 -->
    <el-dialog title="生成邀请码" v-model="createDialogVisible" width="600px">
      <InvitationManagement
          @closeDialog="createDialogVisible = false"
          @refreshCodes="fetchCodes"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentCopy, Delete } from '@element-plus/icons-vue'
import InvitationManagement from '@/components/managementTool/InvitationManagement.vue'
import axiosInstance from '@/service/api.js'

// 从会话存储中获取当前用户角色，用于权限控制
const role = computed(() => sessionStorage.getItem('role') || '0')

// 响应式数据状态定义
const codeList = ref([]) // 存储从服务器获取的完整邀请码列表
const filteredCodes = ref([]) // 存储经过筛选后的邀请码列表
const searchKey = ref('') // 搜索框中输入的关键字
const pageSize = ref(8) // 每页显示的数据条数
const currentPage = ref(1) // 当前页码
const isLoading = ref(false) // 控制页面加载状态
const createDialogVisible = ref(false) // 控制“生成邀请码”弹窗的显示与隐藏

// 计算属性，用于根据当前页码和每页数量，从筛选后的列表中计算出需要显示的数据
const paginatedCodes = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredCodes.value.slice(start, end)
})

// 组件挂载时，如果用户是管理员，则自动获取邀请码列表
onMounted(() => {
  if (role.value === '2') {
    fetchCodes()
  }
})

/**
 * 获取邀请码列表
 * 与后端接口 /api/admin/get-code 对接
 */
const fetchCodes = async () => {
  isLoading.value = true
  try {
    const res = await axiosInstance.get('/api/admin/get-code')
    if (res.data.success) {
      // 格式化时间数据，将ISO字符串转换为本地时间字符串
      const formattedCodes = res.data.data.map((code) => ({
        ...code,
        created_at: new Date(code.created_at).toLocaleString()
      }))
      codeList.value = formattedCodes
      filterCodes() // 获取数据后立即执行一次筛选
    } else {
      ElMessage.error(res.data.message || '获取邀请码列表失败')
    }
  } catch (error) {
    console.error('获取邀请码列表失败', error)
    ElMessage.error('网络错误，请稍后再试')
  } finally {
    isLoading.value = false
  }
}

/**
 * 根据搜索关键字筛选邀请码列表
 */
const filterCodes = () => {
  if (!searchKey.value.trim()) {
    // 如果搜索框为空，则显示全部数据
    filteredCodes.value = [...codeList.value]
  } else {
    // 根据邮箱或邀请码进行模糊匹配
    const keyword = searchKey.value.toLowerCase().trim()
    filteredCodes.value = codeList.value.filter((item) => {
      return (
          item.email.toLowerCase().includes(keyword) ||
          item.invitation_code.toLowerCase().includes(keyword)
      )
    })
  }
  currentPage.value = 1 // 筛选后重置页码为第一页
}

/**
 * 打开生成邀请码的弹窗
 */
const openCreateDialog = () => {
  createDialogVisible.value = true
}

/**
 * 将指定的邀请码复制到用户的剪贴板
 * @param {string} code - 需要复制的邀请码字符串
 */
const copyCode = (code) => {
  navigator.clipboard.writeText(code)
      .then(() => ElMessage.success('邀请码已复制到剪贴板'))
      .catch(() => ElMessage.error('复制失败，请手动复制'))
}

/**
 * 删除指定ID的邀请码
 * @param {number|string} id - 需要删除的邀请码ID
 */
const deleteCode = async (id) => {
  try {
    // 弹出确认对话框，防止误操作
    await ElMessageBox.confirm(
        '确定要删除这个邀请码吗？删除后将无法恢复',
        '提示',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
    ).then(async () => {
      // 用户点击确认后，执行删除操作
      try {
        // 发送DELETE请求到后端，并通过URL查询参数传递code_id
        const res = await axiosInstance.delete('/api/admin/delete-code', {
          params: {
            code_id: id
          }
        })

        if (res.data.code === 200) {
          ElMessage.success('删除成功')
          fetchCodes() // 删除成功后，重新获取列表以更新视图
        } else {
          ElMessage.error(res.data.message || '删除失败')
        }
      } catch (error) {
        console.error('删除邀请码失败', error)
        // 处理不同类型的错误响应
        if (error.response) {
          const { status, data } = error.response;
          if (status === 403) {
            ElMessage.error(data.message || '用户无权限执行此操作');
          } else if (status === 500) {
            ElMessage.error(data.message || '服务器内部错误，删除失败');
          } else {
            ElMessage.error(`删除失败，错误码: ${status}`);
          }
        } else {
          ElMessage.error('网络错误，请稍后再试');
        }
      }
    }).catch((err) => {
      // 如果用户取消了操作，则提示已取消
      if (err === 'cancel') {
        ElMessage.info('已取消删除操作')
      } else {
        console.error('删除操作异常', err)
      }
    })
  } catch (error) {
    console.error('删除邀请码函数异常', error)
  }
}

/**
 * 处理分页页码变化的事件
 * @param {number} newPage - 新的页码
 */
const handlePageChange = (newPage) => {
  currentPage.value = newPage
}
</script>

<style scoped>
/* 全局容器样式 - 对齐广告管理页面 */
.invitation-code-management {
  flex: 1;
  background-color: #ffffff;
  padding: 28px 32px; /* 对齐广告管理的内边距 */
  border-radius: 12px;
  box-sizing: border-box;
  height: 600px;
  margin: 0 auto; /* 居中对齐 */
  max-width: 1400px; /* 对齐广告管理的最大宽度 */
}

/* 页面标题栏 - 对齐广告管理的间距和样式 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px; /* 对齐广告管理的底部间距 */
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  letter-spacing: 0.2px;
}

/* 生成按钮样式 - 完全对齐广告管理的按钮样式 */
.create-btn {
  padding: 0 24px;
  font-size: 15px;
  width: 120px;
  height: 42px;
  transition: all 0.2s ease-in-out;
  background-color: #22c55e !important; /* 强制覆盖element默认样式 */
  border: none !important;
  color: white !important;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(34, 197, 94, 0.15);
}

.create-btn:hover {
  background-color: #16a34a !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(34, 197, 94, 0.2);
}

.create-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(34, 197, 94, 0.15);
}

/* 筛选区域样式 - 对齐广告管理的间距 */
.course-filter {
  display: flex;
  align-items: center;
  gap: 16px; /* 对齐广告管理的间距 */
  margin-bottom: 24px; /* 对齐广告管理的底部间距 */
}

/* 搜索框样式 - 完全对齐广告管理 */
.search-input {
  flex: 1;
  height: 42px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  padding: 0 16px;
  font-size: 15px;
  color: #374151;
  transition: all 0.2s ease;
  outline: none;
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-input:hover {
  border-color: #d1d5db;
}

.search-input:focus {
  border-color: #22c55e;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

/* 筛选按钮样式 - 完全对齐广告管理 */
.filter-item-button {
  width: 90px;
  height: 42px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background-color: #f9fafb;
  cursor: pointer;
  font-size: 15px;
  color: #374151;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.filter-item-button:hover {
  border-color: #22c55e;
  background-color: #f0fdf4;
  color: #16a34a;
}

/* 列表标题样式 - 完全对齐广告管理 */
.code-list {
  margin-bottom: 20px;
  width: 100%;
}

.section-title {
  font-size: 17px;
  margin-bottom: 16px;
  color: #1f2937;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 12px;
  position: relative;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background-color: #22c55e;
  border-radius: 2px;
}

/* 表格容器样式 - 完全对齐广告管理 */
.code-table-container {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); /* 对齐广告管理的阴影强度 */
  max-height: 350px; /* 对齐广告管理的最大高度 */
  overflow-y: auto;
  width: 100%;
  border: 1px solid #f3f4f6;
}

/* 表格样式深度优化 - 完全对齐广告管理 */
:deep(.el-table) {
  --el-table-border-color: #e5e7eb;
  --el-table-text-color: #374151;
  --el-table-header-text-color: #1f2937;
  border: none !important;
}

:deep(.el-table th) {
  border-color: #e5e7eb;
  border-width: 1px;
  background: #f8f9fa !important;
  font-weight: 600;
  font-size: 14px;
  height: 48px;
}

:deep(.el-table td) {
  border-color: #e5e7eb;
  border-width: 1px;
  font-size: 14px;
  color: #4b5563;
  height: 50px;
}

:deep(.el-table--striped tr.el-table__row--striped td) {
  background-color: #fafafa !important;
}

:deep(.el-table__row:hover > td) {
  background-color: #f0fdf4 !important;
}

/* 操作按钮样式 - 完全对齐广告管理 */
.action-button {
  padding: 0 8px;
  margin: 0 4px;
  font-size: 14px;
  height: 32px;
  line-height: 32px;
  transition: all 0.2s ease;
  border-radius: 4px;
}

.action-button .el-icon {
  margin-right: 4px;
  font-size: 16px;
}

/* 复制按钮样式 - 对齐广告管理的hover效果 */
.copy-btn:hover {
  color: #22c55e;
  background-color: rgba(34, 197, 94, 0.05);
}

/* 删除按钮样式 - 对齐广告管理的hover效果 */
.delete-btn:hover {
  color: #ef4444;
  background-color: rgba(239, 68, 68, 0.05);
}

/* 空状态样式 - 完全对齐广告管理 */
.empty-state {
  padding: 70px 0; /* 对齐广告管理的内边距 */
  text-align: center;
  color: #6b7280;
  margin-top: 10px; /* 对齐广告管理的上边距 */
}

.placeholder-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  background-color: #f9fafb;
  border-radius: 50%;
  color: #e5e7eb;
  font-size: 40px;
  font-weight: normal;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #f3f4f6;
}

.empty-text {
  font-size: 16px;
  color: #6b7280;
  margin: 0 0 8px 0;
}

.empty-tip {
  margin-top: 8px;
  color: #9ca3af;
  font-size: 14px;
}

/* 分页组件样式 - 完全对齐广告管理 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px; /* 对齐广告管理的上边距 */
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

.pagination {
  --el-pagination-item-size: 34px;
  --el-pagination-item-font-size: 14px;
  --el-pagination-item-color: #4b5563;
  --el-pagination-item-active-color: #fff;
  --el-pagination-item-active-background-color: #22c55e;
  --el-pagination-item-hover-color: #22c55e;
  --el-pagination-item-hover-background-color: #f0fdf4;
  --el-pagination-border-color: #e5e7eb;
}

.pagination .el-pagination__item {
  border: 1px solid var(--el-pagination-border-color);
  border-radius: 6px;
  margin: 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.pagination .el-pagination__item:not(.is-active):hover {
  border-color: #22c55e;
  color: #22c55e;
}

.pagination .el-pagination__item.is-active {
  border-color: #22c55e;
  background-color: var(--el-pagination-item-active-background-color);
  color: var(--el-pagination-item-active-color);
  font-weight: 600;
}

.pagination .el-pagination__prev,
.pagination .el-pagination__next {
  border: 1px solid var(--el-pagination-border-color);
  border-radius: 6px;
  margin: 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  padding: 0 12px;
}

.pagination .el-pagination__prev:hover,
.pagination .el-pagination__next:hover {
  border-color: #22c55e;
  color: #22c55e;
}

/* 响应式样式 - 对齐广告管理的适配规则 */
@media (max-width: 1200px) {
  .invitation-code-management {
    padding: 24px 20px;
  }

  .code-table-container {
    max-height: 320px;
  }
}

@media (max-width: 768px) {
  .course-filter {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .search-input {
    width: 100%;
  }

  .filter-item-button {
    width: 100%;
  }
}
</style>