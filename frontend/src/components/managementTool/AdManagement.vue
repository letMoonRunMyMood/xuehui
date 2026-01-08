<template>
  <div class="advertisement-management">
    <div class="page-header">
      <h2 class="page-title">广告管理</h2>
      <el-button type="primary" @click="openCreateDialog" class="create-btn">
        <span>添加广告</span>
      </el-button>
    </div>

    <div class="course-filter">
      <input v-model="searchKey" placeholder="搜索广告名称" class="search-input" />
      <el-button @click="filterAds" class="filter-item-button">筛选</el-button>
    </div>

    <div class="ad-list">
      <h3 class="section-title">广告列表</h3>
      <div class="ad-table-container">
        <el-table
          :data="paginatedAds"
          border
          stripe
          style="width: 100%;"
          v-loading="isLoading"
          :header-cell-style="{ background: '#f8f9fa' }"
          :row-style="{ height: '50px' }"
        >
          <el-table-column prop="id" label="ID" width="120" align="center" />
          <el-table-column prop="name" label="广告名称" width="200" align="center" />
          <el-table-column prop="link" label="广告链接" width="300" align="center">
            <template #default="scope">
              <a :href="scope.row.link" target="_blank" class="truncated-link" :title="scope.row.link">
                {{ scope.row.link }}
              </a>
            </template>
          </el-table-column>
          <el-table-column label="图片链接" width="300" align="center">
            <template #default="scope">
              <span class="image-link" :title="fixCoverPath(scope.row.image) || '无图片链接'">
                {{ fixCoverPath(scope.row.image) || '无图片链接' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="215" align="center">
            <template #default="scope">
              <el-button
                type="text"
                size="small"
                @click="previewAd(scope.row)"
                class="action-button preview-btn"
              >
                <el-icon><View /></el-icon>预览
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="deleteAd(scope.row.id)"
                class="action-button delete-btn"
              >
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <div class="empty-state" v-if="filteredAds.length === 0 && !isLoading">
      <div class="empty-icon placeholder-icon">
        <span class="icon">○</span>
      </div>
      <p class="empty-text">暂无广告数据</p>
      <p class="empty-tip" v-if="role === '2'">点击右上角「添加广告」按钮创建新广告</p>
    </div>

    <div class="pagination-container" v-if="filteredAds.length > 0">
      <el-pagination
        class="pagination"
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="filteredAds.length"
        layout="prev, pager, next"
        background
        @current-change="handlePageChange"
      />
    </div>

    <!-- 添加广告弹窗 -->
    <el-dialog title="添加广告" v-model="createDialogVisible" width="800px" destroy-on-close class="create-ad-dialog">
      <el-form :model="formData" :rules="formRules" label-width="120px" class="ad-form">
        <el-form-item label="广告名称" prop="name" class="form-item">
          <el-input v-model="formData.name" placeholder="请输入广告名称" size="large" />
        </el-form-item>
        <el-form-item label="广告链接" prop="link" class="form-item">
          <el-input v-model="formData.link" placeholder="请输入广告链接" size="large" />
        </el-form-item>
        <el-form-item label="广告图片" prop="image" class="form-item">
          <div class="upload-container">
            <!-- 修复1：点击预览区域清空旧数据+触发选择器 -->
            <div 
              v-if="formData.imageUrl" 
              class="upload-preview" 
              @click="handlePreviewClick"
            >
              <img :src="formData.imageUrl" alt="广告图片预览" class="preview-img" />
              <div class="preview-overlay">
                <span class="overlay-text">点击重新上传</span>
              </div>
            </div>
            <!-- 修复2：上传区域强制2:1比例 -->
            <div v-else class="upload-btn-area" @click="handlePreviewClick">
              <el-icon class="upload-icon"><UploadFilled /></el-icon>
              <p class="upload-text">点击上传或拖拽图片至此处</p>
              <p class="upload-desc">建议尺寸：800x400，支持5MB以内的png、jpg、jpeg格式</p>
              <!-- 关键：给input加ref，避免querySelector失效 -->
              <input
                ref="fileInputRef"
                type="file"
                class="file-input"
                accept="image/png, image/jpeg, image/jpg"
                @change="handleFileSelect"
              />
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button size="large" @click="createDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="submitAd" 
          class="confirm-btn"
          :loading="submitLoading"
          size="large"
        >
          确认
        </el-button>
      </template>
    </el-dialog>

    <!-- 图片裁剪弹窗 -->
    <el-dialog title="裁剪广告图片" v-model="cropDialogVisible" width="900px" append-to-body class="crop-ad-dialog">
      <div class="cropper-container">
        <vue-cropper
          ref="cropperRef"
          :img="cropImgUrl"
          :info="true"
          :outputSize="1"
          :outputType="'jpeg'"
          :canScale="true"
          :autoCrop="true"
          :autoCropWidth="800"
          :autoCropHeight="400"
          :fixed="true"
          :fixedNumber="[2, 1]"
          :canMove="true"
          :fixedBox="true"
          class="vue-cropper"
        ></vue-cropper>
      </div>
      <template #footer>
        <el-button @click="cropDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          class="confirm-btn"
          @click="confirmCrop"
        >
          确认裁剪
        </el-button>
      </template>
    </el-dialog>

    <!-- 广告预览弹窗 -->
    <el-dialog title="广告预览" v-model="previewDialogVisible" width="850px" class="preview-ad-dialog">
      <div class="preview-container">
        <a :href="previewAdData.link" target="_blank" class="preview-link">
          <div class="preview-img-wrapper">
            <img
              :src="previewAdData.image || defaultImg"
              class="preview-image"
              alt="广告预览图"
              @error="previewImgError = true"
            />
            <div v-if="previewImgError" class="preview-error">
              图片加载失败，请检查图片链接
            </div>
          </div>
        </a>
        <div class="preview-info">
          <h3>{{ previewAdData.name }}</h3>
          <p>链接: <a :href="previewAdData.link" target="_blank" class="preview-info-link">{{ previewAdData.link }}</a></p>
          <p>图片链接: <a :href="previewAdData.image" target="_blank" class="preview-info-link">{{ previewAdData.image }}</a></p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, UploadFilled } from '@element-plus/icons-vue'
import { VueCropper } from 'vue-cropper'
import 'vue-cropper/dist/index.css'
import axiosInstance from "@/service/api.js"
import { fixCoverPath } from '@/utils/format.js'

const cropperRef = ref(null)
const previewImgError = ref(false)
const defaultImg = 'https://via.placeholder.com/800x400?text=No+Image'
// 关键修复：用ref获取文件输入框
const fileInputRef = ref(null)

const role = ref(sessionStorage.getItem('role') || '0')

const adList = ref([])
const filteredAds = ref([])
const searchKey = ref('')
const pageSize = ref(8)
const currentPage = ref(1)
const isLoading = ref(false)

const createDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const cropDialogVisible = ref(false)
const submitLoading = ref(false)

const formData = reactive({
  name: '',
  link: '',
  image: null,
  imageUrl: '',
  rawFile: null
})

const cropImgUrl = ref('')

const formRules = ref({
  name: [{ required: true, message: '请输入广告名称', trigger: 'blur' }],
  link: [{ required: true, message: '请输入广告链接', trigger: 'blur' }],
  image: [{ required: true, message: '请上传并裁剪广告图片', trigger: 'change' }]
})

const previewAdData = ref({
  id: '',
  name: '',
  link: '',
  image: ''
})

const paginatedAds = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAds.value.slice(start, end)
})

onMounted(() => {
  if (role.value === '2') {
    fetchAds()
  }
})

const fetchAds = async () => {
  isLoading.value = true
  try {
    const res = await axiosInstance.get('/api/admin/get-advertisement')
    if (res.data.success) {
      adList.value = res.data.data.map(ad => ({
        ...ad,
        image: fixCoverPath(ad.image)
      }))
      filterAds()
    } else {
      ElMessage.error(res.data.message || '获取广告列表失败')
    }
  } catch (error) {
    console.error('获取广告列表失败', error)
    ElMessage.error('服务器错误，请检查后端接口')
  } finally {
    isLoading.value = false
  }
}

const filterAds = () => {
  filteredAds.value = searchKey.value
      ? adList.value.filter(item => item.name.toLowerCase().includes(searchKey.value.toLowerCase()))
      : [...adList.value]
  currentPage.value = 1
}

const openCreateDialog = () => {
  formData.name = ''
  formData.link = ''
  formData.image = null
  formData.imageUrl = ''
  formData.rawFile = null
  createDialogVisible.value = true
}

// 核心修复：点击事件 - 清空旧数据 + 触发文件选择器
const handlePreviewClick = () => {
  // 1. 清空旧的图片数据
  formData.imageUrl = ''
  formData.image = null
  formData.rawFile = null
  // 2. 用ref触发文件选择器，比querySelector更可靠
  if (fileInputRef.value) {
    fileInputRef.value.click()
  } else {
    ElMessage.warning('文件选择器未加载，请重试')
  }
}

const beforeFileUpload = (file) => {
  const isAllowed = ['image/png', 'image/jpeg', 'image/jpg'].includes(file.type);
  const isLessThan5M = file.size / 1024 / 1024 < 5;

  if (!isAllowed) {
    ElMessage.error('请上传png、jpg或jpeg格式的图片');
  }
  if (!isLessThan5M) {
    ElMessage.error('图片大小不能超过5MB');
  }
  return isAllowed && isLessThan5M;
}

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (!file) return

  if (!beforeFileUpload(file)) {
    e.target.value = ''
    return
  }

  formData.rawFile = file
  cropImgUrl.value = URL.createObjectURL(file)
  cropDialogVisible.value = true
  e.target.value = ''
}

const confirmCrop = () => {
  if (!cropperRef.value) return;
  
  cropperRef.value.getCropBlob((blob) => {
    const croppedFile = new File([blob], `cropped-ad-${Date.now()}.${formData.rawFile.type.split('/')[1]}`, { 
      type: formData.rawFile.type 
    });
    formData.imageUrl = URL.createObjectURL(blob);
    formData.image = croppedFile;
    cropDialogVisible.value = false;
    ElMessage.success('图片裁剪完成');
  });
}

const submitAd = async () => {
  if (!formData.name || !formData.link || !formData.image) {
    return ElMessage.warning('请完善广告信息并上传图片')
  }

  submitLoading.value = true
  try {
    const form = new FormData()
    form.append('name', formData.name)
    form.append('link', formData.link)
    form.append('image', formData.image)

    const res = await axiosInstance.post('/api/admin/create-advertisement', form)

    if (res.data.success) {
      ElMessage.success('广告创建成功')
      createDialogVisible.value = false
      fetchAds()
    } else {
      ElMessage.error(res.data.message || '创建失败')
    }
  } catch (error) {
    console.error('创建广告失败', error)
    ElMessage.error('服务器错误，请检查后端接口')
  } finally {
    submitLoading.value = false
  }
}

const previewAd = (ad) => {
  previewImgError.value = false
  previewAdData.value = { 
    ...ad,
    image: fixCoverPath(ad.image)
  }
  previewDialogVisible.value = true
}

const deleteAd = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该广告？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(async () => {
      try {
        const res = await axiosInstance.delete('/api/admin/delete-advertisement', {
          data: { advertisement_id: id }
        })

        if (res.data.success) {
          ElMessage.success('删除成功')
          fetchAds()
        } else {
          ElMessage.error(res.data.message || '删除失败')
        }
      } catch (error) {
        console.error('删除广告失败', error)
        ElMessage.error('服务器错误，请检查后端接口')
      }
    }).catch((err) => {
      if (err === 'cancel') {
        ElMessage.info('已取消删除操作')
      } else {
        console.error('删除操作异常', err)
      }
    })
  } catch (error) {
    console.error('删除广告函数异常', error)
  }
}

const handlePageChange = (newPage) => {
  currentPage.value = newPage
}
</script>

<style scoped>
.advertisement-management {
  flex: 1;
  background-color: #ffffff;
  padding: 28px 32px;
  border-radius: 12px;
  box-sizing: border-box;
  height: 600px;
  margin: 0 auto;
  max-width: 1400px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  letter-spacing: 0.2px;
}

.create-btn {
  padding: 0 24px;
  font-size: 15px;
  width: 120px;
  height: 42px;
  transition: all 0.2s ease-in-out;
  background-color: #22c55e !important;
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

.course-filter {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

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

.ad-list {
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

.ad-table-container {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  max-height: 350px;
  overflow-y: auto;
  width: 100%;
  border: 1px solid #f3f4f6;
}

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

.truncated-link, .image-link {
  display: inline-block;
  max-width: 250px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: middle;
  color: #22c55e;
  text-decoration: none;
}

.truncated-link:hover {
  color: #16a34a;
  text-decoration: underline;
}

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

.preview-btn:hover {
  color: #22c55e;
  background-color: rgba(34, 197, 94, 0.05);
}

.delete-btn:hover {
  color: #ef4444;
  background-color: rgba(239, 68, 68, 0.05);
}

.empty-state {
  padding: 70px 0;
  text-align: center;
  color: #6b7280;
  margin-top: 10px;
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

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
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

:deep(.create-ad-dialog .el-dialog__body) {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

:deep(.crop-ad-dialog .el-dialog__body) {
  padding: 20px;
  padding-bottom: 30px;
}

.vue-cropper {
  height: 450px;
  margin-bottom: 20px;
  width: 100%;
}

:deep(.preview-ad-dialog .el-dialog__body) {
  padding: 20px;
}

.ad-form {
  width: 100%;
}

.form-item {
  width: 100%;
  margin-bottom: 20px !important;
  display: flex;
  align-items: center;
}

.ad-form .el-form-item__label {
  width: 120px;
  flex-shrink: 0;
  text-align: left;
  padding-top: 2px;
  font-size: 16px;
  color: #4b5563;
  font-weight: 500;
}

.ad-form .el-form-item__content {
  width: calc(100% - 120px);
  padding-left: 20px;
  box-sizing: border-box;
}

.ad-form .el-input {
  width: 100%;
  height: 36px;
}

.upload-container {
  width: 100%;
}

/* 核心修复3：强制上传/预览区域 2:1 比例 */
.upload-btn-area, .upload-preview {
  width: 100%;
  /* 强制2:1比例 */
  aspect-ratio: 2 / 1;
  border: 2px dashed #e5e7eb;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f9fafb;
  position: relative;
  overflow: hidden;
}

.upload-btn-area:hover, .upload-preview:hover {
  border-color: #22c55e;
  background-color: #f0fdf4;
}

.upload-icon {
  font-size: 60px;
  color: #9ca3af;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 18px;
  color: #4b5563;
  margin-bottom: 10px;
  font-weight: 500;
}

.upload-desc {
  font-size: 14px;
  color: #9ca3af;
  text-align: center;
  max-width: 90%;
}

.file-input {
  display: none;
}

/* 预览图保持比例 */
.preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.upload-preview:hover .preview-overlay {
  opacity: 1;
}

.overlay-text {
  color: white;
  font-size: 18px;
  font-weight: 500;
}

:deep(.confirm-btn) {
  background-color: #22c55e !important;
  border-color: #22c55e !important;
  padding: 0 20px !important;
  height: 36px !important;
  font-size: 16px !important;
}

:deep(.confirm-btn:hover) {
  background-color: #16a34a !important;
  border-color: #16a34a !important;
}

.cropper-container {
  width: 100%;
}

.preview-container {
  text-align: center;
  padding: 10px 0;
}

.preview-img-wrapper {
  width: 100%;
  aspect-ratio: 2 / 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f9fafb;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
}

.preview-image {
  max-width: 95%;
  max-height: 95%;
  object-fit: contain;
}

.preview-error {
  color: #f56c6c;
  margin-top: 10px;
  font-size: 14px;
}

.preview-info {
  text-align: left;
  padding: 0 20px;
  background-color: #f9fafb;
  padding: 16px;
  border-radius: 8px;
}

.preview-info h3 {
  font-size: 18px;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.preview-info p {
  font-size: 14px;
  color: #4b5563;
  margin: 0 0 8px 0;
}

.preview-info-link {
  color: #22c55e;
  text-decoration: none;
  word-break: break-all;
}

.preview-info-link:hover {
  color: #16a34a;
  text-decoration: underline;
}

@media (max-width: 1200px) {
  .advertisement-management {
    padding: 24px 20px;
  }

  .ad-table-container {
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

  .vue-cropper {
    height: 300px;
  }
}
</style>