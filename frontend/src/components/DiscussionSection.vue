<template>
  <!-- 讨论区内容 -->
  <div
    class="discussion-overlay"
    v-if="isOpen"
    :class="{ 'discussion-visible': isOpen }"
  >
    <!-- 遮罩层：阻止父组件交互 -->
    <div class="discussion-backdrop" @click="handleClose"></div>

    <div class="discussion-container">
      <div class="discussion-content">
        <div class="discussion-title-bar">
          <h3>讨论区</h3>
          <span class="close-btn" @click="handleClose">
            <el-icon><Close /></el-icon>
          </span>
        </div>

        <!-- 讨论区输入框 -->
        <div class="discussion-input-area">
          <div class="user-avatar">
            <img
              :src="realUserAvatar || 'https://picsum.photos/200/200?random=user'"
              alt="当前用户头像"
              class="avatar-image"
              @error="handleAvatarError('current-user', e.target.src)"
            >
          </div>
          <div class="input-wrapper">
            <el-input
              v-model="newComment"
              type="textarea"
              :rows="3"
              placeholder="分享你的想法或提问..."
              @keyup.enter.native="postComment"
            ></el-input>
            <div class="input-actions">
              <label class="image-upload-btn">
                <el-icon size="20"><Picture /></el-icon>
                <input
                  type="file"
                  class="image-upload-input"
                  accept="image/png, image/jpg, image/jpeg"
                  @change="handleImageUpload"
                >
              </label>
              <el-button
                type="primary"
                size="default"
                @click="postComment"
                :loading="isPostingComment"
                :disabled="!isCommentValid"
              >
                发布
              </el-button>
            </div>
            <div v-if="selectedImage" class="selected-image-preview">
              <img :src="selectedImage" alt="预览图" class="preview-thumbnail">
              <span class="remove-image" @click="removeImage">
                <el-icon size="16"><Close /></el-icon>
              </span>
            </div>
          </div>
        </div>

        <!-- 评论列表 -->
        <div class="discussion-list">
          <div v-if="loadingComments" class="loading-comments">
            <el-skeleton animated :rows="5" />
          </div>
          <div v-else-if="comments && comments.length > 0">
            <div v-for="(comment, index) in comments" :key="comment.comment_id" class="comment-item">
              <!-- 评论头部信息 -->
              <div class="comment-header">
                <div class="user-info">
                  <img
                    :src="fixCoverPath(comment.user_avatar)" 
                    :alt="`${comment.user_name || '用户'}的头像`"
                    class="user-avatar-img"
                    @error="handleAvatarError(`comment-${index}`, fixCoverPath(comment.user_avatar), comment)"
                  >
                  <div class="user-details">
                    <div class="user-name">
                      {{ comment.user_name || '匿名用户' }}
                      <span class="user-role" :class="isTeacher(comment.user_role) ? 'teacher-tag' : 'student-tag'">
                        {{ isTeacher(comment.user_role) ? '教师' : '学生' }}
                      </span>
                    </div>
                    <div class="comment-time">{{ comment.created_at }}</div>
                  </div>
                </div>
                <div class="comment-actions">
                  <span class="like-btn" @click="toggleLike(comment.comment_id)">
                    <el-icon :class="{'liked': isCommentLiked(comment.comment_id)}">
                      <Pointer />
                    </el-icon>
                    <span>{{ comment.total_likes || 0 }}</span>
                  </span>
                  <el-dropdown @command="(command) => handleCommentCommand(command, comment, null)" trigger="click" placement="bottom-start">
                    <span class="more-btn">
                      <el-icon><MoreFilled /></el-icon>
                    </span>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="copy" :data-id="comment.comment_id" :data-type="comment.comment_type || 'comment'">
                          <el-icon size="14"><CopyDocument /></el-icon>
                          复制评论内容
                        </el-dropdown-item>
                        <el-dropdown-item 
                          command="delete" 
                          :data-id="comment.comment_id" 
                          :disabled="!canDeleteComment(comment)"
                        >
                          <el-icon size="14"><Delete /></el-icon>
                          删除
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </div>

              <!-- 评论内容 -->
              <div class="comment-content">
                <p>{{ comment.content }}</p>
                <img v-if="comment.image" :src="fixCoverPath(comment.image)" alt="评论图片" class="comment-image">
              </div>

              <!-- 回复区域 -->
              <div class="replies-container">
                <div class="view-replies" @click="toggleReplies(comment)">
                  <el-icon size="16" class="reply-icon"><ChatDotSquare /></el-icon>
                  <span>{{ comment.reply_count || 0 }}条回复</span>
                  <el-icon :class="{'rotate-180': comment.replies_expanded}">
                    <ArrowDown />
                  </el-icon>
                </div>

                <!-- 回复列表 -->
                <div v-if="comment.replies_expanded" class="replies-list-container">
                  <div v-if="comment.loading_replies" class="loading-replies">
                    <el-skeleton animated :rows="3" />
                  </div>
                  <div v-else-if="comment.replies && comment.replies.length > 0" class="replies-list">
                    <div v-for="(reply, rIndex) in buildNestedReplies(comment.replies)" :key="reply.id" :class="['reply-item', `depth-${reply.depth}`]">
                      <div class="reply-header">
                        <div class="user-info">
                          <img
                            :src="fixCoverPath(reply.user_avatar)"
                            :alt="`${reply.user_name || '用户'}的头像`"
                            class="reply-avatar-img"
                            @error="handleAvatarError(`comment-${index}-reply-${rIndex}`, fixCoverPath(reply.user_avatar), reply)"
                          >
                          <div class="user-details">
                            <div class="user-name">
                              {{ reply.user_name || '匿名用户' }}
                              <span class="user-role" :class="isTeacher(reply.user_role) ? 'teacher-tag' : 'student-tag'">
                                {{ isTeacher(reply.user_role) ? '教师' : '学生' }}
                              </span>
                            </div>
                            <div class="reply-time">{{ reply.created_at }}</div>
                          </div>
                        </div>
                        <div class="reply-actions">
                          <span class="like-btn" @click="toggleLike(reply.id)">
                            <el-icon :class="{'liked': isCommentLiked(reply.id)}">
                              <Pointer />
                            </el-icon>
                            <span>{{ reply.total_likes || 0 }}</span>
                          </span>
                          <el-dropdown @command="(command) => handleCommentCommand(command, null, reply)" trigger="click" placement="bottom-start">
                            <span class="more-btn">
                              <el-icon><MoreFilled /></el-icon>
                            </span>
                            <template #dropdown>
                              <el-dropdown-menu>
                                <el-dropdown-item command="copy" :data-id="reply.id" :data-type="reply.reply_type || 'reply'">
                                  <el-icon size="14"><CopyDocument /></el-icon>
                                  复制评论内容
                                </el-dropdown-item>
                                <el-dropdown-item 
                                  command="delete" 
                                  :data-id="reply.id" 
                                  :disabled="!canDeleteComment(reply)"
                                >
                                  <el-icon size="14"><Delete /></el-icon>
                                  删除
                                </el-dropdown-item>
                              </el-dropdown-menu>
                            </template>
                          </el-dropdown>
                        </div>
                      </div>
                      <div class="reply-content">
                        <p>{{ reply.content }}</p>
                        <img v-if="reply.image" :src="fixCoverPath(reply.image)" alt="回复图片" class="reply-image">
                      </div>
                    </div>
                  </div>
                  <div v-else class="empty-replies">
                    <p>暂无回复，快来抢沙发吧！</p>
                  </div>
                  <!-- 对楼主的回复框（保留） -->
                  <div class="reply-input-area">
                    <el-input
                      v-model="replyTexts[comment.comment_id]"
                      type="textarea"
                      :rows="1"
                      :placeholder="`回复 ${comment.user_name || '用户'}...`"
                      @keyup.enter.native="postReply(comment.comment_id)"
                    ></el-input>
                    <div class="reply-actions">
                      <label class="image-upload-btn">
                        <el-icon size="16"><Picture /></el-icon>
                        <input
                          type="file"
                          class="image-upload-input"
                          accept="image/png, image/jpg, image/jpeg"
                          @change="handleReplyImageUpload($event, comment.comment_id)"
                        >
                      </label>
                      <el-button
                        type="primary"
                        size="default"
                        @click="postReply(comment.comment_id)"
                        :loading="replyLoading[comment.comment_id]"
                        :disabled="!replyTexts[comment.comment_id]?.trim()"
                      >
                        回复
                      </el-button>
                    </div>
                    <div v-if="replyImages[comment.comment_id]" class="selected-image-preview reply-preview">
                      <img :src="replyImages[comment.comment_id]" alt="回复预览图" class="preview-thumbnail">
                      <span class="remove-image" @click="removeReplyImage(comment.comment_id)">
                        <el-icon size="16"><Close /></el-icon>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-comments">
            <el-icon size="24"><ChatLineRound /></el-icon>
            <p>暂无讨论，快来发起第一个话题吧！</p>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="pagination && pagination.pages > 1" class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            :page-size="pagination.per_page"
            layout="prev, pager, next"
            :total="pagination.total"
            @current-change="loadComments"
            background
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed, nextTick } from 'vue';
import { 
  ElInput, ElButton, ElSkeleton, ElMessage, ElIcon, ElPagination, 
  ElMessageBox, ElDropdown, ElDropdownMenu, ElDropdownItem 
} from 'element-plus';
import axiosInstance from '@/service/api.js';
import { fixCoverPath } from '@/utils/format.js';
import { 
  ChatLineRound, ArrowDown, Close, Picture, Pointer, ChatDotSquare, 
  Delete, MoreFilled, CopyDocument 
} from '@element-plus/icons-vue';

const props = defineProps({
  courseId: { type: [String, Number], required: true },
  courseName: { type: String, default: '' },
  isOpen: { type: Boolean, default: false },
  userAvatar: { type: String, default: '' }
});

const emit = defineEmits(['close', 'reset']); // 新增reset事件，供父组件触发重置

// 状态管理
const comments = ref([]);
const pagination = ref({ page: 1, per_page: 20, total: 0, pages: 0 });
const loadingComments = ref(false);
const newComment = ref('');
const isPostingComment = ref(false);
const replyTexts = ref({});
const replyLoading = ref({});
const likedComments = ref(new Set()); 
const selectedImage = ref(null);
const imageFile = ref(null);
const realUserAvatar = ref('');
const dialogWidth = ref('30%');

// 回复相关状态
const replyImages = ref({});
const replyImageFiles = ref({});

// 用户信息
const userId = ref(sessionStorage.getItem('id'));
const userRole = ref(sessionStorage.getItem('role')); // 0:学生, 1:教师, 2:管理员

// ========== 核心业务逻辑 ==========
// 身份判断方法（兼容数字/字符串）
const isTeacher = (role) => {
  if (role === undefined || role === null) {
    return false;
  }
  // 兼容多种情况：1/'1'/'teacher' 都视为教师
  const roleStr = String(role).toLowerCase();
  const result = roleStr === '1' || roleStr === 'teacher';
  return result;
};

// 评论验证
const isCommentValid = computed(() => {
  const isValid = newComment.value.trim() !== '';
  return isValid;
});

// 检查是否有权限删除评论
const canDeleteComment = (comment) => {
  // 空值保护
  if (!comment) {
    return false;
  }
  
  // 提取关键信息
  const currentUserId = userId.value || '未登录';
  const currentUserRole = userRole.value || '未知角色';
  const commentUserId = comment.user_id || '无作者ID';
  const commentId = comment.comment_id || comment.id || '无ID';
  
  // 权限判断
  const isAdmin = currentUserRole === '2' || currentUserRole === 2;
  const isAuthor = (currentUserId !== '未登录') && (String(currentUserId) === String(commentUserId));
  const hasPermission = isAdmin || isAuthor;
  
  return hasPermission;
};

const handleAvatarError = (avatarKey, src, data = {}) => {
  // 空实现，保留接口
};

// 复制评论内容
const copyCommentContent = (content) => {
  try {
    if (!content) {
      ElMessage.warning('评论内容为空，无法复制');
      return;
    }
    // 复制评论内容到剪贴板
    navigator.clipboard.writeText(content).then(() => {
      ElMessage.success('评论内容已复制到剪贴板');
    }).catch(() => {
      // 降级方案：创建临时input复制
      const input = document.createElement('input');
      input.value = content;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      ElMessage.success('评论内容已复制到剪贴板');
    });
  } catch (error) {
    ElMessage.error('复制失败，请手动复制');
  }
};

// 处理评论/回复操作（复制/删除）
const handleCommentCommand = (command, comment = null, reply = null) => {
  // 优先取回复数据，再取评论数据
  const targetItem = reply || comment;
  if (!targetItem) {
    return;
  }
  const commentId = targetItem.comment_id || targetItem.id;

  switch(command) {
    case 'copy':
      copyCommentContent(targetItem.content);
      break;
    case 'delete':
      deleteComment(commentId);
      break;
    default:
      break;
  }
};

// 获取用户头像
const fetchUserAvatar = async () => {
  if (!userId.value) {
    return;
  }
  
  try {
    let response;
    const roleNum = Number(userRole.value);
    
    if (roleNum === 0) {
      response = await axiosInstance.get(`/api/student/get-student-info`, { params: { student_id: userId.value } });
    } else if (roleNum === 1) {
      response = await axiosInstance.get(`/api/teacher/get-teacher-info`, { params: { teacher_id: userId.value } });
    } else {
      return;
    }
    
    if (response?.data?.success) {
      const rawAvatar = response.data.data?.avatar || '';
      realUserAvatar.value = fixCoverPath(rawAvatar);
    }
  } catch (error) {
    // 静默失败，保留默认头像
  }
};

// 关闭讨论区
const handleClose = () => {
  resetCommentForm();
  resetDiscussionState(); // 关闭时重置内部状态
  emit('close');
  document.documentElement.classList.remove('discussion-lock');
  document.body.classList.remove('discussion-lock');
  const parentContainer = document.querySelector('.pc-container');
  if (parentContainer) {
    parentContainer.classList.remove('discussion-open');
  }
};

// 重置评论表单
const resetCommentForm = () => {
  newComment.value = '';
  selectedImage.value = null;
  imageFile.value = null;
};

// 新增：重置讨论区所有状态（供关闭/父组件调用）
const resetDiscussionState = () => {
  comments.value = [];
  pagination.value = { page: 1, per_page: 20, total: 0, pages: 0 };
  replyTexts.value = {};
  replyLoading.value = {};
  replyImages.value = {};
  replyImageFiles.value = {};
  likedComments.value = new Set();
};

// 处理图片上传
const handleImageUpload = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  // 验证文件类型
  if (!['image/png', 'image/jpg', 'image/jpeg'].includes(file.type)) {
    ElMessage.error('仅支持PNG/JPG/JPEG格式的图片');
    e.target.value = '';
    return;
  }
  
  // 验证文件大小
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过10MB');
    e.target.value = '';
    return;
  }
  
  // 读取文件预览
  const reader = new FileReader();
  reader.onload = (event) => {
    selectedImage.value = event.target.result;
  };
  reader.readAsDataURL(file);
  imageFile.value = file;
  e.target.value = '';
};

const removeImage = () => {
  selectedImage.value = null;
  imageFile.value = null;
};

const handleReplyImageUpload = (e, commentId) => {
  const file = e.target.files[0];
  if (!file) return;
  
  // 验证文件类型
  if (!['image/png', 'image/jpg', 'image/jpeg'].includes(file.type)) {
    ElMessage.error('仅支持PNG/JPG/JPEG格式的图片');
    e.target.value = '';
    return;
  }
  
  // 验证文件大小
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过10MB');
    e.target.value = '';
    return;
  }
  
  // 读取文件预览
  const reader = new FileReader();
  reader.onload = (event) => {
    replyImages.value[commentId] = event.target.result;
  };
  reader.readAsDataURL(file);
  replyImageFiles.value[commentId] = file;
  e.target.value = '';
};

const removeReplyImage = (commentId) => {
  replyImages.value[commentId] = null;
  replyImageFiles.value[commentId] = null;
};

// 加载评论
const loadComments = async (page = 1) => {
  if (!props.courseId) {
    return;
  }
  
  loadingComments.value = true;
  try {
    const response = await axiosInstance.get(`/api/course/comment/${props.courseId}/get-comments-by-course`, {
      params: { page, per_page: pagination.value.per_page }
    });
    
    if (!response.data.success) {
      throw new Error(response.data.message || '获取讨论区数据失败');
    }
    
    const commentData = response.data.data;
    comments.value = commentData.comments || [];
    pagination.value = commentData.pagination;

    // 初始化评论状态
    comments.value.forEach((comment, index) => {
      comment.replies_expanded = false;
      comment.loading_replies = false;
      comment.replies = null;
      replyTexts.value[comment.comment_id] = '';
      replyLoading.value[comment.comment_id] = false;
      replyImages.value[comment.comment_id] = null;
      replyImageFiles.value[comment.comment_id] = null;
      
      // 确保回复数量字段有默认值，避免显示NaN/undefined
      if (comment.reply_count === undefined || comment.reply_count === null) {
        comment.reply_count = 0;
      }
    });
  } catch (error) {
    const errorMsg = error.response?.data?.message || error.message || '网络错误，无法获取评论';
    ElMessage.error(errorMsg);
  } finally {
    loadingComments.value = false;
  }
};

// 发布评论
const postComment = async () => {
  // 前置验证
  if (!userId.value) { 
    ElMessage.error('请先登录'); 
    return; 
  }
  if (userRole.value === '2' || userRole.value === 2) { 
    ElMessage.error('管理员不可发布评论'); 
    return; 
  }
  if (!isCommentValid.value) { 
    ElMessage.warning('内容不能为空'); 
    return; 
  }

  isPostingComment.value = true;
  try {
    const formData = new FormData();
    formData.append('content', newComment.value);
    formData.append('user_id', userId.value);
    formData.append('parent_id', -1);
    if (imageFile.value) formData.append('image', imageFile.value);

    const response = await axiosInstance.post(
      `/api/course/comment/${props.courseId}/create-comment`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    
    if (!response.data.success) {
      throw new Error(response.data.message || '发布评论失败');
    }

    ElMessage.success('评论发布成功');
    resetCommentForm();
    loadComments(pagination.value.page);
  } catch (error) {
    const errorMsg = error.response?.data?.message || error.message || '网络错误，无法发布评论';
    ElMessage.error(errorMsg);
  } finally {
    isPostingComment.value = false;
  }
};

// ========== 适配x-www-form-urlencoded的删除评论方法 ==========
const deleteComment = async (commentId) => {
  try {
    // 1. 调整二次确认按钮：文字改为"确认"，样式改为绿色（primary）
    await ElMessageBox.confirm(
      '此操作将删除该评论，是否继续?',
      '提示',
      {
        confirmButtonText: '确认', // 按钮文字改为"确认"
        cancelButtonText: '取消',
        type: 'primary', // 绿色风格按钮
        confirmButtonClass: 'custom-confirm-btn' // 自定义类名确保绿色样式
      }
    );
  
    // 2. 使用URLSearchParams适配x-www-form-urlencoded格式（替代FormData）
    const params = new URLSearchParams();
    params.append('comment_id', commentId);

    // 3. 发送DELETE请求，使用默认的application/x-www-form-urlencoded请求头
    const response = await axiosInstance.delete('/api/course/comment/delete-comment', {
      data: params // 传递urlencoded格式参数
    });
    
    if (!response.data.success) {
      throw new Error(response.data.message || '删除评论失败');
    }

    // 4. 简化成功提示，只显示"评论删除成功"
    ElMessage.success('评论删除成功');
    
    // 重新加载评论列表
    loadComments(pagination.value.page);
  } catch (error) {
    if (error !== 'cancel') {
      // 区分不同错误类型给出精准提示
      const statusCode = error.response?.status;
      const errorMsg = error.response?.data?.message || error.message || '操作失败';
      
      // 后端定义的错误码提示
      if (statusCode === 404) {
        ElMessage.error('评论不存在或已被删除');
      } else if (statusCode === 403) {
        ElMessage.error('无权限删除该评论（仅管理员或评论作者可删除）');
      } else if (statusCode === 500) {
        ElMessage.error('服务器错误，删除失败');
      } else if (statusCode === 401) {
        ElMessage.error('请先登录后再操作');
      } else {
        ElMessage.error(errorMsg);
      }
    }
  }
};

// 点赞/取消点赞
const toggleLike = async (commentId) => {
  if (!userId.value) { 
    ElMessage.error('请先登录'); 
    return; 
  }
  
  const isLiked = isCommentLiked(commentId);
  
  try {
    // 点赞接口也适配x-www-form-urlencoded格式
    const params = new URLSearchParams();
    params.append('user_id', userId.value);
    params.append('comment_id', commentId);
    params.append('is_like', !isLiked);

    const response = await axiosInstance.post(
      `/api/course/comment/like-comment`,
      params
    );
    
    if (!response.data.success) {
      throw new Error(response.data.message || '操作失败');
    }

    // 更新本地点赞状态
    if (!isLiked) {
      likedComments.value.add(commentId);
    } else {
      likedComments.value.delete(commentId);
    }

    // 更新点赞数
    const updateLikesCount = (items) => {
      for (const item of items) {
        if (item.comment_id === commentId || item.id === commentId) {
          item.likes = (item.likes || 0) + (!isLiked ? 1 : -1);
          item.total_likes = (item.total_likes || 0) + (!isLiked ? 1 : -1);
          break;
        }
        if (item.replies) {
          updateLikesCount(item.replies);
        }
      }
    };
    updateLikesCount(comments.value);

  } catch (error) {
    const errorMsg = error.response?.data?.message || error.message || '网络错误，无法完成点赞';
    ElMessage.error(errorMsg);
  }
};

// 判断是否点赞
const isCommentLiked = (commentId) => {
  const result = likedComments.value.has(commentId);
  return result;
};

// 展开/收起回复
const toggleReplies = async (comment) => {
  if (!comment?.comment_id) {
    return;
  }
  
  if (comment.replies_expanded) {
    comment.replies_expanded = false;
    return;
  }
  
  comment.loading_replies = true;
  try {
    const response = await axiosInstance.get(`/api/course/comment/${comment.comment_id}/get-replies-by-comment`);
    
    if (!response.data.success) {
      throw new Error(response.data.message || '获取回复失败');
    }
    
    comment.replies = response.data.data.replies;
    comment.replies_expanded = true;

    // 初始化回复状态
    replyTexts.value[comment.comment_id] = '';
    replyLoading.value[comment.comment_id] = false;
    replyImages.value[comment.comment_id] = null;
    replyImageFiles.value[comment.comment_id] = null;
  } catch (error) {
    const errorMsg = error.response?.data?.message || error.message || '网络错误，无法加载回复';
    ElMessage.error(errorMsg);
  } finally {
    comment.loading_replies = false;
  }
};

// 构建嵌套回复列表
const buildNestedReplies = (replies) => {
  let flatList = [];
  const build = (items, depth = 1) => {
    for (const item of items) {
      item.depth = depth;
      flatList.push(item);
      if (item.replies && item.replies.length > 0) {
        build(item.replies, depth + 1);
      }
    }
  };
  build(replies || []);
  return flatList;
};

// 发布回复（适配x-www-form-urlencoded，图片上传仍用formdata）
const postReply = async (parentId) => {
  const replyText = replyTexts.value[parentId];
  // 前置验证
  if (!replyText?.trim()) { 
    ElMessage.warning('请输入回复内容'); 
    return; 
  }
  if (!userId.value) { 
    ElMessage.error('请先登录'); 
    return; 
  }

  replyLoading.value[parentId] = true;
  try {
    // 有图片时仍用FormData，无图片时用URLSearchParams
    let requestData;
    let headers = {};
    
    if (replyImageFiles.value[parentId]) {
      const formData = new FormData();
      formData.append('content', replyText);
      formData.append('user_id', userId.value);
      formData.append('parent_id', parentId);
      formData.append('image', replyImageFiles.value[parentId]);
      requestData = formData;
      headers = { 'Content-Type': 'multipart/form-data' };
    } else {
      const params = new URLSearchParams();
      params.append('content', replyText);
      params.append('user_id', userId.value);
      params.append('parent_id', parentId);
      requestData = params;
    }

    const response = await axiosInstance.post(
      `/api/course/comment/${props.courseId}/create-comment`,
      requestData,
      { headers }
    );
    
    if (!response.data.success) {
      throw new Error(response.data.message || '发布回复失败');
    }

    ElMessage.success('回复发布成功');
    
    // 重置表单
    replyTexts.value[parentId] = '';
    replyImages.value[parentId] = null;
    replyImageFiles.value[parentId] = null;

    // 关键：发布回复后重新加载整个评论列表，确保回复数量实时更新
    await loadComments(pagination.value.page);
    
    // 保持该评论的回复展开状态
    const parentComment = comments.value.find(c => c.comment_id === parentId);
    if (parentComment) {
      await toggleReplies(parentComment);
    }
  } catch (error) {
    const errorMsg = error.response?.data?.message || error.message || '网络错误，无法发布回复';
    ElMessage.error(errorMsg);
  } finally {
    replyLoading.value[parentId] = false;
  }
};

// ========== 监听与初始化 ==========
// 监听讨论区状态 - 每次打开都强制刷新
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    document.documentElement.classList.add('discussion-lock');
    document.body.classList.add('discussion-lock');
    const parentContainer = document.querySelector('.pc-container');
    if (parentContainer) parentContainer.classList.add('discussion-open');
    // 移除原有判断，确保每次打开都刷新最新数据
    loadComments();
  } else {
    handleClose();
  }
}, { immediate: true });

// 监听课程ID变化 - 强制刷新
watch(() => props.courseId, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    resetDiscussionState(); // 切换课程时重置状态
    pagination.value.page = 1;
    if (props.isOpen) {
      loadComments();
    }
  }
});

// 初始化
onMounted(() => {
  fetchUserAvatar();
  if (props.isOpen && props.courseId) {
    loadComments();
  }
});
</script>

<style scoped>
/* 全局滚动锁定 */
.discussion-lock {
  overflow: hidden !important;
  height: 100% !important;
  touch-action: none !important;
}

.discussion-overlay {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease, visibility 0.3s ease;
}

.discussion-visible {
  opacity: 1;
  visibility: visible;
}

.discussion-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  backdrop-filter: blur(2px);
}

.discussion-container {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 50%;
  max-width: 800px;
  background-color: #fff;
  transform: translateX(0);
  transition: transform 0.3s ease;
  overflow: hidden;
  box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.pc-container.discussion-open {
  overflow: hidden !important;
  touch-action: none;
}

.discussion-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.discussion-title-bar {
  padding: 15px;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.discussion-title-bar h3 {
  font-size: 20px;
  color: #2b6a3d;
  margin: 0;
  font-weight: 600;
}

.close-btn {
  cursor: pointer;
  color: #909399;
  transition: color 0.2s;
  padding: 5px;
}

.close-btn:hover {
  color: #2b6a3d;
}

.discussion-input-area {
  display: flex;
  gap: 10px;
  margin: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.input-wrapper {
  flex: 1;
}

.comment-title-input {
  margin-bottom: 10px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
  align-items: center;
  gap: 10px;
}

.image-upload-btn {
  display: flex;
  align-items: center;
  color: #666;
  cursor: pointer;
  padding: 5px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  transition: all 0.2s;
}

.image-upload-input {
  display: none;
}

.selected-image-preview {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.selected-image-preview.reply-preview {
  margin-top: 5px;
}

.preview-thumbnail {
  width: 100px;
  height: auto;
  border-radius: 4px;
  border: 1px solid #eee;
}

.remove-image {
  color: #f56c6c;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.discussion-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 15px;
  scrollbar-width: thin;
  scrollbar-color: #ccc #f5f5f5;
}

.discussion-list::-webkit-scrollbar {
  width: 6px;
}

.discussion-list::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 3px;
}

.discussion-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.loading-comments, .loading-replies {
  padding: 20px;
}

.comment-item {
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  align-items: center;
}

.user-info {
  display: flex;
  gap: 10px;
  align-items: center;
  flex: 1;
}

.user-avatar-img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  display: flex;
  align-items: center;
  gap: 5px;
}

.user-role {
  font-size: 12px;
  padding: 1px 4px;
  border-radius: 3px;
}

.teacher-tag {
  background-color: #e6f7ed;
  color: #2b6a3d;
}

.student-tag {
  background-color: #f5f7fa;
  color: #909399;
}

.reply-time, .comment-time {
  font-size: 12px;
  color: #909399;
}

.comment-actions, .reply-actions {
  display: flex;
  gap: 15px;
  color: #909399;
  align-items: center;
}

.like-btn, .delete-btn {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: color 0.2s;
  gap: 5px;
  font-size: 14px;
  padding: 2px 5px;
}

.like-btn:hover, .delete-btn:hover {
  color: #f56c6c;
}

.liked {
  color: #f56c6c !important;
}

.more-btn {
  cursor: pointer;
  padding: 2px 5px;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.more-btn:hover {
  background-color: #f5f5f5;
}

.comment-content {
  margin-bottom: 15px;
  padding-left: 46px;
  text-align: left;
}

.comment-content p {
  margin: 0;
  line-height: 1.6;
  color: #333;
  font-size: 14px;
}

.comment-image {
  max-width: 100%;
  max-height: 200px;
  margin-top: 10px;
  border-radius: 4px;
}

.replies-container {
  margin-top: 15px;
  padding-left: 46px;
  text-align: left;
}

.view-replies {
  display: flex;
  align-items: center;
  color: #2b6a3d;
  cursor: pointer;
  margin-bottom: 10px;
  font-size: 14px;
  gap: 5px;
}

.reply-icon {
  margin-right: 3px;
}

.view-replies:hover {
  text-decoration: underline;
}

.replies-list-container {
  border-left: 2px solid #f0f0f0;
  padding-left: 15px;
}

.replies-list {
  width: 100%;
}

.reply-item {
  padding: 15px 0;
  border-bottom: 1px solid #f9f9f9;
  width: 100%;
}

.reply-item:last-child {
  border-bottom: none;
}

.reply-item.depth-1 { padding-left: 0px; }
.reply-item.depth-2 { padding-left: 20px; }
.reply-item.depth-3 { padding-left: 40px; }
.reply-item.depth-4 { padding-left: 60px; }
.reply-item.depth-5 { padding-left: 80px; }

.reply-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 5px;
  align-items: center;
  width: 100%;
}

.reply-avatar-img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.reply-content {
  padding-left: 42px;
  text-align: left;
}

.reply-content p {
  margin: 0;
  line-height: 1.6;
  color: #666;
  font-size: 14px;
}

.reply-image {
  max-width: 100%;
  max-height: 150px;
  margin-top: 5px;
  border-radius: 4px;
}

.reply-input-area {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
  text-align: left;
}

.reply-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.empty-comments, .empty-replies {
  text-align: center;
  padding: 40px 0;
  color: #909399;
  font-size: 16px;
}

.empty-comments el-icon, .empty-replies el-icon {
  margin-bottom: 15px;
  color: #ccc;
}

.rotate-180 {
  transform: rotate(180deg);
  transition: transform 0.3s ease;
}

.pagination-container {
  padding: 15px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

:deep(.custom-confirm-btn) {
  background-color: #2b6a3d !important;
  border-color: #2b6a3d !important;
}
</style>