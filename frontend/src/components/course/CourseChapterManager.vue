<template>
  <el-dialog
      :model-value="dialogVisible"
      :title="course.title ? `当前课程: ${course.title}` : '课程章节与资源管理'"
      class="chapter-resource-dialog"
      width="1300px"
      @close="handleClose"
  >
    <div class="management-container">
      <!-- 左侧章节列表 -->
      <div class="sidebar">
        <div
            v-for="(chapter, chapterIndex) in courseChapters"
            :key="chapter.id"
            class="chapter-item"
            @click="toggleChapter(chapter)"
            @dragstart="handleChapterDragStart($event, chapter, chapterIndex)"
            draggable="true"
            :class="{
              'chapter-expanded': chapter.expanded,
              'chapter-hover': isChapterHovered(chapter.id),
              'dragging': isDragging && draggedItemType === 'chapter' && draggedChapterIndex === chapterIndex
            }"
            :data-id="chapter.id"
            @mouseenter="handleChapterMouseEnter(chapter.id)"
            @mouseleave="handleChapterMouseLeave(chapter.id)"
        >
          <div class="chapter-header">
            <div class="chapter-info">
              <span class="chapter-index">第{{ chapterIndex + 1 }}章</span>
              <span class="chapter-title">{{ chapter.title || '未命名章节' }}</span>
              <span class="resource-count">({{ getResourceCount(chapter.resources) }}个资料)</span>
            </div>
            <el-button
                type="text"
                icon="el-icon-edit"
                size="default"
                @click.stop="openEditChapter(chapter, chapterIndex)">
              编辑
            </el-button>
          </div>
          <div class="chapter-content" v-if="chapter.expanded">
            <div v-if="chapter.resources.length > 0" class="resource-list">
              <div
                  v-for="(resource, resIndex) in chapter.resources"
                  :key="resource.id"
                  class="resource-item"
                  @click.stop="loadResourceDetails(resource)"
                  @dragstart.stop="handleResourceDragStart($event, chapter.id, resource, resIndex)"
                  draggable="true"
                  :class="{
                    'resource-hover': isResourceHovered(resource.id),
                    'dragging': isDragging && draggedItemType === 'resource' && draggedResourceChapterId === chapter.id && draggedResourceIndex === resIndex
                  }"
                  :data-id="resource.id"
                  @mouseenter="handleResourceMouseEnter(resource.id)"
                  @mouseleave="handleResourceMouseLeave(resource.id)"
              >
                <div class="resource-header">
                  <div class="resource-title-container">
                    <el-icon :size="16" :class="getFileIconClass(resource.type)"></el-icon>
                    <span class="resource-type-tag">{{ getFileExtension(resource.type) }}</span>
                    <span class="resource-title">{{ resource.title || '未命名资源' }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-resource">
              <el-icon size="20"><Document /></el-icon>
              <span class="no-material-info">该章节暂无资料</span>
            </div>
            <div class="add-resource-dashed" @click.stop="openAddResourceDialog(chapter.id)">
              <span class="dashed-text">
                添加资料
              </span>
            </div>
          </div>
        </div>
        <div class="add-chapter-dashed" @click="openAddChapterDialog">
          <span class="dashed-text">
            添加新章节
          </span>
        </div>
        <div class="trash-container" @dragover.prevent="handleDragOver" @drop="handleDrop">
          <div class="trash-icon" :class="{ 'trash-active': isDragOver }">
            拖此删除
          </div>
        </div>
      </div>
      <!-- 右侧预览区 -->
      <div class="preview-area">
        <h3 class="nav-title">资料预览</h3>
        <div class="preview-container">
          <div v-if="previewResourceInfo" class="preview-content">
            <div class="preview-body">
              <div v-if="isLoadingResource" class="loading-preview">
                <el-skeleton animated />
              </div>
              <div v-else class="file-preview-area">
                <div v-if="previewResourceInfo.type === 'video'" class="video-preview">
                  <div class="video-wrapper">
                    <video
                        ref="videoRef"
                        controls
                        width="80%"
                        style="aspect-ratio: 16/9;"
                        @error="handleVideoError"
                        @loadeddata="handleVideoLoaded"
                    >
                      <source :src="previewResourceInfoUrl" :type="getVideoMimeType(previewResourceInfoUrl)">
                      您的浏览器不支持视频播放
                    </video>
                    <div v-if="videoError" class="video-error">
                      <el-icon size="16"><Error /></el-icon>
                      <span>视频加载失败，请检查文件路径或尝试下载查看</span>
                    </div>
                  </div>
                </div>
                <!-- DOC/DOCX 预览 -->
                <div v-else-if="['doc', 'docx'].includes(previewResourceInfo.type)" class="doc-preview">
                  <div v-if="docContent" class="doc-content">
                    <div class="doc-header">
                      <h3>{{ previewResourceInfo.title || '文档内容' }}</h3>
                      <div class="doc-actions">
                        <el-button @click="downloadResource(previewResourceInfo)" type="primary" size="default">下载
                        </el-button>
                      </div>
                    </div>
                    <div class="doc-text" v-html="docContent"></div>
                  </div>
                  <div v-else-if="isLoadingDoc" class="loading-doc">
                    <el-skeleton animated />
                  </div>
                  <div v-else class="error-doc">
                    <el-icon size="24"><Error /></el-icon>
                    <p>{{ docError || '文档加载失败，请尝试下载查看' }}</p>
                  </div>
                </div>
                <!-- PDF 预览 -->
                <div v-else-if="previewResourceInfo.type === 'pdf'" class="pdf-preview">
                  <div class="pdf-container" style="width: 750px; height: 500px;">
                    <div v-if="!previewResourceInfoUrl" class="no-pdf-url">
                      <p>暂无文档链接可预览</p>
                    </div>
                    <iframe
                        v-else
                        :src="previewResourceInfoUrl + '?t=' + pdfTimestamp"
                        width="100%"
                        height="100%"
                        class="pdf-iframe"
                        @load="handlePdfLoad"
                        @error="handlePdfError"
                    ></iframe>
                    <div v-if="isPdfLoading" class="loading-pdf">加载中...</div>
                    <div v-else-if="pdfError" class="pdf-error">文档加载失败，请检查文件路径或尝试下载</div>
                  </div>
                </div>
                
                <!-- TXT 预览 -->
                <div v-else-if="previewResourceInfo.type === 'txt'" class="txt-preview">
                  <div v-if="txtContent" class="txt-content">
                    <pre>{{ txtContent }}</pre>
                  </div>
                  <div v-else-if="isLoadingTxt" class="loading-txt">加载中...</div>
                  <div v-else class="error-txt">文本加载失败</div>
                </div>

                <!-- PPT/PPTX 预览 -->
                <div v-else-if="['ppt', 'pptx'].includes(previewResourceInfo.type)" class="ppt-preview">
                  <div v-if="pptxLoading" class="loading-pptx">加载中...</div>
                  <div v-if="pptxError" class="error-pptx">
                    <el-icon size="16"><Error /></el-icon>
                    <span>演示文稿加载失败，请尝试下载查看</span>
                  </div>
                  <VueOfficePptx
                      v-else
                      :src="previewResourceInfoUrl"
                      style="width: 750px; height: 600px; margin: 0 auto;"
                      @rendered="pptxLoading = false"
                      @error="handlePptxError"
                  />
                  <div class="preview-actions">
                    <el-button type="text" size="default" v-if="previewResourceInfoUrl" @click="openInNewTab(previewResourceInfoUrl)">新窗口打开</el-button>
                    <el-button type="primary" size="default" @click="downloadResource(previewResourceInfo)">下载文件</el-button>
                  </div>
                </div>
                <!-- 其他文件类型 -->
                <div v-else class="other-document-preview">
                  <el-icon :size="40" class="file-icon"></el-icon>
                  <div class="file-info">
                    <h4>{{ previewResourceInfo.title || '未知文件' }}</h4>
                    <p>类型: {{ getFileExtension(previewResourceInfo.type) }}</p>
                    <p>大小: {{ formatFileSize(previewResourceInfo.size) || '-' }}</p>
                    <div class="preview-actions">
                      <el-button type="primary" size="small" @click="downloadResource(previewResourceInfo)">下载文件</el-button>
                      <el-button type="text" size="small" v-if="previewResourceInfoUrl" @click="openInNewTab(previewResourceInfoUrl)">新窗口打开</el-button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-preview">
            <p>请选择左侧资料进行预览</p>
          </div>
        </div>
      </div>
    </div>
    <!-- 添加章节弹窗 -->
    <el-dialog
        :model-value="addChapterVisible"
        title="添加章节"
        width="400px"
        class="small-dialog"
        @close="addChapterVisible = false"
    >
      <el-form :model="newChapter" label-width="80px">
        <el-form-item label="章节标题" prop="title">
          <el-input v-model="newChapter.title" placeholder="请输入章节标题" />
        </el-form-item>
        <el-form-item label="章节排序" prop="order">
          <el-input-number v-model="newChapter.order" :min="1" :default-value="getDefaultOrder()" :step="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addChapterVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAddChapter">确认添加</el-button>
        </div>
      </template>
    </el-dialog>
    <!-- 编辑章节弹窗 -->
    <el-dialog
        :model-value="editChapterVisible"
        title="编辑章节"
        width="400px"
        class="small-dialog"
        @close="editChapterVisible = false"
    >
      <el-form :model="editChapter" label-width="80px">
        <el-form-item label="章节标题" prop="title">
          <el-input v-model="editChapter.title" placeholder="请输入章节标题" />
        </el-form-item>
        <el-form-item label="章节排序" prop="order">
          <el-input-number v-model="editChapter.order" :min="1" :step="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editChapterVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmEditChapter">确认修改</el-button>
        </div>
      </template>
    </el-dialog>
    <!-- 添加资源 - 使用子组件 -->
    <MaterialAddDialog
        v-if="addResourceChapterId !== null"
        :visible="addResourceVisible"
        :chapter-id="addResourceChapterId"
        :course-id="props.course.id"
        @update:visible="addResourceVisible = $event"
        @refresh-data="handleRefreshData"
    />
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox, ElIcon } from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { saveAs } from 'file-saver'
import axiosInstance from "@/service/api.js";
import MaterialAddDialog from './materialUpload.vue'
import VueOfficePptx from '@vue-office/pptx'
import * as mammoth from 'mammoth';
import * as docx from 'docx';
import {Document} from "@element-plus/icons-vue";

// [IMPORTANT] 导入路径修正函数
import { fixCoverPath } from '@/utils/format.js'

const props = defineProps({
  visible: { type: Boolean, default: false },
  course: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['close', 'update:course'])

// 响应式数据
const addResourceVisible = ref(false)
const dialogVisible = ref(props.visible)
const courseChapters = ref([])
const previewResourceInfo = ref(null)
const previewResourceInfoUrl = ref('')
const isLoadingResource = ref(false)
const isPdfLoading = ref(false)
const pdfError = ref(false)
const pdfTimestamp = ref(0)
const addChapterVisible = ref(false)
const editChapterVisible = ref(false)
const addResourceChapterId = ref(null)
const newChapter = ref({ title: '', course_id: props.course.id || 0, order: 1 })
const editChapter = ref({ id: '', title: '', course_id: props.course.id || 0, order: 1 })
const isDragging = ref(false)
const isDragOver = ref(false)
const draggedItemType = ref('')
const draggedChapterIndex = ref(-1)
const draggedChapterId = ref(null)
const draggedResourceIndex = ref(-1)
const draggedResourceId = ref(null)
const draggedResourceChapterId = ref(null)
const chapterHovered = ref({})
const resourceHovered = ref({})
const videoError = ref(false)
const videoRef = ref('')
const txtContent = ref('')
const isLoadingTxt = ref(false)
const pptxLoading = ref(false)
const pptxError = ref('')
const docContent = ref('')
const isLoadingDoc = ref(false)
const docError = ref('')
const { Error, Download, CircleClose } = ElementPlusIconsVue

const handleClose = () => {
  dialogVisible.value = false
  emit('close')
  resetData()
}

const resetData = () => {
  addChapterVisible.value = false
  editChapterVisible.value = false
  addResourceChapterId.value = null
  newChapter.value = { title: '', course_id: props.course.id || 0, order: 1 }
  editChapter.value = { id: '', title: '', course_id: props.course.id || 0, order: 1 }
  resetDragState()
  previewResourceInfo.value = null
  previewResourceInfoUrl.value = ''
  isLoadingResource.value = false
  chapterHovered.value = {}
  resourceHovered.value = {}
  resetPreviewState()
}

const loadChapters = async () => {
  if (!props.course.id) return
  try {
    const response = await axiosInstance.get('/api/course/get-course-detail', { params: { course_id: props.course.id } })
    if (response.data.success) {
      const courseData = response.data.data
      courseChapters.value = (courseData.chapters || []).map(chapter => {
        const resources = [
          ...(chapter.videos || []).map(video => ({ ...video, type: 'video', file: fixCoverPath(video.file_url), size: video.size || 0 })),
          ...(chapter.documents || []).map(doc => ({ ...doc, type: getFileTypeFromExt(doc.file_url), file: fixCoverPath(doc.file_url), size: doc.size || 0 }))
        ]
        return { ...chapter, expanded: false, resources: normalizeResources(resources) }
      })
      emit('update:course', courseData)
    } else {
      ElMessage.error(response.data.message || '获取章节失败')
    }
  } catch (error) {
    ElMessage.error('网络错误：获取章节数据失败，请重试')
    console.error('[错误] 网络异常:', error)
  }
}

const getFileTypeFromExt = (url) => {
  if (!url) return 'doc';
  const ext = url.split('.').pop().toLowerCase();
  const videoExts = ['mp4', 'mov', 'avi', 'mkv', 'webm', 'flv', 'wmv', 'mpg', 'mpeg'];
  const docExts = ['doc', 'docx', 'txt', 'pdf', 'rtf', 'wps'];
  const presentationExts = ['ppt', 'pptx', 'key', 'odp'];
  if (videoExts.includes(ext)) return 'video';
  if (presentationExts.includes(ext)) return 'ppt';
  if (docExts.includes(ext)) return ext === 'pdf' ? 'pdf' : ext === 'txt' ? 'txt' : 'doc';
  return 'doc';
};

const normalizeResources = (resources) => {
  if (!resources || !Array.isArray(resources)) return []
  return resources.map(resource => ({ ...resource, type: mapResourceType(resource.type) }))
}

const mapResourceType = (type) => {
  const videoTypes = ['mp4', 'mov', 'avi', 'mkv', 'webm', 'video'];
  const presentationTypes = ['ppt', 'pptx'];
  const docTypes = ['doc', 'docx', 'pdf', 'txt'];
  if (videoTypes.includes(type)) return 'video';
  if (presentationTypes.includes(type)) return 'ppt';
  if (docTypes.includes(type)) return type === 'pdf' ? 'pdf' : type === 'txt' ? 'txt' : 'doc';
  return 'doc';
}

const isVideoFile = (type) => type === 'video'
const isDocFile = (type) => ['doc', 'pdf', 'txt'].includes(type)
const isPptFile = (type) => ['ppt', 'pptx'].includes(type)

const loadResourceDetails = async (resource) => {
  isLoadingResource.value = true
  resetPreviewState()
  try {
    let response
    if (isVideoFile(resource.type)) {
      response = await axiosInstance.get('/api/course/get-video', { params: { video_id: resource.id } })
    } else {
      response = await axiosInstance.get('/api/course/get-document', { params: { document_id: resource.id } })
    }
    if (response.data.success) {
      const resourceData = response.data.data
      const originalUrl = resourceData.url
      const finalType = getFileTypeFromExt(originalUrl) || resource.type

      previewResourceInfo.value = { ...resource, ...resourceData, type: finalType }
      previewResourceInfoUrl.value = fixCoverPath(originalUrl)

      if (['doc', 'docx'].includes(finalType)) {
        await loadDocContent(previewResourceInfoUrl.value, finalType)
      } else if (finalType === 'txt') {
        await loadTxtContent()
      } else if (isPptFile(finalType)) {
        pptxLoading.value = true
        pptxError.value = ''
      } else if (finalType === 'pdf') {
        isPdfLoading.value = true
        pdfTimestamp.value = new Date().getTime() // 防止PDF缓存
      }
    } else {
      previewResourceInfo.value = { ...resource, title: '加载失败', url: '', type: resource.type }
      previewResourceInfoUrl.value = ''
      ElMessage.error(response.data.message || '获取资源详情失败')
    }
  } catch (error) {
    previewResourceInfo.value = { ...resource, title: '加载失败', url: '', type: resource.type }
    previewResourceInfoUrl.value = ''
    ElMessage.error('获取资源详情失败，请重试')
    console.error("Load resource error:", error)
  } finally {
    isLoadingResource.value = false
  }
}

const loadDocContent = async (url, type) => {
  isLoadingDoc.value = true
  docContent.value = ''
  docError.value = ''
  try {
    const response = await axiosInstance.get(url, { responseType: 'arraybuffer' })
    const arrayBuffer = response.data
    if (type === 'docx' || url.toLowerCase().endsWith('.docx')) {
      const result = await mammoth.convertToHtml({ arrayBuffer })
      if (result.messages.some(msg => msg.type === 'error')) throw new Error('文档内容解析错误')
      docContent.value = result.value
    } else if (type === 'doc' || url.toLowerCase().endsWith('.doc')) {
      try {
        const doc = new docx.Document(arrayBuffer)
        const text = doc.getFullText()
        docContent.value = text.replace(/\n/g, '<br>').replace(/\s{2,}/g, ' ').trim()
      } catch (docxError) {
        const decoder = new TextDecoder('utf-8', { fatal: false })
        const textContent = decoder.decode(arrayBuffer)
        docContent.value = textContent.trim() ? textContent.replace(/\n/g, '<br>') : ''
        if (!docContent.value) throw new Error('无法解析DOC文件内容')
      }
    }
  } catch (error) {
    console.error('文档解析失败:', error)
    docError.value = '文档加载失败，请尝试下载查看'
  } finally {
    isLoadingDoc.value = false
  }
}

const loadTxtContent = async () => {
  isLoadingTxt.value = true
  try {
    const response = await axiosInstance.get(previewResourceInfoUrl.value, { responseType: 'text' })
    txtContent.value = response.data
  } catch (error) {
    console.error('Failed to load TXT content:', error)
    txtContent.value = ''
  } finally {
    isLoadingTxt.value = false
  }
}

const resetPreviewState = () => {
  txtContent.value = ''
  isLoadingTxt.value = false
  pptxLoading.value = false
  pptxError.value = ''
  videoError.value = false
  isPdfLoading.value = false
  pdfError.value = false
  docContent.value = ''
  isLoadingDoc.value = false
  docError.value = ''
}

const handlePptxError = (error) => {
  pptxError.value = '演示文稿加载失败，请尝试下载查看'
  pptxLoading.value = false
  console.error('PPT文档加载错误:', error)
}

const toggleChapter = (chapter) => {
  courseChapters.value = courseChapters.value.map(ch => ({ ...ch, expanded: ch.id === chapter.id ? !ch.expanded : false }))
}

const openAddChapterDialog = () => {
  newChapter.value = { title: '', course_id: props.course.id, order: getDefaultOrder() }
  addChapterVisible.value = true
}

const openEditChapter = (chapter, index) => {
  editChapter.value = { id: chapter.id, title: chapter.title, course_id: props.course.id, order: chapter.order }
  editChapterVisible.value = true
}

const confirmAddChapter = async () => {
  if (!props.course.id || !newChapter.value.title.trim() || newChapter.value.order < 1) {
    ElMessage.error('请填写完整章节信息')
    return
  }
  try {
    const formData = new FormData()
    formData.append('title', newChapter.value.title)
    formData.append('course_id', props.course.id)
    formData.append('order', newChapter.value.order)
    const res = await axiosInstance.post('/api/course/create-chapter', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (res.data.success) {
      ElMessage.success('章节添加成功')
      addChapterVisible.value = false
      await loadChapters()
    } else {
      ElMessage.error(res.data.message || '添加章节失败')
    }
  } catch (error) {
    ElMessage.error('添加章节失败，请重试')
  }
}

const confirmEditChapter = async () => {
  if (!editChapter.value.id || !editChapter.value.title.trim() || editChapter.value.order < 1) {
    ElMessage.error('请填写完整章节信息')
    return
  }
  try {
    await ElMessageBox.confirm('确定修改该章节？修改后不可恢复', '提示', { 
      type: 'warning',
      confirmButtonText: '确认', // 新增：确认按钮文字
      cancelButtonText: '取消'   // 新增：取消按钮文字
    })
      .then(async () => {
        const formData = new FormData()
        formData.append('chapter_id', editChapter.value.id)
        formData.append('title', editChapter.value.title)
        formData.append('order', editChapter.value.order)
        const res = await axiosInstance.patch('/api/course/update-chapter', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
        if (res.data.success) {
          ElMessage.success('章节修改成功')
          editChapterVisible.value = false
          await loadChapters()
        } else {
          ElMessage.error(res.data.message || '修改章节失败')
        }
      })
      .catch(() => ElMessage.info('已取消修改操作'))
  } catch (error) {
    ElMessage.error('修改章节失败，请重试')
  }
}

const openAddResourceDialog = (chapterId) => {
  addResourceChapterId.value = chapterId
  addResourceVisible.value = true
}

const handleChapterDragStart = (e, chapter, index) => {
  e.dataTransfer.setData('text/plain', chapter.id);
  isDragging.value = true
  draggedItemType.value = 'chapter'
  draggedChapterIndex.value = index
  draggedChapterId.value = chapter.id
}

const handleResourceDragStart = (e, chapterId, resource, resIndex) => {
  e.dataTransfer.setData('text/plain', `${chapterId},${resource.id}`);
  isDragging.value = true
  draggedItemType.value = 'resource'
  draggedResourceIndex.value = resIndex
  draggedResourceId.value = resource.id
  draggedResourceChapterId.value = chapterId
}

const handleDragOver = (e) => {
  e.preventDefault()
  isDragOver.value = true
  e.dataTransfer.dropEffect = 'move'
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragOver.value = false
  if (isDragging.value) {
    if (draggedItemType.value === 'chapter' && draggedChapterId.value) {
      deleteChapter(draggedChapterId.value)
    } else if (draggedItemType.value === 'resource' && draggedResourceId.value) {
      deleteDroppedResource()
    } else {
      ElMessage.warning('不支持将此类型拖到删除区域')
    }
  }
  resetDragState()
}

const deleteDroppedResource = async () => {
  if (!draggedResourceChapterId.value || !draggedResourceId.value) return
  try {
    const chapter = courseChapters.value.find(ch => ch.id === draggedResourceChapterId.value)
    const resource = chapter?.resources.find(r => r.id === draggedResourceId.value)
    if (!resource) return
    const ext = getFileExtension(resource.type)
    await ElMessageBox.confirm(`确定删除该${ext}？删除后不可恢复`, '提示', { 
      type: 'warning',
      confirmButtonText: '确认', // 新增：确认按钮文字
      cancelButtonText: '取消'   // 新增：取消按钮文字
    })
      .then(async () => {
        const formData = new FormData()
        let url = ''
        if (resource.type === 'video') {
          formData.append('video_id', resource.id)
          url = '/api/course/delete-video'
        } else {
          formData.append('document_id', resource.id)
          url = '/api/course/delete-document'
        }
        const response = await axiosInstance.delete(url, { data: formData, headers: { 'Content-Type': 'multipart/form-data' } })
        if (response.data.success) {
          ElMessage.success('资源删除成功')
          await loadChapters()
        } else {
          ElMessage.error(response.data.message || '删除资源失败')
        }
      })
      .catch(() => ElMessage.info('已取消删除操作'))
  } catch (error) {
    ElMessage.error('删除资源失败，请重试')
  }
}

const resetDragState = () => {
  isDragging.value = false
  isDragOver.value = false
  draggedItemType.value = ''
  draggedChapterIndex.value = -1
  draggedChapterId.value = null
  draggedResourceIndex.value = -1
  draggedResourceId.value = null
  draggedResourceChapterId.value = null
}

const deleteChapter = async (chapterId) => {
  try {
    await ElMessageBox.confirm('确定删除该章节？删除后不可恢复', '提示', { 
      type: 'warning',
      confirmButtonText: '确认', // 新增：确认按钮文字
      cancelButtonText: '取消'   // 新增：取消按钮文字
    })
      .then(async () => {
        const formData = new FormData()
        formData.append('chapter_id', chapterId)
        const res = await axiosInstance.delete('/api/course/delete-chapter', { data: formData, headers: { 'Content-Type': 'multipart/form-data' } })
        if (res.data.success) {
          ElMessage.success('章节删除成功')
          await loadChapters()
        } else {
          ElMessage.error(res.data.message || '删除章节失败')
        }
      })
      .catch(() => ElMessage.info('已取消删除操作'))
  } catch (error) {
    ElMessage.error('删除章节失败，请重试')
  }
}

const getDefaultOrder = () => {
  const chapters = courseChapters.value || []
  return chapters.length ? Math.max(...chapters.map(ch => ch.order || 0)) + 1 : 1
}

const getResourceCount = (resources) => (resources || []).length

const openInNewTab = (url) => {
  if (url) window.open(url, '_blank')
  else ElMessage.warning('暂无预览链接')
}

const downloadResource = (resource) => {
  if (previewResourceInfoUrl.value) saveAs(previewResourceInfoUrl.value, resource.title)
  else ElMessage({ type: 'info', message: `模拟下载: ${resource.title}` })
}

const handleVideoError = () => {
  videoError.value = true
  ElMessage.error('视频加载失败，请检查文件路径或尝试下载查看')
}

const handleVideoLoaded = () => {
  videoError.value = false
}

const handlePdfLoad = () => {
  isPdfLoading.value = false
  pdfError.value = false
}

const handlePdfError = () => {
  isPdfLoading.value = false
  pdfError.value = true
  ElMessage.error('文档加载失败')
}

const handleChapterMouseEnter = (chapterId) => {
  chapterHovered.value[chapterId] = true
}

const handleChapterMouseLeave = (chapterId) => {
  chapterHovered.value[chapterId] = false
}

const isChapterHovered = (chapterId) => chapterHovered.value[chapterId] || false

const handleResourceMouseEnter = (resourceId) => {
  resourceHovered.value[resourceId] = true
}

const handleResourceMouseLeave = (resourceId) => {
  resourceHovered.value[resourceId] = false
}

const isResourceHovered = (resourceId) => resourceHovered.value[resourceId] || false

const getFileExtension = (type) => {
  const extMap = {
    'doc': '文档', 'pdf': 'PDF文档', 'txt': '文本文档', 'video': '视频', 'ppt': '演示文档', 'pptx': '演示文档'
  }
  return extMap[type] || '其他文件'
}

const getFileIconClass = (type) => {
  if (isVideoFile(type)) return 'el-icon-video-camera text-2b6a3d'
  if (isDocFile(type)) return type === 'pdf' ? 'el-icon-document text-red-500' : 'el-icon-document text-2b6a3d'
  if (isPptFile(type)) return 'el-icon-picture text-orange-500'
  return 'el-icon-document text-gray-500'
}

const videoMimeMap = {
  'mp4': 'video/mp4', 'mov': 'video/quicktime', 'avi': 'video/x-msvideo', 'mkv': 'video/x-matroska', 'webm': 'video/webm'
}

const getVideoMimeType = (url) => {
  if (!url) return 'video/mp4'
  const ext = url.split('.').pop().toLowerCase()
  return videoMimeMap[ext] || 'video/mp4'
}

const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return bytes.toFixed(2) + ' ' + units[i]
}
    
onMounted(() => {
  if (props.course.id) loadChapters()
})

watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.course.id) loadChapters()
  else if (!newVal) resetData()
})

watch(() => props.course.id, (newId) => {
  if (newId) loadChapters()
})

const handleRefreshData = () => {
  loadChapters()
}

onUnmounted(() => {
  // 清理资源
})
</script>

<style scoped>
/* [FIX] 修正悬停样式的选择器，使其更精确 */
.chapter-item:hover:not(.dragging),
.chapter-item.chapter-hover {
  box-shadow: 0 4px 16px 0 rgba(43, 106, 61, 0.15);
  border-color: #2b6a3d;
}

.resource-item:hover:not(.dragging),
.resource-item.resource-hover {
  padding-left: 5px;
  border-color: #2b6a3d;
  background-color: #f0f7f2;
}

/* [FIX] 为拖拽中的元素添加样式，使其颜色加深 */
.chapter-item.dragging,
.resource-item.dragging {
  opacity: 0.7;
  background-color: #d6f0dd; /* 颜色加深效果 */
  border-color: #2b6a3d;
  box-shadow: 0 2px 8px rgba(43, 106, 61, 0.3);
}

/* ... 其他样式 ... */

/* PPT预览样式 */
.ppt-preview {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.loading-pptx {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 600px;
  color: #909399;
  font-size: 16px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
  width: 100%;
  max-width: 900px;
}

.error-pptx {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 600px;
  color: #f56c6c;
  font-size: 14px;
  background-color: #fff;
  border: 1px solid #ffe3e3;
  border-radius: 4px;
  width: 100%;
  max-width: 900px;
}

.chapter-resource-dialog .el-dialog {
  border-radius: 0;
}

.chapter-resource-dialog .el-dialog__body {
  padding: 0 !important;
  overflow: hidden !important;
}

.management-container {
  display: flex;
  height: 600px;
  overflow: hidden;
}

.sidebar {
  width: 400px;
  overflow-y: auto;
  padding: 15px;
  border-right: 1px solid #ebeef5;
  position: relative;
}

.preview-area {
  flex: 1;
  overflow: hidden;
  padding: 15px;
}

.chapter-item {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  margin-bottom: 8px;
  padding: 12px;
  transition: all 0.3s ease;
  position: relative;
  background-color: #fff;
  cursor: pointer;
}

.chapter-expanded {
  border-color: #c0c4cc;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  color: #333;
  line-height: 30px;
}

.chapter-content {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #dcdfe6;
}

.resource-item {
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #dcdfe6;
  transition: all 0.3s ease;
  cursor: pointer;
}


.resource-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.resource-title-container {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.resource-title {
  font-size: 16px;
  color: #000;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 30px;
}

.resource-type-tag {
  font-size: 15px;
  color: #2b6a3d;
  background-color: #e6f7ed;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  line-height: 30px;
  margin-left: 10px;
} 
.empty-resource {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
  color: #999;
  font-size: 12px;
}

.add-resource-dashed, .add-chapter-dashed {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border: 1px dashed #666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 8px;
  color: #666;
}

.add-resource-dashed:hover, .add-chapter-dashed:hover {
  border-color: #2b6a3d;
  color: #2b6a3d;
  background-color: #f0f7f2;
}

.add-chapter-dashed {
  margin: 15px 0;
}

.trash-container {
  position: absolute;
  bottom: 15px;
  left: 15px;
  right: 15px;
  padding: 12px;
  background: #f56c6c;
  color: #fff;
  text-align: center;
  border-radius: 4px;
  cursor: pointer;
  box-sizing: border-box;
  transition: all 0.2s;
  z-index: 10;
}

.trash-active {
  background: #e64c4c;
  transform: scale(1.02);
}

.preview-container {
  background: #fff;
  border-radius: 6px;
  padding: 15px;
  height: 100%;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.12), 0 1px 3px 0 rgba(0, 0, 0, 0.24);
  display: flex;
  flex-direction: column;
}

.nav-title {
  font-size: 25px;
  color: #2b6a3d;
  margin: 0 0 15px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e5e5;
  font-weight: 600;
}

.preview-body {
  flex-grow: 1;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  overflow-y: auto;
}

.loading-preview {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-preview, .pdf-preview, .doc-preview, .txt-preview, .other-document-preview {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.video-wrapper {
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 80%;
}

.video-wrapper video {
  width: 100%;
  height: auto;
  display: block;
}

.video-error {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f56c6c;
  font-size: 14px;
}

.pdf-container {
  border: 1px solid #e9ecef;
  border-radius: 4px;
  background-color: #f9f9f9;
  overflow: hidden;
  position: relative;
  width: 750px;
  height: 500px;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.loading-pdf, .pdf-error, .no-pdf-url {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 14px;
  background-color: #fff;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1;
}

.pdf-error {
  color: #f56c6c;
}

.txt-preview .txt-content {
  width: 100%;
  max-width: 800px;
  background: #f7f8fa;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  padding: 1em;
  overflow-x: auto;
  line-height: 1.6;
  font-family: monospace;
}

.empty-preview {
  font-size: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: #999;
}

.chapter-index {
  color: #2b6a3d;
  font-size: 18px;
  line-height: 30px;
}

.dashed-text {
  width:100%;
  font-size: 16px;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  text-align: center;
}

.dashed-text:hover {
  color: #333;
}

.file-info h4 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #2b6a3d;
}

.file-info p {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.preview-actions {
  display: flex;
  gap: 8px;
  margin-top: 15px;
}

.text-2b6a3d { color: #2b6a3d !important; }
.text-red-500 { color: #f56c6c !important; }
.text-orange-500 { color: #ff7d00 !important; }
.text-gray-500 { color: #909399 !important; }

.el-button--primary {
  background-color: #2b6a3d !important;
  border-color: #2b6a3d !important;
}
.el-button--primary:hover {
  background-color: #235631 !important;
  border-color: #235631 !important;
}

.el-radio__inner:hover, .el-radio__inner:hover + .el-radio__label {
  color: #2b6a3d !important;
}

.el-radio__inner:hover {
  border-color: #2b6a3d !important;
}

.el-radio.is-checked .el-radio__inner {
  background-color: #2b6a3d !important;
  border-color: #2b6a3d !important;
}

.el-input__inner:focus {
  border-color: #2b6a3d !important;
  outline: none !important;
  box-shadow: 0 0 0 2px rgba(43, 106, 61, 0.2) !important;
}

.el-input__inner {
  border-color: #dcdfe6 !important;
}

.el-input__inner:focus + .el-input__icon {
  color: #2b6a3d !important;
}

.el-input-number__decrease, .el-input-number__increase {
  color: #dcdfe6 !important;
}

.el-input-number__decrease:hover, .el-input-number__increase:hover {
  color: #2b6a3d !important;
  background-color: #e6f7ed !important;
}

.el-input-number__decrease:active, .el-input-number__increase:active {
  color: #2b6a3d !important;
  background-color: #d6f0dd !important;
}

.el-input-number__input {
  border-color: #dcdfe6 !important;
}

.el-input-number__input:focus {
  border-color: #2b6a3d !important;
}

.el-skeleton__line {
  background-color: #e6f7ed !important;
}

.el-icon {
  color: #2b6a3d !important;
}

.el-icon:hover {
  color: #235631 !important;
}

/* 调整章节编辑按钮样式 */
.chapter-header .el-button {
  color: #2b6a3d;
  border: 1px solid #2b6a3d;
  padding: 0 18px 0 0;
  border-radius: 4px;
  transition: all 0.2s;
}

.chapter-header .el-button:hover {
  background-color: #2b6a3d;
  color: white !important;
}

.trash-icon{
  font-size: 16px;
}

.no-material-info{
  font-size: 16px;
  justify-content: left;
}

/* 文档预览核心样式 */
.doc-preview {
  flex: 1;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
  width: 95%;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  scrollbar-width: thin;
}

.doc-preview::-webkit-scrollbar { width: 6px; }
.doc-preview::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.doc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f2f2f2;
}
.doc-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.doc-actions {
  display: flex;
  gap: 10px;
}

.doc-content {
  line-height: 1.8;
  color: #444;
  font-size: 14px;
}
.doc-text {
  text-align: left;
  h1, h2, h3, h4, h5, h6 {
    margin: 1.5em 0 0.8em;
    font-weight: 600;
    color: #2b6a3d;
    border-left: 4px solid #2b6a3d;
    padding-left: 10px;
  }
  h1 { font-size: 24px; }
  h2 { font-size: 20px; }
  h3 { font-size: 18px; }
  h4 { font-size: 16px; }

  p {
    margin: 0.8em 0;
    text-indent: 2em;
  }

  ul, ol {
    margin: 0.8em 0 0.8em 2em;
    padding-left: 1em;
    list-style: inside;
  }
  ul { list-style-type: disc; }
  ol { list-style-type: decimal; }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
  }
  th, td {
    border: 1px solid #e5e7eb;
    padding: 8px 12px;
    text-align: left;
  }
  th {
    background: #f9fafb;
    font-weight: 600;
  }

  pre, code {
    background: #f7f8fa;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    padding: 0.2em 0.4em;
    font-family: "Fira Code", monospace;
    font-size: 13px;
    color: #e64c4c;
  }
  pre {
    padding: 1em;
    margin: 1em 0;
    overflow-x: auto;
    line-height: 1.6;
  }

  img {
    max-width: 100%;
    height: auto;
    margin: 1em 0;
    border-radius: 4px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  }
}

.loading-doc {
  display: flex;
  justify-content: center;
  padding: 50px 0;
}
.loading-doc .el-skeleton {
  width: 80%;
}

.error-doc {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
  color: #f56c6c;
  text-align: center;
}
.error-doc .el-icon {
  font-size: 24px;
  margin-bottom: 10px;
}
</style>