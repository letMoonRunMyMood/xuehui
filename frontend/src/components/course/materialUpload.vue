<template>
  <!-- 模板部分保持不变 -->
  <div class="custom-dialog" v-if="visible">
    <!-- 遮罩层 -->
    <div class="dialog-mask" @click="handleClose"></div>

    <!-- 对话框主体 -->
    <div class="dialog-container">
      <!-- 头部 -->
      <div class="dialog-header">
        <h3>添加资料</h3>
        <button class="close-btn" @click="handleClose">×</button>
      </div>

      <!-- 内容区域 -->
      <div class="dialog-content">
        <form class="form-container">
          <!-- 资料名称 -->
          <div class="form-group row">
            <label class="col-label">资料名称：</label>
            <div class="col-control">
              <input
                  type="text"
                  v-model="form.name"
                  placeholder="请输入资料名称"
                  class="form-input"
              >
              <span class="error-message" v-if="errors.name">{{ errors.name }}</span>
            </div>
          </div> 
          <!-- 分隔线 -->
          <div class="divider"></div>
          <!-- 选择文件 -->
          <div class="form-group row">
            <label class="col-label">选择文件：</label>
            <div class="col-control">
              <div v-if="!form.file" class="file-upload-container">
                <input
                    type="file"
                    id="file-upload-input"
                    ref="fileInput"
                    @change="handleFileChange($event.target.files[0])"
                >
                <label for="file-upload-input" class="primary-btn">
                  选择文件
                </label>
              </div>
              <div class="file-info" v-else>
                {{ form.file.name }}
                <button type="button" class="remove-btn" @click="handleFileRemove">×</button>
              </div>
              <span class="error-message" v-if="errors.file">{{ errors.file }}</span>
            </div>
          </div>
          <!-- 分隔线 -->
          <div class="divider"></div>
          <!-- 资料类型 -->
          <div class="form-group row">
            <label class="col-label">资料类型：</label>
            <div class="col-control">
              <select v-model="form.type" @change="handleTypeChange" class="form-select">
                <option value="">请选择资料类型</option>
                <option value="doc">文档</option>
                <option value="video">视频</option>
              </select>
              <span class="error-message" v-if="errors.type">{{ errors.type }}</span>
            </div>
          </div> 
          <!-- 分隔线 -->
          <div class="divider"></div>
          <!-- 视频排序（按需显示） -->
          <div class="form-group row" v-if="form.type === 'video'">
            <label class="col-label">视频排序：</label>
            <div class="col-control">
              <input
                  type="number"
                  v-model.number="form.order"
                  min="1"
                  step="1"
                  placeholder="视频排序"
                  class="form-input"
              >
              <span class="error-message" v-if="errors.order">{{ errors.order }}</span>
            </div>
          </div>
        </form>
      </div>
      <!-- 底部按钮 -->
      <div class="dialog-footer">
        <button class="cancel-btn" @click="handleClose">取消</button>
        <button class="submit-btn" @click="submitForm" :disabled="isUploading">
          添加
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axiosInstance from '@/service/api.js'

const props = defineProps({
  visible: { type: Boolean, default: false },
  chapterId: { type: Number, required: true },
  courseId: { type: Number, default: 0 }
}) 

const emit = defineEmits(['update:visible', 'refresh-data', 'close'])

const fileInput = ref(null)
const form = reactive({
  name: '',
  type: 'doc',
  chapter_id: props.chapterId,
  file: null,
  order: 1
})

const errors = reactive({
  name: '',
  file: '',
  type: '',
  order: ''
})

const isFileUploaded = ref(false)
const isUploading = ref(false)
const currentMaxOrder = ref(0) // 记录当前章节最大视频排序

// --- 修改开始 ---

// 文档文件类型校验 (与后端保持一致)
const allowedDocExt = ['pdf', 'doc', 'docx', 'ppt', 'pptx']
// 视频文件类型校验
const allowedVideoExt = ['mp4', 'mov', 'avi', 'mkv', 'webm']
// 文件大小限制 (与后端保持一致，50MB)
const maxFileSize = 50 * 1024 * 1024 

// --- 修改结束 ---

// 处理文件选择
const handleFileChange = (file) => {
  if (!file) return

  const ext = file.name.split('.').pop().toLowerCase()

  // --- 修改开始 ---

  // 根据不同的资料类型校验文件格式
  if (form.type === 'doc' && !allowedDocExt.includes(ext)) {
    ElMessage.error('文档仅支持pdf、doc、docx、ppt、pptx格式')
    return
  }
  if (form.type === 'video' && !allowedVideoExt.includes(ext)) {
    ElMessage.error('视频仅支持mp4、mov、avi、mkv、webm格式')
    return
  }

  // --- 修改结束 ---

  // 校验文件大小
  if (file.size > maxFileSize) {
    // --- 修改开始 ---
    ElMessage.error('文件大小不能超过50MB')
    // --- 修改结束 ---
    return
  }

  form.file = file
  validateFile()
}

const handleFileRemove = () => {
  form.file = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  errors.file = ''
}

// 处理资料类型变更
const handleTypeChange = () => {
  if (form.type === 'video') {
    form.order = currentMaxOrder.value + 1
  } else {
    form.order = 1
  }
  validateType()
  // 当类型改变时，清空已选文件，防止类型不匹配
  if (form.file) {
      handleFileRemove();
  }
}

// 关闭弹窗
const handleClose = () => {
  emit('update:visible', false)
  emit('close')
  resetForm()
}

// 重置表单
const resetForm = () => {
  form.name = ''
  form.type = 'doc'
  form.chapter_id = props.chapterId
  form.file = null
  form.order = 1
  isFileUploaded.value = false
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })
  if (fileInput.value) {
    fileInput.value.value = ''
  }
} 
// 表单验证
const validateName = () => {
  if (!form.name.trim()) {
    errors.name = '请输入资料名称'
    return false
  }
  errors.name = ''
  return true
}

const validateFile = () => {
  if (!form.file) {
    errors.file = '请选择上传文件'
    return false
  }
  errors.file = ''
  return true
}

const validateType = () => {
  if (!form.type) {
    errors.type = '请选择资料类型'
    return false
  }
  errors.type = ''
  return true
}

const validateOrder = () => {
  if (form.type === 'video' && (!form.order || isNaN(form.order) || form.order < 1)) {
    errors.order = '请输入有效的视频排序'
    return false
  }
  errors.order = ''
  return true
}

// 提交表单
const submitForm = () => {
  const isValid = validateName() && validateFile() && validateType() && validateOrder()

  if (isValid) {
    uploadResource()
  }
}

// 上传资源
const uploadResource = async () => {
  isUploading.value = true

  try {
    const actionUrl = form.type === 'video'
        ? '/api/course/upload-video'
        : '/api/course/upload-document' 

    const formData = new FormData()
    formData.append('title', form.name)
    formData.append('type', form.type)
    formData.append('chapter_id', form.chapter_id)

    if (form.type === 'video') {
      formData.append('order', form.order.toString())
      formData.append('video', form.file)
    } else {
      formData.append('document', form.file)
    }

    const res = await axiosInstance.post(
        actionUrl,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
    )

    if (res.data.success) {
      ElMessage.success('资料添加成功')
      emit('refresh-data')
      emit('update:visible', false)
      isFileUploaded.value = true

      // 更新当前最大排序值
      if (form.type === 'video') {
        currentMaxOrder.value = Math.max(currentMaxOrder.value, form.order)
      }
    } else {
      ElMessage.error(res.data.message || '资料添加失败')
    }
  } catch (error) {
    console.error('上传资料失败:', error)
    // 更友好的错误提示
    if (error.response && error.response.data && error.response.data.message) {
        ElMessage.error(`上传失败: ${error.response.data.message}`);
    } else {
        ElMessage.error('资料添加失败，请检查网络或联系管理员')
    }
  } finally {
    isUploading.value = false
  }
}    
// 重置文件上传状态
const resetFileUpload = () => {
  isFileUploaded.value = false
  handleFileRemove()
}

// 组件挂载时获取当前章节最大视频排序
onMounted(() => {
  if (props.chapterId) {
    fetchMaxVideoOrder(props.chapterId)
  }
})

// 获取当前章节最大视频排序
const fetchMaxVideoOrder = async (chapterId) => {
  try {
    // 由于后端没有提供专门接口，我们通过课程详情接口获取
    const res = await axiosInstance.get('/api/course/get-course-detail', {
      params: { course_id: props.courseId || 0 } // 假设从父组件获取courseId
    })

    if (res.data.success) {
      const courseData = res.data.data
      const chapter = courseData.chapters.find(ch => ch.id === chapterId)
      if (chapter) {
        const videos = chapter.videos || []
        currentMaxOrder.value = videos.length ? Math.max(...videos.map(v => v.order)) : 0
      } else {
        currentMaxOrder.value = 0
      }
    } else {
      currentMaxOrder.value = 0
      ElMessage.warning(res.data.message || '获取视频排序失败，将从1开始排序')
    }
  } catch (error) {
    console.error('获取视频排序失败:', error)
    currentMaxOrder.value = 0
    ElMessage.warning('网络错误，获取视频排序失败，将从1开始排序')
  }
}

// 监听visible变化，重置表单
watch(() => props.visible, (newVal) => {
  if (newVal) {
    resetForm()
  }
})
</script>

<style scoped>
/* 样式部分保持不变 */
/* 基础样式 */
.custom-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.dialog-container {
  position: relative;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 520px;
  max-height: 90vh;
  overflow: hidden;
}

/* 头部样式 */
.dialog-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #999;
  cursor: pointer;
  padding: 0 6px;
  border-radius: 50%;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #666;
  background-color: #f5f5f5;
}

/* 内容区域样式 */
.dialog-content {
  padding: 24px;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group.row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.col-label {
  width: 100px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
  padding-top: 8px;
  text-align: left;
}

.col-control {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-input,
.form-select {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  border: 1px solid #d9d9d9; /* 明确设置边框 */
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #206644;
  box-shadow: 0 0 0 2px rgba(32, 102, 68, 0.2);
}

.form-input::placeholder {
  color: #999;
}

.form-select {
  appearance: none;
  background-image: none;
  padding-right: 30px;
  position: relative;
}

.form-select:after {
  content: "▼";
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #909399;
  font-size: 12px;
}

.form-select::-ms-expand {
  display: none;
}

.error-message {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 2px;
}

.divider {
  height: 1px;
  background-color: #e5e5e5;
  margin: 16px 0;
}

/* 文件上传样式 */
input[type="file"] {
  display: none;
}

.file-upload-container {
  display: inline-flex;
  align-items: center;
}

.primary-btn {
  background-color: #206644;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 0 16px;
  cursor: pointer;
  font-size: 14px;
  height: 36px;
  display: inline-flex;
  justify-content: flex-start;
  align-items: center;
  transition: background-color 0.2s;
}

.primary-btn:hover {
  background-color: #185034;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #333;
  padding: 8px 12px;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  background-color: #f9f9f9;
  min-height: 36px;
}

.remove-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 14px;
  transition: color 0.2s;
}

.remove-btn:hover {
  color: #f56c6c;
}

/* 底部按钮 */
.dialog-footer {
  padding: 16px 24px;
  border-top: 1px solid #e5e5e5;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background-color: #f8f9fa;
}

.cancel-btn,
.submit-btn {
  padding: 0 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  transition: all 0.2s;
}

.cancel-btn {
  background: #fff;
  border: 1px solid #d9d9d9;
  color: #666;
}

.cancel-btn:hover {
  background-color: #f5f5f5;
}

.submit-btn {
  background-color: #206644;
  color: #fff;
  border: none;
}

.submit-btn:hover {
  background-color: #185034;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>