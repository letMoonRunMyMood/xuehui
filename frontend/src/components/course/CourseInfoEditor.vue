<template>
  <!-- ... template 部分保持不变 ... -->
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="修改课程信息"
    width="700px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="courseInfoFormRef"
      :model="courseForm"
      label-width="100px"
      :rules="formRules"
      class="course-info-form"
    >
      <!-- 课程名称 -->
      <el-form-item label="课程名称" prop="name">
        <el-input
          v-model="courseForm.name"
          placeholder="请输入课程名称"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>

      <!-- 课程简介 -->
      <el-form-item label="课程简介" prop="introduction">
        <el-input
          v-model="courseForm.introduction"
          type="textarea"
          placeholder="请输入课程简介"
          rows="4"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <!-- 课程价格 -->
      <el-form-item label="课程价格" prop="price">
        <el-input
          v-model="courseForm.price"
          placeholder="请输入课程价格（免费填0）"
          type="number"
          min="0"
          step="0.01"
          prefix="¥"
        />
      </el-form-item>

      <!-- 所属科目 -->
      <el-form-item label="所属科目" prop="subject_id">
        <el-select
          v-model="courseForm.subject_id"
          placeholder="请选择科目"
          style="width: 100%"
        >
          <el-option
            v-for="subject in subjectList"
            :key="subject.id"
            :label="subject.name"
            :value="subject.id"
          />
        </el-select>
      </el-form-item>

      <!-- 适用年级 -->
      <el-form-item label="适用年级" prop="grade_id">
        <el-select
          v-model="courseForm.grade_id"
          placeholder="请选择年级"
          style="width: 100%"
        >
          <el-option
            v-for="grade in gradeList"
            :key="grade.id"
            :label="grade.name"
            :value="grade.id"
          />
        </el-select>
      </el-form-item>

      <!-- 课程封面 -->
      <el-form-item label="课程封面">
        <div class="cover-upload-wrapper">
          <div class="upload-container">
            <el-upload
              class="cover-uploader"
              drag
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleCoverChange"
              accept="image/png,image/jpg,image/jpeg"
            >
              <template #default v-if="newCoverFile">
                <div class="image-preview-wrapper">
                  <img :src="newCoverUrl" alt="封面预览" class="preview-image" />
                  <el-button
                    type="link"
                    class="remove-btn"
                    icon="CircleClose"
                    @click.stop="removeNewCover"
                  >
                  </el-button>
                </div>
                <div class="el-upload__text">点击或拖拽以更换图片</div>
              </template>
              <template #default v-else>
                <div v-if="courseForm.cover" class="image-preview-wrapper">
                  <img :src="fixCoverPath(courseForm.cover)" alt="当前封面" class="preview-image" />
                </div>
                <div v-else>
                  <i class="el-icon-upload" />
                  <div class="el-upload__text">
                    拖拽文件到此处上传<br />
                    <em>或点击上传</em>
                  </div>
                </div>
              </template>
            </el-upload>
          </div>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button
        type="primary"
        @click="submitCourseInfo"
        :loading="submitLoading"
      >
        保存修改
      </el-button>
    </template>
  </el-dialog>

  <!-- 图片裁剪弹窗 -->
  <el-dialog
    v-model="cropDialogVisible"
    title="裁剪封面图"
    width="800px"  
    top="10vh"     
    center       
    :before-close="handleCropClose"
  >
    <div class="cropper-container">
      <vue-cropper
        ref="cropperRef"
        :img="cropImgUrl"
        :info="true"
        :auto-crop="true"
        :auto-crop-width="640" 
        :auto-crop-height="360" 
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
import { ref, reactive, watch, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VueCropper } from 'vue-cropper';
import axiosInstance from '@/service/api.js'
import { fixCoverPath } from '@/utils/format.js'

const props = defineProps({
  visible: { type: Boolean, default: false },
  course: { type: Object, required: true, default: () => ({}) }
})

const emit = defineEmits(['close', 'update-success', 'update:visible'])

const submitLoading = ref(false)
const courseInfoFormRef = ref(null)
const newCoverFile = ref(null)
const newCoverUrl = ref('')
const cropperRef = ref(null);
const cropDialogVisible = ref(false);
const cropImgUrl = ref('');

const subjectList = ref([
  { id: 1, name: '语文' }, { id: 2, name: '数学' }, { id: 3, name: '英语' },
  { id: 4, name: '物理' }, { id: 5, name: '化学' }, { id: 6, name: '生物' },
  { id: 7, name: '历史' }, { id: 8, name: '地理' }, { id: 9, name: '政治' }
])
const gradeList = ref([
  { id: 1, name: '初一' }, { id: 2, name: '初二' }, { id: 3, name: '初三' },
  { id: 4, name: '高一' }, { id: 5, name: '高二' }, { id: 6, name: '高三' }
])

const courseForm = reactive({
  course_id: '',
  name: '',
  introduction: '',
  price: 0,
  subject_id: undefined,
  grade_id: undefined,
  cover: ''
})

const formRules = {
  name: [
    { required: true, message: '请输入课程名称', trigger: 'blur' },
    { min: 2, max: 50, message: '课程名称长度在2-50字符之间', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入课程价格', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value === undefined || value === null || value === '') {
          callback(new Error('请输入课程价格'));
        } else if (typeof value === 'string' && !/^\d+(\.\d{1,2})?$/.test(value)) {
          callback(new Error('请输入有效的数字，最多两位小数'));
        } else if (Number(value) < 0) {
          callback(new Error('价格不能为负数'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ],
  subject_id: [{ required: true, message: '请选择所属科目', trigger: 'change' }],
  grade_id: [{ required: true, message: '请选择适用年级', trigger: 'change' }]
}

watch(() => props.course, (newCourse) => {
  if (newCourse && newCourse.id) {
    resetForm();
    courseForm.course_id = newCourse.id
    courseForm.name = newCourse.name || ''
    courseForm.introduction = newCourse.introduction || ''
    courseForm.price = newCourse.price || 0
    courseForm.subject_id = newCourse.subject_id || undefined
    courseForm.grade_id = newCourse.grade_id || undefined
    courseForm.cover = newCourse.cover || ''
  }
}, { immediate: true, deep: true })

const handleCoverChange = (file) => {
  const maxSize = 5 * 1024 * 1024;
  if (file.size > maxSize) {
    ElMessage.error('封面图片大小不能超过5MB');
    return;
  }
  const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg'];
  if (!allowedTypes.includes(file.raw.type)) {
    ElMessage.error('仅支持PNG/JPG/JPEG格式的图片');
    return;
  }
  
  cropImgUrl.value = URL.createObjectURL(file.raw);
  cropDialogVisible.value = true;
};

const cleanupNewCover = () => {
  if (newCoverUrl.value) {
    URL.revokeObjectURL(newCoverUrl.value);
  }
  newCoverFile.value = null;
  newCoverUrl.value = '';
};

const removeNewCover = () => {
  cleanupNewCover(); // 调用清理函数
  ElMessage.info('已取消新封面的选择'); 
};

const handleCropClose = () => {
  if (cropImgUrl.value) URL.revokeObjectURL(cropImgUrl.value);
  cropImgUrl.value = '';
  cropDialogVisible.value = false;
};

const confirmCrop = () => {
  cropperRef.value.getCropBlob((blob) => {
    if (!blob) {
      ElMessage.error('裁剪失败，请重试！');
      return;
    }
    cleanupNewCover(); 
    
    newCoverFile.value = blob;
    newCoverUrl.value = URL.createObjectURL(blob);

    ElMessage.success('封面裁剪成功！');
    handleCropClose();
  });
};

const resetForm = () => {
  if (courseInfoFormRef.value) {
    courseInfoFormRef.value.resetFields();
  }
  cleanupNewCover(); 
}

const handleClose = () => {
  resetForm();
  emit('update:visible', false);
  emit('close');
}

const submitCourseInfo = async () => {
  try {
    await courseInfoFormRef.value.validate()
  } catch (error) {
    ElMessage.error('请完善必填信息')
    return
  }

  try {
    await ElMessageBox.confirm('确定要修改该课程信息吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch (error) {
    ElMessage.info('已取消修改')
    return
  }

  submitLoading.value = true
  try {
    const formData = new FormData()
    formData.append('course_id', courseForm.course_id)
    formData.append('name', courseForm.name)
    formData.append('introduction', courseForm.introduction)
    formData.append('price', courseForm.price)
    formData.append('subject_id', courseForm.subject_id)
    formData.append('grade_id', courseForm.grade_id)
    
    if (newCoverFile.value) {
      const fileName = `cover_${Date.now()}.png`;
      formData.append('cover', newCoverFile.value, fileName);
    }

    const response = await axiosInstance.patch('/api/course/update-course', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (response.data.success) {
      emit('update-success', response.data.data)
      handleClose()
    } else {
      ElMessage.error(response.data.message || '修改失败')
    }
  } catch (error) {
    console.error('修改课程信息失败:', error)
    ElMessage.error('修改失败：' + (error.response?.data?.message || '网络错误'))
  } finally {
    submitLoading.value = false
  }
}

onUnmounted(() => {
  cleanupNewCover(); 
  if (cropImgUrl.value) URL.revokeObjectURL(cropImgUrl.value);
});
</script>

<style scoped>
.course-info-form {
  padding: 10px 0;
}
.cover-upload-wrapper {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  flex-wrap: wrap;
}
.upload-container {
  flex: 1;
  min-width: 300px;
}
.cover-uploader {
  width: 100%;
}
.image-preview-wrapper {
  position: relative;
  width: 100%;
  height: 180px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.remove-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 24px;
  height: 24px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}
.image-preview-wrapper:hover .remove-btn {
  opacity: 1;
}
.cropper-container {
  height: 450px;  
}
</style>