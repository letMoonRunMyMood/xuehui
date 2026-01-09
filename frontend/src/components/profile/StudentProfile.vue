<template>
  <div class="student-profile-container">
    <div v-if="isLoading" class="loading-state">
      <div class="skeleton-profile">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-info">
          <div class="skeleton-row"></div>
          <div class="skeleton-row"></div>
          <div class="skeleton-row"></div>
          <div class="skeleton-row"></div>
        </div>
      </div>
    </div>

    <div v-else-if="errorMessage" class="error-state">
      <el-alert type="error" :message="errorMessage" show-icon></el-alert>
    </div>

    <div v-else class="profile-content">
      <div class="header-row">
        <div class="avatar-wrap">
          <el-avatar
              class="avatar"
              :src="avatarUrl"
              size="120"
              shape="circle"
              :style="{ border: '2px solid #e5e9f2', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }"
              @error="handleAvatarLoadError"
          ></el-avatar>
        </div>
        <div class="basic-info">
          <div class="info-row">
            <span class="info-label">昵称：</span>
            <span class="info-value text-xl font-semibold">{{ student.username || '暂无昵称' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">身份：</span>
            <span class="info-value text-gray-500">{{ student.role || '学生' }}</span>
          </div>
        </div>
        <div class="edit-btn-wrap">
          <el-button
              type="primary"
              size="large"
              :style="{ padding: '12px 24px', fontSize: '16px', background: '#2b6a3d'}"
              @click="openEditDialog"
          >
            <el-icon><Edit /></el-icon>
            <span>编辑资料</span>
          </el-button>
        </div>
      </div>

      <!-- 资料信息栏：同步老师端，减小高度 -->
      <div class="profile-details">
        <div class="detail-item">
          <span class="label">用户名:</span>
          <span class="value">{{ student.username || '未设置' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">邮箱:</span>
          <span class="value">{{ student.email || '未设置' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">加入时间:</span>
          <span class="value">{{ formatDate(student.join_time) || '未记录' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">年级:</span>
          <span class="value">{{ student.grade || '未设置' }}</span>
        </div>
      </div>

      <!-- 新增：退出登录按钮（和老师端样式一致，靠右对齐） -->
      <div class="logout-btn-wrap">
        <el-button
            type="danger"
            size="large"
            :style="{ padding: '12px 24px', fontSize: '16px' , background: '#f56c6c', borderColor: '#f56c6c'}"
            @click="handleLogout"
        >
          <span>退出登录</span>
        </el-button>
      </div>
    </div>

    <!-- 学生端表单窗口：完全保留原有样式（年级选择等），无任何改动 -->
    <el-dialog
        v-model="editDialogVisible"
        title="编辑个人资料"
        width="500px"
        center
        :before-close="handleDialogClose"
    >
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="80px">
        <el-form-item label="头像">
          <div class="avatar-upload-container">
            <el-upload
                class="avatar-uploader"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleAvatarSelect"
                :before-upload="beforeAvatarUpload"
                :file-list="fileList"
            >
              <el-avatar
                  v-if="previewAvatar"
                  :src="previewAvatar"
                  size="160"
                  shape="circle"
                  class="avatar-uploader-img"
                  @error="handleAvatarLoadError"
              ></el-avatar>
              <div v-else class="avatar-uploader-icon">
                <el-icon><Plus /></el-icon>
              </div>
            </el-upload>
            <div class="upload-tips">支持5MB以内的png、jpg、jpeg格式图片</div>
          </div>
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" disabled></el-input>
        </el-form-item>
        <el-form-item label="年级" prop="grade">
          <el-select
              v-model="editForm.grade"
              placeholder="请选择年级"
              style="width: 100%"
          >
            <el-option
                v-for="item in gradeOptions"
                :key="item"
                :label="item"
                :value="item"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button type="primary" @click="submitEditForm">确认修改</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="cropDialogVisible" title="裁剪头像" width="600px">
      <vue-cropper
          ref="cropperRef"
          :img="cropImgUrl"
          :info="true"
          :outputSize="1"
          :outputType="'png'"
          :canScale="true"
          :autoCrop="true"
          :autoCropWidth="200"
          :autoCropHeight="200"
          :fixedBox="true"
      ></vue-cropper>
      <template #footer>
        <el-button @click="cropDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCrop">确认裁剪</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Plus, Edit } from '@element-plus/icons-vue';
import axiosInstance from '@/service/api.js';
import { VueCropper } from 'vue-cropper';
import 'vue-cropper/dist/index.css';
import { fixCoverPath } from '@/utils/format.js';
import eventBus, { EVENT_TYPES } from '@/utils/eventBus.js';

const route = useRoute();
const router = useRouter();

const isLoading = ref(true);
const errorMessage = ref('');
const student = ref({});
const defaultAvatar = ref('https://picsum.photos/200/200?random=student');
const avatarUrl = ref('');
const studentId = ref(null);
const editDialogVisible = ref(false);
const editFormRef = ref(null);
const previewAvatar = ref('');
const fileList = ref([]);

const cropDialogVisible = ref(false);
const cropImgUrl = ref('');
const cropperRef = ref(null);

const gradeOptions = ref([
  '初一', '初二', '初三',
  '高一', '高二', '高三'
]);

const editForm = reactive({
  username: '',
  email: '',
  grade: '',
});

const editRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }]
};

onMounted(() => {
  if (route.query.student_id) {
    studentId.value = parseInt(route.query.student_id);
    fetchStudentInfo(studentId.value);
  } else {
    const sessionStudentId = sessionStorage.getItem('id');
    if (sessionStudentId) {
      studentId.value = parseInt(sessionStudentId);
      fetchStudentInfo(studentId.value);
    } else {
      errorMessage.value = '缺少学生ID参数';
      isLoading.value = false;
    }
  }
});

watch(
    () => student.value,
    (newVal) => {
      if (newVal) {
        editForm.username = newVal.username || '';
        editForm.email = newVal.email || '';
        editForm.grade = newVal.grade || '';
        const fixedAvatar = fixCoverPath(newVal.avatar || '');
        previewAvatar.value = fixedAvatar || defaultAvatar.value;
        avatarUrl.value = fixedAvatar || defaultAvatar.value;
      }
    },
    { deep: true }
);

const fetchStudentInfo = async (id) => {
  isLoading.value = true;
  errorMessage.value = '';

  try {
    const response = await axiosInstance.get('/api/student/get-student-info', {
      params: { student_id: id }
    });
    if (response.data.success) {
      student.value = response.data.data;
      const backendAvatar = response.data.data?.avatar || '';
      const fixedAvatar = fixCoverPath(backendAvatar);
      avatarUrl.value = fixedAvatar || defaultAvatar.value;
      previewAvatar.value = fixedAvatar || defaultAvatar.value;
    } else {
      throw new Error(response.data.message || '获取头像失败');
    }
  } catch (error) {
    avatarUrl.value = defaultAvatar.value;
    previewAvatar.value = defaultAvatar.value;
    console.error('获取学生信息异常', error);
    errorMessage.value = '网络错误，请稍后再试';
  } finally {
    isLoading.value = false;
  }
};

const openEditDialog = () => {
  if (student.value) {
    editForm.username = student.value.username || '';
    editForm.email = student.value.email || '';
    editForm.grade = student.value.grade || '';
    const fixedAvatar = fixCoverPath(student.value.avatar || '');
    previewAvatar.value = fixedAvatar || defaultAvatar.value;
    fileList.value = [];
    editDialogVisible.value = true;
  } else {
    ElMessage.error('获取学生信息失败，无法编辑');
  }
};

const handleDialogClose = () => {
  editDialogVisible.value = false;
  cropDialogVisible.value = false;
  const fixedAvatar = fixCoverPath(student.value?.avatar || '');
  previewAvatar.value = fixedAvatar || defaultAvatar.value;
};

const beforeAvatarUpload = (file) => {
  const isAllowed = ['image/png', 'image/jpeg', 'image/jpg'].includes(file.type);
  const isLessThan5M = file.size / 1024 / 1024 < 5;

  if (!isAllowed) {
    ElMessage.error('请上传png、jpg或jpeg格式的图片');
  }
  if (!isLessThan5M) {
    ElMessage.error('图片大小不能超过5MB');
  }
  return isAllowed && isLessThan5M;
};

const handleAvatarSelect = (file) => {
  if (!file.raw) return;
  cropImgUrl.value = URL.createObjectURL(file.raw);
  cropDialogVisible.value = true;
};

const confirmCrop = () => {
  if (!cropperRef.value) return;
  cropperRef.value.getCropBlob((blob) => {
    const croppedFile = new File([blob], 'cropped-avatar.png', { type: 'image/png' });
    fileList.value = [{ raw: croppedFile }];
    previewAvatar.value = URL.createObjectURL(croppedFile);
    cropDialogVisible.value = false;
  });
};

const submitEditForm = async () => {
  if (!editFormRef.value) return;

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const formData = new FormData();
        formData.append('student_id', studentId.value);
        formData.append('username', editForm.username);
        formData.append('grade', editForm.grade);

        if (fileList.value.length > 0) {
          formData.append('avatar', fileList.value[0].raw);
        }

        const response = await axiosInstance.patch('/api/student/update-student-info', formData);

        if (response.data.success) {
          ElMessage.success('资料更新成功');
          handleDialogClose();
          fetchStudentInfo(studentId.value);
          eventBus.emit(EVENT_TYPES.AVATAR_UPDATED);
        } else {
          ElMessage.error(response.data.message || '更新失败，请重试');
        }
      } catch (error) {
        console.error('更新资料失败', error);
        ElMessage.error('网络错误，请稍后再试');
      }
    }
  });
};

const handleAvatarLoadError = () => {
  avatarUrl.value = defaultAvatar.value;
  previewAvatar.value = defaultAvatar.value;
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  try {
    const date = new Date(dateStr);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  } catch (error) {
    return '';
  }
};

// 新增：退出登录核心方法（和老师端逻辑完全一致）
const handleLogout = async () => {
  try {
    await axiosInstance.post('/api/auth/logout', {});
    sessionStorage.clear();
    ElMessage.success('已退出登录');
    router.push('/auth');
  } catch (error) {
    console.error('退出登录失败', error);
    ElMessage.error('退出登录失败，请稍后再试');
  }
};
</script>

<style scoped>
.student-profile-container {
  flex: 1;
  background-color: #fff;
  padding: 24px;
  box-sizing: border-box;
  min-height: 600px;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e9f2;
}

.avatar-wrap {
  margin-right: 24px;
}

.avatar {
  width: 120px;
  height: 120px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.basic-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.info-row {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.info-label {
  font-size: 18px;
  font-weight: 500;
  color: #666;
  min-width: 60px;
  margin-right: 12px;
}

.info-value {
  color: #666;
  font-size: 18px;
  font-weight: 500;
}

.edit-btn-wrap {
  margin-left: 24px;
}

/* 同步老师端：减小资料信息栏高度 */
.profile-details {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  margin-bottom: 20px; /* 预留退出按钮空间 */
}

.detail-item {
  display: flex;
  align-items: flex-start;
  background-color: #f8fafc;
  border-radius: 8px;
  padding: 10px 20px; /* 减小内边距，降低单个资料项高度 */
  border: 1px solid #e5e9f2;
  transition: all 0.2s ease;
}

.detail-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transform: translateY(-1px);
}

.detail-item .label {
  font-weight: 500;
  color: #666;
  min-width: 100px;
  font-size: 16px; /* 减小字体大小，降低资料项高度 */
  padding-top: 1px;
}

.detail-item .value {
  color: #333;
  font-size: 16px; /* 减小字体大小，降低资料项高度 */
  flex: 1;
}

/* 新增：退出登录按钮样式（和老师端完全一致，靠右对齐） */
.logout-btn-wrap {
  display: flex;
  justify-content: flex-end; /* 靠右对齐 */
  margin-top: 0;
}

.avatar-upload-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}

.avatar-uploader {
  border: 1px dashed #dcdfe6;
  border-radius: 50%;
  cursor: pointer;
  width: 160px;
  height: 160px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-uploader-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-uploader-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  color: #8c939d;
  font-size: 24px;
}

.upload-tips {
  font-size: 14px;
  color: #909399;
}

.loading-state {
  width: 100%;
  padding: 60px 0;
  text-align: center;
}

.skeleton-profile {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  width: 100%;
  max-width: 600px;
  padding: 24px;
  margin: 0 auto;
}

.skeleton-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: #f0f0f0;
  margin: 0 auto 24px;
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-row {
  height: 28px;
  background: #f0f0f0;
  border-radius: 4px;
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-row:nth-child(1) { width: 40%; }
.skeleton-row:nth-child(2) { width: 60%; }
.skeleton-row:nth-child(3) { width: 30%; }
.skeleton-row:nth-child(4) { width: 50%; }

.error-state {
  width: 100%;
  padding: 16px;
  box-sizing: border-box;
}

.vue-cropper {
  height: 400px;
  margin-bottom: 20px;
}

@keyframes skeleton-loading {
  0% { background-color: #f0f0f0; }
  50% { background-color: #e0e0e0; }
  100% { background-color: #f0f0f0; }
}
</style>