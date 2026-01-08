<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="新建课程"
    width="60%"
    center
  >
    <el-form
      ref="courseFormRef"
      :model="courseForm"
      :rules="courseRules"
      label-width="100px"
    >
      <el-form-item label="课程名称" prop="name">
        <el-input
          v-model="courseForm.name"
          placeholder="请输入课程名称"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="课程封面">
        <div
          class="cover-upload-container"
          @click="triggerCoverUpload"
          role="button"
          tabindex="0"
        >
          <div v-if="previewUrl" class="cover-preview">
            <img :src="previewUrl" alt="课程封面预览" class="cover-image" />
          </div>
          <div v-else class="cover-placeholder">
            <el-icon size="24"><PictureFilled /></el-icon>
            <p>点击上传封面</p>
          </div>
          <input
            ref="coverFileInput"
            type="file"
            accept="image/png,image/jpg,image/jpeg"
            class="hidden-file-input"
            @change="handleCoverChange"
          />
        </div>
      </el-form-item>

      <el-form-item label="课程简介" prop="introduction">
        <el-input
          v-model="courseForm.introduction"
          type="textarea"
          :rows="4"
          placeholder="请输入课程简介"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="课程价格" prop="price">
        <el-input
          v-model="courseForm.price"
          type="number"
          :min="0"
          :step="0.01"
          placeholder="请输入课程价格（免费填0）"
          prefix="¥"
        />
      </el-form-item>

      <el-form-item label="适用年级" prop="gradeId">
        <el-select v-model="courseForm.gradeId" placeholder="请选择适用年级">
          <el-option
            v-for="grade in grades"
            :key="grade.id"
            :label="grade.name"
            :value="grade.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="所属学科" prop="subjectId">
        <el-select v-model="courseForm.subjectId" placeholder="请选择所属学科">
          <el-option
            v-for="subject in subjects"
            :key="subject.id"
            :label="subject.name"
            :value="subject.id"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleDialogClose">取消</el-button>
        <el-button type="primary" @click="submitCourseForm">确定</el-button>
      </span>
    </template>
  </el-dialog>

  <el-dialog
    v-model="cropDialogVisible"
    title="裁剪封面图"
    width="500px"
    top="5vh"
    :before-close="handleCropClose"
  >
    <div class="cropper-container">
      <vue-cropper
        ref="cropperRef"
        :img="cropImgUrl"
        :info="true"
        :auto-crop="true"
        :auto-crop-width="400"
        :auto-crop-height="225"
        :fixed-box="true"
        :fixed-number="[16, 9]"
        :can-move="true"
        :can-move-box="true"
        :original="false"
        :center-box="false"
        :high="true"
        :info-true="true"
        output-type="png"
      ></vue-cropper>
    </div>
    <template #footer>
      <el-button @click="handleCropClose">取消</el-button>
      <el-button type="primary" @click="confirmCrop">确认裁剪</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, nextTick, defineProps, defineEmits, onUnmounted, watch } from 'vue'; // 新增：导入watch
import { ElMessage, ElMessageBox, ElIcon } from 'element-plus';
import { PictureFilled } from '@element-plus/icons-vue';
import { VueCropper } from 'vue-cropper';
import axiosInstance from "@/service/api.js";

const props = defineProps({
  visible: { type: Boolean, default: false }
});
const emit = defineEmits(['close', 'create']);

const courseFormRef = ref(null);
const coverFileInput = ref(null);
const previewUrl = ref('');
const cropperRef = ref(null);
const cropDialogVisible = ref(false);
const cropImgUrl = ref('');
const croppedFile = ref(null);

const courseForm = reactive({
  name: '',
  introduction: '',
  price: 0.0,
  gradeId: '',
  subjectId: ''
});

const courseRules = {
  name: [
    { required: true, message: '请输入课程名称', trigger: 'blur' },
    { min: 2, max: 50, message: '课程名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  introduction: [
    { required: true, message: '请输入课程简介', trigger: 'blur' },
    { min: 10, max: 500, message: '课程简介长度在 10 到 500 个字符', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入课程价格', trigger: 'blur' },
    { type: 'number', min: 0, message: '价格不能为负数', trigger: 'blur' }
  ],
  gradeId: [{ required: true, message: '请选择适用年级', trigger: 'change' }],
  subjectId: [{ required: true, message: '请选择所属学科', trigger: 'change' }]
};

const grades = ref([
  { id: 1, name: '初一' }, { id: 2, name: '初二' }, { id: 3, name: '初三' },
  { id: 4, name: '高一' }, { id: 5, name: '高二' }, { id: 6, name: '高三' }
]);
const subjects = ref([
  { id: 1, name: '语文' }, { id: 2, name: '数学' }, { id: 3, name: '英语' },
  { id: 4, name: '物理' }, { id: 5, name: '化学' }, { id: 6, name: '生物' },
  { id: 7, name: '历史' }, { id: 8, name: '地理' }, { id: 9, name: '政治' }
]);

// 修复点1：重置封面状态时，先判断DOM是否存在
const resetCoverState = () => {
  // 安全释放URL，避免内存泄漏
  if (previewUrl.value) {
    try { URL.revokeObjectURL(previewUrl.value); } catch (e) {}
    previewUrl.value = '';
  }
  if (cropImgUrl.value) {
    try { URL.revokeObjectURL(cropImgUrl.value); } catch (e) {}
    cropImgUrl.value = '';
  }
  croppedFile.value = null;
  
  // 关键：先判断coverFileInput.value是否存在，再清空value
  if (coverFileInput.value) {
    coverFileInput.value.value = '';
  }
};

// 修复点2：替换原nextTick，改用watch监听visible变化（确保DOM挂载后再重置）
watch(() => props.visible, (newVal) => {
  if (newVal) {
    nextTick(() => { // 确保DOM已渲染
      courseFormRef.value?.resetFields();
      resetCoverState();
    });
  }
}, { immediate: true }); // 初始化时执行一次

const handleDialogClose = () => {
  emit('update:visible', false);
  emit('close');
};

const triggerCoverUpload = () => {
  // 修复点3：触发上传前判断DOM是否存在
  if (coverFileInput.value) {
    coverFileInput.value.click();
  }
};

const handleCoverChange = (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg'];
  const maxSize = 10 * 1024 * 1024;

  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('请上传 PNG、JPG 或 JPEG 格式的图片');
    // 修复点4：清空input前判断DOM
    if (coverFileInput.value) coverFileInput.value.value = '';
    return;
  }
  if (file.size > maxSize) {
    ElMessage.error('图片大小不能超过 10MB');
    // 修复点4：清空input前判断DOM
    if (coverFileInput.value) coverFileInput.value.value = '';
    return;
  }

  cropImgUrl.value = URL.createObjectURL(file);
  cropDialogVisible.value = true;
};

const handleCropClose = () => {
  if (cropImgUrl.value) {
    try { URL.revokeObjectURL(cropImgUrl.value); } catch (e) {}
    cropImgUrl.value = '';
  }
  cropDialogVisible.value = false;
  // 修复点5：清空input前判断DOM
  if (coverFileInput.value) coverFileInput.value.value = '';
};

const confirmCrop = () => {
  cropperRef.value.getCropBlob((blob) => {
    if (!blob) {
      ElMessage.error('裁剪失败，请重试！');
      return;
    }
    
    // 修复点6：先判断input是否存在，再获取文件名
    const originalFileName = coverFileInput.value?.files[0]?.name || `cover_${Date.now()}.png`;
    const fileExtension = originalFileName.slice(originalFileName.lastIndexOf('.')) || '.png';
    const newFileName = `cropped_${Date.now()}${fileExtension}`;
    croppedFile.value = new File([blob], newFileName, { type: blob.type });

    if (previewUrl.value) {
      try { URL.revokeObjectURL(previewUrl.value); } catch (e) {}
    }
    previewUrl.value = URL.createObjectURL(blob);

    ElMessage.success('封面裁剪成功！');
    handleCropClose();
  });
};

const submitCourseForm = async () => {
  try {
    await courseFormRef.value.validate();
  } catch (error) {
    ElMessage.error('请完善必填信息');
    return;
  }

  try {
    await ElMessageBox.confirm('确认创建课程？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'question'
    });
  } catch (error) {
    ElMessage.info('已取消创建');
    return;
  }

  const teacherId = sessionStorage.getItem('id');
  if (!teacherId) {
    ElMessage.error('无法获取教师信息，请重新登录！');
    return;
  }

  const formData = new FormData();
  formData.append('name', courseForm.name);
  formData.append('introduction', courseForm.introduction);
  formData.append('price', courseForm.price);
  formData.append('grade_id', courseForm.gradeId);
  formData.append('subject_id', courseForm.subjectId);
  formData.append('teacher_id', teacherId);

  if (croppedFile.value) {
    formData.append('cover', croppedFile.value);
  }

  try {
    const response = await axiosInstance.post('/api/course/create-course', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    if (response.data.success) {
      ElMessage.success('课程创建成功！');
      emit('create', response.data.data);
      handleDialogClose();
    } else {
      ElMessage.error(response.data.message || '创建失败');
    }
  } catch (error) {
    console.error('创建课程失败', error);
    ElMessage.error('创建课程失败：' + (error.response?.data?.message || '网络错误'));
  }
};

onUnmounted(() => {
  resetCoverState();
});
</script>

<style scoped>
.cover-upload-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  padding: 20px;
  transition: all 0.3s ease;
}
.cover-upload-container:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}
.cover-preview {
  position: relative;
  width: 120px;
  height: 120px;
  overflow: hidden;
  border-radius: 6px;
}
.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cover-placeholder {
  display: flex;
  width: 120px;
  height: 120px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
}
.cover-placeholder p {
  margin: 8px 0 0;
}
.hidden-file-input {
  display: none;
}
.cropper-container {
  height: 300px;
}
.el-button {
  background-color: #4caf50;
}
</style>