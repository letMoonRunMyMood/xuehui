<template>
  <div class="pc-container">
    <!-- 导航栏组件：固定到顶部 -->
    <NavigationBar :currentNav="currentNav" />

    <!-- 内容包裹层：适配固定导航栏，实现滚动 -->
    <div class="content-wrapper">
      <div class="pc-main">
        <!-- 面包屑导航和讨论区按钮容器 -->
        <div class="breadcrumb-container">
          <div class="breadcrumb">
            <span @click="navigateTo('/home')" class="breadcrumb-link">首页</span>
            <span class="breadcrumb-separator">></span>
            <span @click="navigateTo('/course')" class="breadcrumb-link">课程中心</span>
            <span class="breadcrumb-separator">></span>
            <span @click="navigateTo(`/course/${courseId}`)" class="breadcrumb-link">课程详情</span>
            <span class="breadcrumb-separator">></span>
            <span class="breadcrumb-current">课程内容</span>
          </div>

          <!-- 课程讨论区按钮 - 面包屑右侧 -->
          <div
              class="course-discussion-toggle"
              @click="isDiscussionOpen = true"
          >
            <div class="discussion-header">
              <el-icon :size="18" class="discussion-icon">
                <ChatLineRound />
              </el-icon>
              <span class="discussion-title">课程讨论区</span>
              <span class="discussion-count" v-if="discussionCount > 0">{{ discussionCount }}</span>
              <el-icon class="discussion-arrow" :size="16">
                <ArrowRight />
              </el-icon>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-state">
          <el-skeleton :rows="12" active></el-skeleton>
        </div>

        <!-- 错误状态 -->
        <div v-if="errorMessage" class="error-state">
          <el-alert type="error" :message="errorMessage" show-icon></el-alert>
        </div>
      </div>

      <!-- 章节和资料内容区域 -->
      <div class="pc-main course-bottom-container">
        <div class="content-section">
          <h2 class="section-title">课程章节</h2>
          <div v-if="courseChapters && courseChapters.length > 0" class="content-list">
            <div
                v-for="(chapter, chapterIndex) in courseChapters"
                :key="chapter.id"
                class="chapter-item"
                @click="toggleChapter(chapter)"
                :class="{ 'chapter-expanded': chapter.expanded }"
            >
              <div class="chapter-header">
                <div class="chapter-info">
                  <span class="chapter-index">第{{ chapterIndex + 1 }}章</span>
                  <span class="chapter-title">{{ chapter.title || '未命名章节' }}</span>
                </div>
              </div>
              <div class="chapter-content" v-if="chapter.expanded">
                <div v-if="chapter.resources.length > 0" class="resource-list">
                  <div
                      v-for="(resource, resIndex) in chapter.resources"
                      :key="resource.id"
                      class="resource-item"
                      @click.stop="loadResourceDetails(resource)"
                      :class="{ 
                        'resource-hover': isResourceHovered(resource.id),
                        'resource-active': selectedResourceId === resource.id 
                      }"
                      @mouseenter="handleResourceMouseEnter(resource.id)"
                      @mouseleave="handleResourceMouseLeave(resource.id)"
                  >
                    <div class="resource-header">
                      <div class="resource-title-container">
                        <span class="resource-type-tag">{{ getFileExtension(resource.type) }}</span>
                        <span class="resource-title">{{ resource.title || '未命名资源' }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="empty-resource">
                  <el-icon size="16"><Document /></el-icon>
                  <span>该章节暂无资料</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-tip">
            <el-icon size="24"><Document /></el-icon>
            <p>该课程暂无章节</p>
          </div>
        </div>

        <!-- 右侧资料详情区域 -->
        <div class="material-section">
          <h2 class="section-title">资料详情</h2>
          <div v-if="previewResourceInfo" class="material-detail">
            <!-- 预览容器 - 用于居中所有内容 -->
            <div class="preview-container">
              <div v-if="isLoadingResource" class="loading-preview">
                <el-skeleton animated />
              </div>
              <div v-else class="file-preview-wrapper">
                <!-- 视频预览 -->
                <div v-if="previewResourceInfo.type === 'video'" class="preview-content">
                  <div class="video-wrapper">
                    <video
                        ref="videoRef"
                        controls
                        style="max-width: 100%; max-height: 500px;"
                        @error="handleVideoError"
                        @loadeddata="handleVideoLoaded"
                        @timeupdate="handleTimeUpdate"
                        @play="handleVideoPlay"
                        @pause="handleVideoPause"
                        @ended="handleVideoEnded"
                    >
                      <source :src="previewResourceInfoUrl" :type="getVideoMimeType(previewResourceInfoUrl)">
                      您的浏览器不支持视频播放
                    </video>
                    <div v-if="videoError" class="video-error">
                      <el-icon size="16"><InfoFilled /></el-icon>
                      <span>视频加载失败，请尝试下载查看</span>
                    </div>
                  </div>

                  <!-- 操作按钮 -->
                  <div class="preview-actions">
                    <el-button type="text" size="default" v-if="previewResourceInfoUrl" @click="openInNewTab(previewResourceInfoUrl)">
                      新窗口打开
                    </el-button>
                    <el-button type="primary" size="default" @click="downloadResource(previewResourceInfo)">
                      下载文件
                    </el-button>
                  </div>
                </div>

                <!-- Word文档预览 -->
                <div v-else-if="['doc', 'docx'].includes(previewResourceInfo.type)" class="preview-content doc-preview">
                  <div v-if="isLoadingDoc" class="loading-docx">加载中...</div>
                  <div v-if="docError" class="docx-error">
                    <el-icon size="16"><InfoFilled /></el-icon>
                    <span>{{ docError || '文档加载失败，请尝试下载查看' }}</span>
                  </div>
                  <div v-else-if="docContent" class="doc-content">
                    <div class="doc-header">
                      <h3>{{ previewResourceInfo.title || '文档内容' }}</h3>
                    </div>
                    <div class="doc-text" v-html="docContent"></div>
                  </div>

                  <!-- 操作按钮 -->
                  <div class="preview-actions">
                    <el-button type="text" size="default" v-if="previewResourceInfoUrl" @click="openInNewTab(previewResourceInfoUrl)">
                      新窗口打开
                    </el-button>
                    <el-button type="primary" size="default" @click="downloadResource(previewResourceInfo)">
                      下载文件
                    </el-button>
                  </div>
                </div>

                <!-- PDF预览 -->
                <div v-else-if="previewResourceInfo.type === 'pdf'" class="preview-content pdf-preview">
                  <div class="pdf-container">
                    <!-- 无PDF链接时的提示 -->
                    <div v-if="!previewResourceInfoUrl" class="no-pdf-url">
                      <p>暂无文档链接可预览</p>
                    </div>
                    <!-- PDF iframe预览 -->
                    <iframe
                        v-else
                        :src="previewResourceInfoUrl + '?t=' + pdfTimestamp"
                        class="pdf-iframe"
                        @load="handlePdfLoad"
                        @error="handlePdfError"
                    ></iframe>
                    <!-- 加载中状态 -->
                    <div v-if="isPdfLoading" class="loading-pdf">加载中...</div>
                    <!-- 加载失败状态 -->
                    <div v-else-if="pdfError" class="pdf-error">文档加载失败，请检查文件路径或尝试下载</div>
                  </div>

                  <!-- 操作按钮 -->
                  <div class="preview-actions">
                    <el-button type="text" size="default" v-if="previewResourceInfoUrl" @click="openInNewTab(previewResourceInfoUrl)">
                      新窗口打开
                    </el-button>
                    <el-button type="primary" size="default" @click="downloadResource(previewResourceInfo)">
                      下载文件
                    </el-button>
                  </div>
                </div>

                <!-- PPT预览 -->
                <div v-else-if="['ppt', 'pptx'].includes(previewResourceInfo.type)" class="preview-content">
                  <div class="ppt-container">
                    <!-- 加载状态 -->
                    <div v-if="pptxLoading" class="loading-pptx">
                      <el-skeleton width="80%" height="500px" animated />
                    </div>
                    <div v-if="pptxError" class="pptx-error">
                      <el-icon size="16"><InfoFilled /></el-icon>
                      <span>演示文稿加载失败，请尝试下载查看</span>
                    </div>
                    <VueOfficePptx
                        v-else
                        :src="previewResourceInfoUrl"
                        style="width: 800px; height: auto; margin: 0 auto;"
                        @rendered="pptxLoading = false"
                        @error="handlePptxError"
                    />
                  </div>

                  <!-- 操作按钮 -->
                  <div class="preview-actions">
                    <el-button type="text" size="default" v-if="previewResourceInfoUrl" @click="openInNewTab(previewResourceInfoUrl)">
                      新窗口打开
                    </el-button>
                    <el-button type="primary" size="default" @click="downloadResource(previewResourceInfo)">
                      下载文件
                    </el-button>
                  </div>
                </div>

                <!-- 文本预览 -->
                <div v-else-if="['txt', 'md'].includes(previewResourceInfo.type)" class="preview-content">
                  <div v-if="isLoadingTxt" class="loading-txt">加载中...</div>
                  <div v-else class="txt-content" v-html="txtContent || '暂无内容'"></div>

                  <!-- 操作按钮 -->
                  <div class="preview-actions">
                    <el-button type="text" size="default" v-if="previewResourceInfoUrl" @click="openInNewTab(previewResourceInfoUrl)">
                      新窗口打开
                    </el-button>
                    <el-button type="primary" size="default" @click="downloadResource(previewResourceInfo)">
                      下载文件
                    </el-button>
                  </div>
                </div>

                <!-- 图片预览 -->
                <div v-else-if="isImageFile(previewResourceInfo.type)" class="preview-content">
                  <img :src="previewResourceInfoUrl" alt="预览图" class="preview-image" />

                  <!-- 操作按钮 -->
                  <div class="preview-actions">
                    <el-button type="text" size="default" v-if="previewResourceInfoUrl" @click="openInNewTab(previewResourceInfoUrl)">
                      新窗口打开
                    </el-button>
                    <el-button type="primary" size="default" @click="downloadResource(previewResourceInfo)">
                      下载文件
                    </el-button>
                  </div>
                </div>

                <!-- 其他文件类型 -->
                <div v-else class="preview-content other-document-preview">
                  <el-icon :size="40" class="file-icon"><Document /></el-icon>
                  <div class="file-info">
                    <h4>{{ previewResourceInfo.title || '未知文件' }}</h4>
                    <p>类型: {{ getFileExtension(previewResourceInfo.type) }}</p>
                    <p>大小: {{ formatFileSize(previewResourceInfo.size) || '-' }}</p>
                  </div>
                  <div class="preview-actions">
                    <el-button type="primary" size="default" @click="downloadResource(previewResourceInfo)">下载文件</el-button>
                    <el-button type="text" size="default" v-if="previewResourceInfoUrl" @click="openInNewTab(previewResourceInfoUrl)">新窗口打开</el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-preview">
            <el-icon :size="40" class="empty-icon"><Document /></el-icon>
            <p>请选择左侧资料进行预览</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 讨论区子组件 -->
    <DiscussionSection
        :course-id="courseId"
        :course-name="courseName"
        :is-open="isDiscussionOpen"
        :user-avatar="userAvatar"
        @close="isDiscussionOpen = false"
        @update-count="discussionCount = $event"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, nextTick, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElSkeleton, ElAlert, ElMessage, ElNotification, ElButton } from 'element-plus';
// 导入@vue-office相关组件
import VueOfficeDocx from '@vue-office/docx'
import VueOfficePptx from '@vue-office/pptx'
// 仅保留docx的样式
import '@vue-office/docx/lib/index.css'
import NavigationBar from '../components/NavigationBar.vue';
import Footer from '../components/Footer.vue';
import axiosInstance from '@/service/api.js';
import { saveAs } from 'file-saver';
import { ArrowRight, Document, InfoFilled, ChatLineRound, Loading, CircleCloseFilled } from '@element-plus/icons-vue';
import DiscussionSection from '../components/DiscussionSection.vue';
// 关键导入：路径修正函数和文档解析依赖
import { fixCoverPath } from '@/utils/format.js'
import * as mammoth from 'mammoth';

const route = useRoute();
const router = useRouter();

// 导航栏标识
const currentNav = ref('courseContent');
const courseId = ref(route.params.id);
const courseChapters = ref([]);
const previewResourceInfo = ref(null);
const previewResourceInfoUrl = ref('');
const isLoading = ref(true);
const errorMessage = ref('');
const isLoadingResource = ref(false);
// 文档预览相关状态
const isPdfLoading = ref(false);
const pdfError = ref(false);
const pdfTimestamp = ref(0);
const docxLoading = ref(false);
const docError = ref('');
const isLoadingDoc = ref(false);
const docContent = ref('');
const txtContent = ref('');
const isLoadingTxt = ref(false);
const pptxLoading = ref(false);
const pptxError = ref(false);
// 视频相关状态
const videoError = ref(false);
const courseRequestController = ref(null);
const resourceHovered = ref({});

// 核心交互：记录选中资源
const selectedResourceId = ref(null);

// 视频进度相关状态
const currentProgress = ref(0.0);
const isSavingProgress = ref(false);
const progressSaveInterval = ref(null);
const videoRef = ref(null);
const userId = ref(sessionStorage.getItem('id'));
const currentVideoId = ref(null);
const pendingProgress = ref(0.0);

// 讨论区相关状态
const isDiscussionOpen = ref(false);
const discussionCount = ref(0);
const courseName = ref('');
const userAvatar = ref(sessionStorage.getItem('avatar'));

// 导航方法
const navigateTo = (path) => {
  router.push(path);
};

// 加载章节数据
const loadChapters = async () => {
  isLoading.value = true;
  errorMessage.value = '';

  if (courseRequestController.value) {
    courseRequestController.value.abort();
  }

  courseRequestController.value = new AbortController();

  try {
    const response = await axiosInstance.get('/api/course/get-course-detail', {
      params: { course_id: courseId.value },
      signal: courseRequestController.value.signal
    });

    if (response.data.success) {
      const courseData = response.data.data;
      courseName.value = courseData.name || '';
      courseChapters.value = (courseData.chapters || []).map(chapter => {
        const resources = [
          ...(chapter.videos || []).map(video => ({
            ...video,
            type: 'video',
            file: fixCoverPath(video.file_url),
            size: video.size || 0
          })),
          ...(chapter.documents || []).map(doc => ({
            ...doc,
            type: getFileTypeFromExt(doc.file_url),
            file: fixCoverPath(doc.file_url),
            size: doc.size || 0
          }))
        ];
        return {
          ...chapter,
          expanded: false,
          resources: normalizeResources(resources)
        };
      });
    } else {
      errorMessage.value = response.data.message || '获取课程章节失败';
    }
  } catch (error) {
    if (error.name !== 'AbortError') {
      errorMessage.value = '网络错误，请重试';
      console.error('获取课程章节失败:', error);
    }
  } finally {
    isLoading.value = false;
  }
};

const getVideoProgress = async (videoId) => {
  if (!userId.value || !videoId) return 0;

  try {
    const response = await axiosInstance.get('/api/course/get-progress', {
      params: {
        user_id: userId.value,
        video_id: videoId
      }
    });

    if (response.data.success && response.data.data.have_progress) {
      return response.data.data.progress;
    }
  } catch (error) {
    console.error('获取播放进度失败:', error);
    ElMessage.error('获取播放进度失败，将从开头播放');
  }

  return 0;
};

// 保存视频进度
const saveVideoProgress = async (videoId, progress) => {
  if (!userId.value || !videoId) return;

  if (isSavingProgress.value) {
    return;
  }

  isSavingProgress.value = true;

  try {
    const formData = new FormData();
    formData.append('user_id', userId.value);
    formData.append('video_id', videoId);
    formData.append('progress', progress);

    const response = await axiosInstance.post('/api/course/save-progress', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    if (!response.data.success) {
      ElMessage.error(response.data.message || '保存播放进度失败');
    }
  } catch (error) {
    console.error('保存播放进度失败:', error);
    ElMessage.error('保存播放进度失败，请稍后再试');
  } finally {
    isSavingProgress.value = false;
  }
};

// 视频时间更新事件处理
const handleTimeUpdate = () => {
  if (!videoRef.value || !videoRef.value.duration || !userId.value || !currentVideoId.value) {
    return;
  }

  const progress = videoRef.value.currentTime / videoRef.value.duration;
  currentProgress.value = progress;

  if (!progressSaveInterval.value) {
    progressSaveInterval.value = setInterval(() => {
      saveVideoProgress(currentVideoId.value, currentProgress.value);
    }, 1000);
  }
};

// 视频播放/暂停/结束事件处理
const handleVideoPlay = () => {};
const handleVideoPause = () => {
  if (userId.value && currentVideoId.value && previewResourceInfo.value && previewResourceInfo.value.type === 'video') {
    saveVideoProgress(currentVideoId.value, currentProgress.value);
  }
  // 清除定时器
  if (progressSaveInterval.value) {
    clearInterval(progressSaveInterval.value);
    progressSaveInterval.value = null;
  }
};
const handleVideoEnded = () => {
  if (userId.value && currentVideoId.value && previewResourceInfo.value && previewResourceInfo.value.type === 'video') {
    saveVideoProgress(currentVideoId.value, 1.0);
    ElNotification({
      title: '视频播放完成',
      message: '该视频已全部播放完毕',
      type: 'success'
    });
  }
  // 清除定时器
  if (progressSaveInterval.value) {
    clearInterval(progressSaveInterval.value);
    progressSaveInterval.value = null;
  }
};

// 文件类型处理
const getFileTypeFromExt = (url) => {
  if (!url) return 'doc';
  const ext = url.split('.').pop().toLowerCase();
  const fileTypeMap = {
    'pdf': 'pdf',
    'doc': 'doc',
    'docx': 'docx',
    'ppt': 'ppt',
    'pptx': 'pptx',
    'mp4': 'video',
    'mov': 'video',
    'avi': 'video',
    'mkv': 'video',
    'webm': 'video',
    'txt': 'txt',
    'md': 'md',
    'jpg': 'image',
    'jpeg': 'image',
    'png': 'image',
    'gif': 'image',
    'bmp': 'image'
  };
  return fileTypeMap[ext] || 'doc';
};

const normalizeResources = (resources) => {
  if (!resources || !Array.isArray(resources)) return [];
  return resources.map(resource => ({
    ...resource,
    type: mapResourceType(resource.type)
  }));
};

const mapResourceType = (type) => {
  const typeMap = {
    'video': 'video',
    'doc': 'doc',
    'docx': 'docx',
    'pdf': 'pdf',
    'ppt': 'ppt',
    'pptx': 'pptx',
    'image': 'image',
    'audio': 'audio',
    'txt': 'txt',
    'md': 'md'
  };
  return typeMap[type] || 'doc';
};

// 文件类型判断
const isTextFile = (type) => ['txt', 'md'].includes(type);
const isVideoFile = (type) => type === 'video';
const isPdfFile = (type) => type === 'pdf';
const isDocxFile = (type) => ['doc', 'docx'].includes(type);
const isPptxFile = (type) => ['ppt', 'pptx'].includes(type);
const isImageFile = (type) => ['image', 'jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(type);

// 文档预览错误处理
const handleDocxError = (error) => {
  docError.value = '文档加载失败，请尝试下载查看';
  isLoadingDoc.value = false;
  console.error('Word文档加载错误:', error);
};

const handlePptxError = (error) => {
  pptxError.value = true;
  pptxLoading.value = false;
  ElMessage.error(`PPT加载失败: ${error.message || '文件格式错误或链接无效'}`);
  console.error('PPT文档加载错误:', error);
};

// PDF相关处理函数
const handlePdfLoad = () => {
  isPdfLoading.value = false;
  pdfError.value = false;
};

const handlePdfError = () => {
  isPdfLoading.value = false;
  pdfError.value = true;
  ElMessage.error('文档加载失败');
};

// 视频错误处理
const handleVideoError = () => {
  videoError.value = true;
  ElMessage.error('视频加载失败，请检查文件路径或尝试下载查看');
};

// 加载文档内容
const loadDocContent = async (url, type) => {
  isLoadingDoc.value = true;
  docContent.value = '';
  docError.value = '';
  try {
    const response = await axiosInstance.get(url, { responseType: 'arraybuffer' });
    const arrayBuffer = response.data;
    
    if (type === 'docx' || url.toLowerCase().endsWith('.docx')) {
      const result = await mammoth.convertToHtml({ arrayBuffer });
      if (result.messages.some(msg => msg.type === 'error')) {
        throw new Error('文档内容解析错误');
      }
      docContent.value = result.value;
    } else if (type === 'doc' || url.toLowerCase().endsWith('.doc')) {
      const decoder = new TextDecoder('utf-8', { fatal: false });
      const textContent = decoder.decode(arrayBuffer);
      docContent.value = textContent.trim() ? textContent.replace(/\n/g, '<br>') : '';
      if (!docContent.value) {
        throw new Error('无法解析DOC文件内容');
      }
    }
  } catch (error) {
    console.error('文档解析失败:', error);
    docError.value = '文档加载失败，请尝试下载查看';
  } finally {
    isLoadingDoc.value = false;
  }
};

// 加载文本内容
const loadTxtContent = async () => {
  isLoadingTxt.value = true;
  try {
    const response = await axiosInstance.get(previewResourceInfoUrl.value, { responseType: 'text' });
    txtContent.value = response.data;
  } catch (error) {
    console.error('加载文本内容失败:', error);
    txtContent.value = '';
  } finally {
    isLoadingTxt.value = false;
  }
};

// 加载资源详情
const loadResourceDetails = async (resource) => {
  selectedResourceId.value = resource.id;
  isLoadingResource.value = true;
  resetPreviewState();
  
  try {
    let response;

    if (isVideoFile(resource.type)) {
      response = await axiosInstance.get('/api/course/get-video', {
        params: { video_id: resource.id }
      });
      currentVideoId.value = resource.id;
    } else {
      response = await axiosInstance.get('/api/course/get-document', {
        params: { document_id: resource.id }
      });
    }

    if (response.data.success) {
      const resourceData = response.data.data;
      const originalUrl = resourceData.url;
      const fixedUrl = fixCoverPath(originalUrl);
      const finalType = getFileTypeFromExt(originalUrl) || resource.type;

      previewResourceInfo.value = {
        ...resource,
        ...resourceData,
        type: finalType,
        size: resource.size || resourceData.size || 0
      };
      previewResourceInfoUrl.value = fixedUrl;

      if (['doc', 'docx'].includes(finalType)) {
        await loadDocContent(fixedUrl, finalType);
      } else if (finalType === 'txt' || finalType === 'md') {
        await loadTxtContent();
      } else if (isPptxFile(finalType)) {
        pptxLoading.value = true;
      } else if (finalType === 'pdf') {
        isPdfLoading.value = true;
        pdfTimestamp.value = new Date().getTime();
      }

      if (isVideoFile(finalType) && userId.value) {
        pendingProgress.value = await getVideoProgress(currentVideoId.value);
      }
    } else {
      previewResourceInfo.value = {
        ...resource,
        title: '加载失败',
        url: '',
        type: resource.type
      };
      previewResourceInfoUrl.value = '';
      ElMessage.error(response.data.message || '获取资源详情失败');
    }
  } catch (error) {
    previewResourceInfo.value = {
      ...resource,
      title: '加载失败',
      url: '',
      type: resource.type
    };
    previewResourceInfoUrl.value = '';
    ElMessage.error('获取资源详情失败，请重试');
    console.error('加载资源失败:', error);
  } finally {
    isLoadingResource.value = false;
    if (!isPdfFile(previewResourceInfo.value?.type)) {
      isPdfLoading.value = false;
    }
  }
};

// 重置预览状态
const resetPreviewState = () => {
  txtContent.value = '';
  isLoadingTxt.value = false;
  pptxLoading.value = false;
  pptxError.value = false;
  videoError.value = false;
  isPdfLoading.value = false;
  pdfError.value = false;
  docContent.value = '';
  isLoadingDoc.value = false;
  docError.value = '';
  // 清除视频进度定时器
  if (progressSaveInterval.value) {
    clearInterval(progressSaveInterval.value);
    progressSaveInterval.value = null;
  }
};

// 视频加载完成后设置进度
const handleVideoLoaded = () => {
  videoError.value = false;

  if (userId.value && currentVideoId.value && pendingProgress.value > 0 && videoRef.value) {
    nextTick(() => {
      videoRef.value.currentTime = pendingProgress.value * videoRef.value.duration;
      ElMessage({
        type: 'info',
        message: `视频进度加载成功`
      });
      currentProgress.value = pendingProgress.value;
      pendingProgress.value = 0;
    });
  }
};

// 切换章节展开/收起
const toggleChapter = (chapter) => {
  courseChapters.value = courseChapters.value.map(ch => ({
    ...ch,
    expanded: ch.id === chapter.id ? !ch.expanded : false
  }));
};

// 辅助函数
const openInNewTab = (url) => {
  if (url) {
    window.open(url, '_blank');
  } else {
    ElMessage.warning('暂无预览链接');
  }
};

const downloadResource = (resource) => {
  if (previewResourceInfoUrl.value) {
    saveAs(previewResourceInfoUrl.value, resource.title);
  } else {
    ElMessage({ type: 'info', message: `模拟下载: ${resource.title}` });
  }
};

// 修正文件类型标签映射
const getFileExtension = (type) => {
  const extMap = {
    'doc': '文档', 'docx': '文档',
    'pdf': 'PDF文档',
    'ppt': '演示文稿', 'pptx': '演示文稿',
    'video': '视频', 'mp4': '视频', 'mov': '视频', 'avi': '视频', 'mkv': '视频', 'webm': '视频',
    'image': '图片', 'jpg': '图片', 'jpeg': '图片', 'png': '图片', 'gif': '图片', 'bmp': '图片',
    'txt': '文本文档', 'md': '文本文档'
  };
  return extMap[type] || type;
};

// 文件大小格式化
const formatFileSize = (bytes) => {
  if (!bytes) return '-';
  const units = ['B', 'KB', 'MB', 'GB'];
  let i = 0;
  let size = bytes;
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024;
    i++;
  }
  return size.toFixed(2) + ' ' + units[i];
};

const videoMimeMap = {
  'mp4': 'video/mp4',
  'mov': 'video/quicktime',
  'avi': 'video/x-msvideo',
  'mkv': 'video/x-matroska',
  'webm': 'video/webm'
};

const getVideoMimeType = (url) => {
  if (!url) {
    return 'video/mp4';
  }
  const ext = url.split('.').pop().toLowerCase();
  return videoMimeMap[ext] || 'video/mp4';
};

// 悬停处理
const handleResourceMouseEnter = (resourceId) => {
  resourceHovered.value[resourceId] = true;
};

const handleResourceMouseLeave = (resourceId) => {
  resourceHovered.value[resourceId] = false;
};

const isResourceHovered = (resourceId) => resourceHovered.value[resourceId] || false;

// 组件挂载时初始化
onMounted(() => {
  if (courseId.value) {
    loadChapters();
  }
});

// 路由变化时重新获取数据
watch(
    () => route.params.id,
    (newId) => {
      if (newId) {
        courseId.value = newId;
        previewResourceInfo.value = null;
        selectedResourceId.value = null;
        loadChapters();
        window.scrollTo(0, 0);
      }
    }
);

// 组件卸载时取消请求和清除定时器
onUnmounted(() => {
  if (courseRequestController.value) {
    courseRequestController.value.abort();
  }

  if (progressSaveInterval.value) {
    clearInterval(progressSaveInterval.value);
    progressSaveInterval.value = null;
  }
});

// 页面离开前保存进度
onBeforeUnmount(() => {
  if (userId.value && currentVideoId.value && previewResourceInfo.value && previewResourceInfo.value.type === 'video' && videoRef.value) {
    const progress = videoRef.value.currentTime / videoRef.value.duration;
    saveVideoProgress(currentVideoId.value, progress);
  }
  // 清除定时器
  if (progressSaveInterval.value) {
    clearInterval(progressSaveInterval.value);
    progressSaveInterval.value = null;
  }
});
</script>

<style scoped>
/* 全局布局：Flex垂直布局，适配固定导航栏 */
.pc-container {
  width: 100%;
  height: 100vh;
  position: relative;
  background-color: #f0f7f4;
  font-family: 'Inter', 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 导航栏固定样式 */
:deep(.NavigationBar) {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 999;
  background-color: #f0f7f4;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 内容包裹层 */
.content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 20px;
}

.pc-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 30px;
  box-sizing: border-box;
}

/* 面包屑容器 */
.breadcrumb-container {
  width: 100%;
  margin-top: 20px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
}

/* 面包屑样式 - 与参考页保持一致 */
.breadcrumb {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  flex: 1;
}

.breadcrumb-link {
  cursor: pointer;
  color: #333;
  margin-right: 8px;
  transition: color 0.2s;
}
.breadcrumb-link:hover {
  color: #20c997;
}
.breadcrumb-separator {
  margin: 0 8px;
  color: #e0e0e0;
}
.breadcrumb-current {
  color: #999;
  font-weight: 500;
}

/* 讨论区按钮样式 - 紧凑化间距 */
.course-discussion-toggle {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #fff;
  transition: all 0.3s ease;
  cursor: pointer;
  padding: 5px 15px;
  display: inline-flex;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.course-discussion-toggle:hover {
  border-color: #20c997;
  background-color: #f0f7f4;
}

.discussion-header {
  display: flex;
  align-items: center;
  padding: 0;
}

.discussion-icon {
  color: #2b6a3d;
  margin-right: 8px;
}

.discussion-title {
  font-size: 16px;
  color: #333;
  white-space: nowrap;
}

.discussion-count {
  background-color: #2b6a3d;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin: 0 8px;
}

.discussion-arrow {
  transition: transform 0.3s ease;
  color: #909399;
}

.rotate-180 {
  transform: rotate(180deg);
}

/* 加载与错误状态 */
.loading-state {
  padding: 60px 0;
  text-align: center;
  margin-bottom: 20px;
}

.error-state {
  padding: 30px 0;
  margin-bottom: 20px;
}

/* 章节+资料容器*/
.course-bottom-container {
  min-height: 650px;
  display: flex;
  gap: 30px;
  box-sizing: border-box;
  margin-bottom: 30px;
}

/* 左侧章节区域 */
.content-section {
  width: 350px;
  background-color: #fff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e9e5;
  box-sizing: border-box;
  flex-shrink: 0; /* 防止宽度被挤压 */
}

.section-title {
  font-size: 18px;
  color: #2b6a3d;
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #e5e5e5;
  font-weight: 600;
  text-align: center;
}

/* 章节项样式 */
.chapter-item {
  border: 2px solid #dcdfe6;
  border-radius: 8px;
  margin-bottom: 8px;
  padding: 8px;
  transition: all 0.3s ease;
  position: relative;
  background-color: #fff;
  cursor: pointer;
}

.chapter-item:hover {
  box-shadow: 0 4px 16px 0 rgba(43, 106, 61, 0.15);
  border-color: #2b6a3d;
}

.chapter-expanded {
  border-color: #2b6a3d;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chapter-index {
  font-size: 18px;
  color: #2b6a3d;
  font-weight: 600;
  line-height: 30px;
}

.chapter-title {
  font-size: 18px;
  color: #000;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 30px;
}

.chapter-content {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #dcdfe6;
}

/* 资源列表样式 */
.resource-list {
  margin-bottom: 8px;
}

.resource-item {
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #dcdfe6;
  transition: all 0.3s ease;
  cursor: pointer;
}

.resource-item:hover, .resource-hover {
  padding-left: 5px;
  background-color: #f8f9fa;
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

/* 资料名样式 */
.resource-title {
  font-size: 16px;
  color: #000;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 30px;
}

.resource-type-tag {
  font-size: 14px;
  font-weight:600;
  color: #000000;
  background-color: #2c824a;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  line-height: 30px;
  margin-left: 5px;
  margin-right: 5px;
}

.resource-item:hover .resource-type-tag,
.resource-hover .resource-type-tag {
  color: #ffffff;
  background-color: #2c824a;
}

.resource-item.resource-active .resource-type-tag {
  color: #ffffff;
  background-color: #2c824a;
}

.empty-resource {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 10px 0;
  color: #999;
  font-size: 14px;
}

.empty-tip {
  text-align: center;
  padding: 40px 0;
  color: #999;
  font-size: 16px;
}

/* 右侧资料详情区域 */
.material-section {
  flex: 1;
  background-color: #fff;
  border-radius: 12px;
  padding: 30px 10px 0 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e9e5;
  box-sizing: border-box;
}

.material-detail {
  padding: 0;
  border: 1px solid #e0e9e5;
  border-radius: 6px;
  margin-top: 10px;
  box-sizing: border-box;
  min-height: calc(100vh - 320px); 
  overflow-y: auto;
}

.material-section .material-detail {
  min-height: calc(100vh - 320px); 
  overflow-y: hidden;
}

/* 预览容器 */
.preview-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.preview-content {
  width: 100%;
  position: relative;
  padding-bottom: 10px;
}

/* 视频预览区域 */
.video-wrapper {
  padding: 20px 0;
  width: 100%;
  display: flex;
  justify-content: center;
}

.video-wrapper video {
  max-width: 100%;
  max-height: 500px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
}

.video-error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f56c6c;
  font-size: 14px;
  padding: 10px 20px;
  border-radius: 4px;
  z-index: 1;
}

/* PDF预览样式 */
.pdf-preview {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 700px;
  padding: 20px 0;
}

.pdf-container {
  border: 1px solid #e9ecef;
  border-radius: 4px;
  background-color: #f9f9f9;
  overflow: hidden;
  position: relative;
  min-width: 800px;
  height: 600px;
  width: 110%;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.no-pdf-url, .loading-pdf, .pdf-error {
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

/* PPT预览区域 */
.ppt-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.loading-pptx {
  width: 100%;
  max-width: 800px;
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 16px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
}

/* 文档错误状态样式 */
.pptx-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 800px;
  height: 500px;
  color: #f56c6c;
  font-size: 14px;
  background-color: #fff;
  border: 1px solid #ffe3e3;
  border-radius: 4px;
}

/* Word文档加载样式 */
.loading-docx {
  width: 800px;
  height: 500px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 16px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
}

.docx-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 800px;
  height: 500px;
  margin: 0 auto;
  color: #f56c6c;
  font-size: 14px;
  background-color: #fff;
  border: 1px solid #ffe3e3;
  border-radius: 4px;
}

/* 文档预览样式 */
.doc-preview {
  flex: 1;
  max-height: 500px;
  overflow-y: auto;
  width: 95%;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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
}

.doc-content {
  line-height: 1.8;
  color: #444;
  font-size: 14px;
}
.doc-text {
  text-align: left;
}
.doc-text h1, .doc-text h2, .doc-text h3 {
  margin: 1.5em 0 0.8em;
  font-weight: 600;
  color: #2b6a3d;
  border-left: 4px solid #2b6a3d;
  padding-left: 10px;
}
.doc-text p {
  margin: 0.8em 0;
  text-indent: 2em;
}
.doc-text ul, .doc-text ol {
  margin: 0.8em 0 0.8em 2em;
  padding-left: 1em;
}

/* 文本预览 */
.txt-content {
  width: 100%;
  min-height: 300px;
  max-height: 500px;
  padding: 20px;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  background-color: #fff;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  color: #333;
}

/* 加载文本样式 */
.loading-txt {
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

/* 图片预览 */
.preview-image {
  max-width: 100%;
  max-height: 500px;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  object-fit: contain;
}

/* 其他文件样式 */
.other-document-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  border: 1px dashed #e5e7eb;
  border-radius: 4px;
  min-height: 400px;
}

.file-icon {
  color: #909399 !important;
  margin-bottom: 20px;
}

.file-info {
  text-align: center;
  margin-bottom: 20px;
}

.file-info h4 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #333;
}

.file-info p {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

/* 预览操作按钮 */
.preview-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

/* 空预览状态 */
.empty-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 500px;
  color: #909399;
  font-size: 16px;
}

.empty-icon {
  color: #e0e0e0 !important;
  margin-bottom: 20px;
}

/* 加载状态样式 */
.loading-preview {
  width: 100%;
  max-width: 800px;
  padding: 20px;
}
</style>