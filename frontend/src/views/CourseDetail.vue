<template>
  <!-- 全局容器：Flex垂直布局，占满视口高度 -->
  <div class="pc-container">
    <NavigationBar :currentNav="currentNav" />

    <!-- 内容区域：自动填充剩余空间，超出时垂直滚动 -->
    <div class="content-wrapper">
      <!-- 面包屑导航容器 -->
      <div class="pc-main breadcrumb-wrapper">
        <div class="breadcrumb">
          <span @click="navigateTo('/home')" class="breadcrumb-link">首页</span>
          <span class="breadcrumb-separator">></span>
          <span @click="navigateTo('/course')" class="breadcrumb-link">课程中心</span>
          <span class="breadcrumb-separator">></span>
          <span class="breadcrumb-current">课程详情</span>
        </div>
      </div>

      <!-- 课程主体内容容器 -->
      <div class="pc-main content-main">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-state">
          <el-skeleton :rows="10" active></el-skeleton>
        </div>

        <!-- 错误状态 -->
        <div v-if="errorMessage" class="error-state">
          <el-alert type="error" :message="errorMessage" show-icon></el-alert>
        </div>

        <!-- 课程详情内容 -->
        <div v-else-if="course && !errorMessage" class="course-detail-wrapper">
          <div class="course-header">
            <div class="course-cover-box">
              <img
                :src="fixCoverPath(course.cover) || defaultCover"
                alt="课程主图"
                class="course-cover"
              >
            </div>
            <div class="course-info-right">
              <h1 class="course-title">{{ course.name || '暂无课程名称' }}</h1>
              <div class="subject-grade">
                <span>科目: {{ course.subject_name || '暂无科目' }}</span>
                <span>年级: {{ course.grade_name || '暂无年级' }}</span>
              </div>
              <p class="course-subtitle">课程介绍:{{ course.introduction || '暂无课程介绍' }}</p>
              <div class="teacher-info">
                <p>主讲老师: {{ course.teacher?.username || '暂无讲师信息' }}</p>
                <p>讲师学校: {{ course.teacher?.university || '暂无学校信息' }}</p>
                <p>讲师介绍: {{ course.teacher?.introduction || '暂无讲师介绍' }}</p>
              </div>

              <div class="price-enroll">
                <span class="price-tag">¥{{ course.price || 0 }}</span>
                <!-- 学生用户显示报名/收藏按钮 -->
                <div v-if="isStudent">
                  <el-button
                    :type="isSubscribed ? 'primary' : 'success'"
                    class="enroll-button"
                    size="large"
                    :loading="buttonLoading || payLoading"
                    :disabled="buttonLoading || favoriteLoading || payLoading"
                    @click="handleButtonClick"
                  >
                    {{ buttonLoading ? '处理中...' : payLoading ? '支付中...' : (isSubscribed ? '进入课堂' : '立即报名') }}
                  </el-button>
                  <el-button
                    :type="isFavorited ? 'warning' : ''"
                    class="favorite-button"
                    :plain="!isFavorited"
                    :circle="true"
                    :icon="Star"
                    @click="toggleFavorite"
                    :loading="favoriteLoading"
                    :disabled="buttonLoading || payLoading"
                    :class="{ 'active': isFavorited }"
                  >
                  </el-button>
                </div>
                <!-- 非学生用户仅显示进入课堂按钮 -->
                <div v-else>
                  <el-button
                    type="primary"
                    class="enroll-button"
                    size="large"
                    :loading="buttonLoading"
                    :disabled="buttonLoading"
                    @click="navigateToCourseContent"
                  >
                    {{ buttonLoading ? '处理中...' : '进入课堂' }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 章节+推荐课程区域 -->
      <div class="pc-main course-bottom-container">
        <!-- 章节区域 -->
        <div class="chapter-section pc-content">
          <h2 class="section-title">课程章节</h2>
          <div v-if="course.chapters && course.chapters.length > 0" class="chapter-list">
            <div
              v-for="(chapter, index) in course.chapters"
              :key="index"
              class="chapter-item"
            >
              <span class="chapter-number">第{{ index + 1 }}章</span>
              <span class="chapter-title-text">{{ chapter.title || '暂无章节标题' }}</span>
            </div>
          </div>
          <div v-else class="empty-tip">
            该课程暂无章节内容
          </div>
        </div>

        <!-- 推荐课程区域：粘性定位 -->
        <div class="recommend-section pc-sidebar">
          <h2 class="section-title">推荐课程</h2>
          <div v-if="recommendCourses && recommendCourses.length > 0" class="recommend-list">
            <div
              v-for="(recCourse, idx) in recommendCourses.slice(0, 4)"
              :key="recCourse.id"
              class="recommend-item card-frame"
              @click="navigateToCourseDetail(recCourse.id)"
            >
              <h3 class="rec-course-name">{{ recCourse.name || '暂无课程名称' }}</h3>
              <div class="info-columns">
                <div class="info-column">
                  <div class="info-item"><i class="el-icon-user"></i> 讲师：{{ recCourse.teacher_name || '暂无' }}</div>
                  <div class="info-item"><i class="el-icon-s-data"></i> 年级：{{ recCourse.grade_name || '暂无' }}</div>
                </div>
                <div class="info-column">
                  <div class="info-item"><i class="el-icon-folder-opened"></i> 科目：{{ recCourse.subject_name || '暂无' }}</div>
                  <div class="info-item"><i class="el-icon-user-solid"></i> 学习人数：{{ recCourse.subscriber_count || 0 }}</div>
                </div>
              </div>
              <div class="course-meta">
                <div class="course-price" :class="recCourse.price === 0 ? 'free' : 'paid'">
                  {{ recCourse.price === 0 ? '免费' : `¥${recCourse.price.toFixed(2)}` }}
                </div>
                <div class="course-time">{{ formatDate(recCourse.created_at) }}</div>
              </div>
            </div>
          </div>
          <div class="empty-state" v-else>
            <el-icon size="48"><Document /></el-icon>
            <p>暂无推荐课程</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 支付结果弹窗：脱离文档流，不影响滚动 -->
    <el-dialog
      v-model="paymentDialogVisible"
      title="支付结果"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <template #content>
        <div class="payment-result">
          <div class="result-icon" :class="paymentSuccess ? 'success' : paymentCancelled ? 'info' : 'error'">
            <i :class="paymentSuccess ? 'el-icon-circle-check' : paymentCancelled ? 'el-icon-info' : 'el-icon-circle-close'"></i>
          </div>
          <p class="result-message">
            {{ paymentSuccess ? '订阅成功！' : paymentCancelled ? '已取消支付' : '订阅失败' }}
          </p>
          <p class="result-detail">{{ paymentMessage }}</p>
        </div>
      </template>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closePaymentDialog">关闭</el-button>
          <el-button v-if="paymentSuccess" type="primary" @click="navigateToCourseContent">
            进入课程
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 页脚：固定到底部 -->
    <Footer class="footer-fixed"/>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElSkeleton, ElAlert, ElMessage, ElMessageBox, ElDialog, ElButton, ElIcon } from 'element-plus';
import { Star, Document } from '@element-plus/icons-vue';
import NavigationBar from '../components/NavigationBar.vue';
import axiosInstance from "@/service/api.js";
import Footer from '../components/Footer.vue';
import { fixCoverPath } from '@/utils/format.js';

const route = useRoute();
const router = useRouter();

// 基础变量
const currentNav = ref('courseDetail');
const defaultCover = 'https://picsum.photos/400/250?random=100';
const course = ref({});
const isLoading = ref(true);
const errorMessage = ref('');
const courseRequestController = ref(null);
const buttonLoading = ref(false);
const isSubscribed = ref(false);
const isFavorited = ref(false);
const favoriteLoading = ref(false);
const isStudent = ref(false);
const recommendCourses = ref([]);

// 支付相关状态
const payLoading = ref(false);
const orderId = ref('');
const baseUrl = ref(`http://localhost:5173/course/${route.params.id}/content`);
const paymentDialogVisible = ref(false);
const paymentSuccess = ref(false);
const paymentMessage = ref('');
const paymentCancelled = ref(false);
let paymentCheckInterval = null;

// 工具函数：安全转换为数字
const toNumber = (value) => {
  const num = Number(value);
  return isNaN(num) ? null : num;
};

// 日期格式化：仅保留年月日
const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return typeof dateStr === 'string' ? dateStr.split(' ')[0] :
      `${dateStr.getFullYear()}-${(dateStr.getMonth() + 1).toString().padStart(2, '0')}-${dateStr.getDate().toString().padStart(2, '0')}`;
};

// 校验用户是否为学生身份（role=0）
const checkStudentRole = () => {
  const role = sessionStorage.getItem('role');
  isStudent.value = role === '0';
};

// 封装订阅参数（仅学生）
const getSubscriptionParams = () => {
  const courseId = route.params.id;
  const studentId = sessionStorage.getItem('id');
  if (!courseId || !studentId) return null;
  return {
    student_id: toNumber(studentId),
    course_id: toNumber(courseId)
  };
};

// 封装收藏参数（仅学生）
const getFavoriteParams = () => {
  const courseId = route.params.id;
  const studentId = sessionStorage.getItem('id');
  if (!courseId || !studentId) return null;
  return {
    student_id: toNumber(studentId),
    course_id: toNumber(courseId)
  };
};

// 检查课程订阅状态
const checkSubscription = async () => {
  const params = getSubscriptionParams();
  if (!params) {
    isSubscribed.value = false;
    return;
  }

  try {
    buttonLoading.value = true;
    const response = await axiosInstance.get('/api/student/check-subscribe', { params });
    if (response.data.success) isSubscribed.value = response.data.data.is_subscribed;
    else ElMessage.error(response.data.message || '检查订阅状态失败');
  } catch (error) {
    console.error('检查订阅状态失败:', error);
    ElMessage.error('网络错误，请稍后再试');
  } finally {
    buttonLoading.value = false;
  }
};

// 检查课程收藏状态
const checkFavorite = async () => {
  const params = getFavoriteParams();
  if (!params) {
    isFavorited.value = false;
    return;
  }

  try {
    favoriteLoading.value = true;
    const response = await axiosInstance.get('/api/student/check-favorite', { params });
    if (response.data.success) isFavorited.value = response.data.data.is_favorited;
    else ElMessage.error(response.data.message || '检查收藏状态失败');
  } catch (error) {
    console.error('检查收藏状态失败:', error);
    ElMessage.error('网络错误，请稍后再试');
  } finally {
    favoriteLoading.value = false;
  }
};

// 切换课程收藏状态
const toggleFavorite = async () => {
  if (!isStudent.value) {
    ElMessage.error('只有学生可以收藏课程');
    return;
  }

  const params = getFavoriteParams();
  if (!params) {
    ElMessage.error('请先登录');
    router.push('/login');
    return;
  }

  favoriteLoading.value = true;

  try {
    if (isFavorited.value) {
      // 取消收藏
      const response = await axiosInstance.delete('/api/student/cancel-favorite', { data: params });
      if (response.data.success) {
        ElMessage.success('取消收藏成功！');
        isFavorited.value = false;
      } else ElMessage.error(response.data.message || '取消收藏失败');
    } else {
      // 收藏课程
      const response = await axiosInstance.post('/api/student/create-favorite', params);
      if (response.data.success) {
        ElMessage.success('收藏成功！');
        isFavorited.value = true;
      } else ElMessage.error(response.data.message || '收藏失败');
    }
  } catch (error) {
    console.error('收藏操作失败:', error);
    ElMessage.error('网络错误，请稍后再试');
  } finally {
    favoriteLoading.value = false;
  }
};

// 报名/支付按钮点击逻辑
const handleButtonClick = async () => {
  if (!isStudent.value) {
    navigateToCourseContent();
    return;
  }

  const params = getSubscriptionParams();
  if (!params) {
    ElMessage.error('请先登录');
    router.push('/login');
    return;
  }

  buttonLoading.value = true;

  try {
    if (isSubscribed.value) {
      navigateToCourseContent();
    } else {
      const coursePrice = course.value.price || 0;
      coursePrice <= 0 ? await subscribeForFree(params) : await createPaymentOrder(params);
    }
  } catch (error) {
    console.error('操作失败:', error);
  } finally {
    buttonLoading.value = false;
    nextTick(() => {
      if (isStudent.value) {
        checkSubscription();
        checkFavorite();
      }
    });
  }
};

// 免费课程订阅
const subscribeForFree = async (params) => {
  try {
    await ElMessageBox.confirm('确定要订阅该免费课程吗？', '订阅确认', { confirmButtonText: '确认订阅', cancelButtonText: '取消' });
    payLoading.value = true;
    const response = await axiosInstance.post('/api/student/create-subscribe', params);
    if (response.data.success) {
      showPaymentResult(true, false, '订阅成功！');
      isSubscribed.value = true;
    } else showPaymentResult(false, false, response.data.message || '订阅失败');
  } catch (error) {
    console.error('订阅失败', error);
    if (error.message === 'cancel') {
      ElMessage.info('已取消订阅');
      showPaymentResult(false, true, '已取消支付操作');
    } else showPaymentResult(false, false, error.message || '订阅失败');
    throw error;
  } finally {
    payLoading.value = false;
  }
};

// 创建付费课程支付订单
const createPaymentOrder = async (params) => {
  try {
    const coursePrice = course.value.price || 0;
    await ElMessageBox.confirm(
      `确定要支付 ¥${coursePrice.toFixed(2)} 订阅《${course.value.name || '该课程'}》吗？`,
      '支付确认',
      { type: 'warning', confirmButtonText: '确认支付', cancelButtonText: '取消' }
    );

    payLoading.value = true;
    const formData = new FormData();
    formData.append('amount', coursePrice);
    formData.append('subject', course.value.name || '课程订阅');
    formData.append('student_id', toNumber(params.student_id));
    formData.append('course_id', toNumber(params.course_id));
    formData.append('base_url', baseUrl.value);

    const response = await axiosInstance.post('/api/pay/create_sandbox_order', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    if (response.data.success) {
      orderId.value = response.data.order_id;
      const payUrl = response.data.pay_url;
      const paymentStartTime = Date.now();
      const paymentWindow = window.open(payUrl, '_blank');
      if (!paymentWindow) throw new Error('弹出窗口被阻止，请允许浏览器弹出窗口');
      startPaymentCheck(paymentWindow, paymentStartTime);
    } else showPaymentResult(false, false, response.data.message || '创建支付订单失败');
  } catch (error) {
    console.error('创建支付订单失败', error);
    if (error.message === 'cancel') {
      ElMessage.info('已取消支付操作');
      showPaymentResult(false, true, '已取消支付操作');
    } else showPaymentResult(false, false, error.message || '创建支付订单失败');
    throw error;
  } finally {
    payLoading.value = false;
  }
};

// 检查支付状态（定时轮询）
const startPaymentCheck = (paymentWindow, startTime) => {
  if (paymentCheckInterval) clearInterval(paymentCheckInterval);
  const timeoutDuration = 3 * 60 * 1000;

  paymentCheckInterval = setInterval(async () => {
    if (Date.now() - startTime > timeoutDuration) {
      clearInterval(paymentCheckInterval);
      showPaymentResult(false, false, '支付超时，请重试');
      return;
    }

    if (paymentWindow && paymentWindow.closed) {
      clearInterval(paymentCheckInterval);
      checkPaymentStatus();
      return;
    }

    try {
      if (orderId.value) {
        showPaymentResult(true, false, '支付成功！');
        return;
      }
    } catch (error) {
      console.error('检查支付状态失败', error);
    }
  }, 3000);
};

// 校验最终支付状态
const checkPaymentStatus = async () => {
  if (!orderId.value) return;
  try {
    showPaymentResult(true, false, '支付成功！');
  } catch (error) {
    console.error('检查支付状态失败', error);
    showPaymentResult(false, false, '网络错误，请稍后再试');
  }
};

// 显示支付结果弹窗
const showPaymentResult = (success, cancelled, message) => {
  paymentSuccess.value = success;
  paymentCancelled.value = cancelled;
  paymentMessage.value = message;
  paymentDialogVisible.value = true;
};

// 关闭支付结果弹窗
const closePaymentDialog = () => {
  paymentDialogVisible.value = false;
};

// 跳转到课程内容页
const navigateToCourseContent = () => {
  if (route.params.id) router.push(`/course/${route.params.id}/content`);
  else {
    console.error('课程ID不存在，无法跳转');
    ElMessage.error('课程ID不存在，无法跳转');
  }
};

// 跳转到推荐课程详情页
const navigateToCourseDetail = (courseId) => {
  if (courseId) router.push(`/course/${courseId}`);
  else {
    console.error('课程ID不存在，无法跳转');
    ElMessage.error('课程ID不存在，无法跳转');
  }
};

// 通用导航方法
const navigateTo = (path) => {
  router.push(path);
};

// 获取课程详情数据
const fetchCourseData = async (courseId) => {
  isLoading.value = true;
  errorMessage.value = '';
  if (courseRequestController.value) courseRequestController.value.abort();
  courseRequestController.value = new AbortController();

  try {
    const response = await axiosInstance.get('/api/course/get-course-detail', {
      params: { course_id: toNumber(courseId) },
      signal: courseRequestController.value.signal
    });
    if (response.data.success) {
      course.value = response.data.data;
      fetchRecommendCourses();
    } else errorMessage.value = response.data.message || '获取课程详情失败';
  } catch (error) {
    if (error.name !== 'AbortError') {
      errorMessage.value = '网络错误，请重试';
      console.error('获取课程详情失败:', error);
    }
  } finally {
    isLoading.value = false;
    nextTick(() => {
      checkStudentRole();
      if (isStudent.value) {
        checkSubscription();
        checkFavorite();
      }
    });
  }
};

// 获取推荐课程数据
const fetchRecommendCourses = async () => {
  try {
    const response = await axiosInstance.get('/api/course/recommend', { params: { limit: 4 } });
    if (response.data.success) recommendCourses.value = response.data.data.courses || [];
    else console.warn('获取推荐课程失败:', response.data.message);
  } catch (error) {
    console.error('获取推荐课程网络错误:', error);
  }
};

// 组件生命周期
onMounted(() => {
  if (route.params.id) fetchCourseData(route.params.id);
});

watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      fetchCourseData(newId);
      window.scrollTo(0, 0);
    }
  }
);

watch(
  () => sessionStorage.getItem('role'),
  (newRole) => {
    checkStudentRole();
    if (newRole === '0') {
      checkSubscription();
      checkFavorite();
    } else {
      isSubscribed.value = false;
      isFavorited.value = false;
    }
  },
  { immediate: true }
);

onUnmounted(() => {
  if (courseRequestController.value) courseRequestController.value.abort();
  if (paymentCheckInterval) clearInterval(paymentCheckInterval);
});
</script>

<style scoped>
/* 全局布局：Flex垂直布局 */
.pc-container {
  width: 100%;
  height: 100vh;
  background-color: #f0f7f4;
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 内容容器：自动填充，垂直滚动 */
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
.breadcrumb-wrapper {
  margin-top: 20px;
  margin-bottom: 12px;
}

/* 课程主体容器 */
.content-main {
  margin-bottom: 20px;
}

/* 面包屑样式 */
.breadcrumb {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
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

/* 加载/错误状态 */
.loading-state {
  padding: 60px 0;
  text-align: center;
}
.error-state {
  padding: 30px 0;
}

/* 课程详情主容器 */
.course-detail-wrapper {
  display: flex;
  flex-direction: column;
}

/* 课程头部布局 */
.course-header {
  display: flex;
  min-height: 450px; 
  flex-wrap: wrap;
  gap: 60px;
  margin-bottom: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e9e5;
  padding: 40px 50px;
  align-items: flex-start;
}

.course-cover-box {
  width: 560px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0; 
}

.course-cover {
  width: 100%;
  height: 360px;
  border-radius: 8px;
  border: 2px solid #e0e9e5;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  object-fit: cover;
  transition: transform 0.3s ease;
}

.course-cover:hover {
  transform: scale(1.02);
}

/* 右侧课程信息 */
.course-info-right {
  flex: 1;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0 20px;
}

.course-title {
  font-size: 28px;
  color: #2b6a3d;
  font-weight: 700;
  margin: 0 0 16px 0;
  line-height: 1.3;
  text-align: left;
}

.course-subtitle {
  font-size: 20px;
  color: #222;
  margin: 0 0 12px 0;
  line-height: 1.6;
  text-align: left;
}

.teacher-info {
  margin-bottom: 20px;
  line-height: 1.6;
  color: #222;
  text-align: left;
}

.subject-grade {
  display: flex;
  gap: 20px;
  color: #222;
  margin-bottom: 20px;
  font-size: 20px;
}

/* 价格与按钮区域 */
.price-enroll {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: auto;
}

.price-tag {
  font-size: 28px;
  color: #ff5421;
  font-weight: bold;
  line-height: 50px;
}

.enroll-button {
  margin-left: 10px;
  padding: 10px 30px;
  font-size: 18px;
  line-height: 50px;
  background-color: #2b6a3d;
  min-width: 140px;
}

.favorite-button {
  width: 40px;
  height: 40px;
  padding: 0;
  background-color: #f5f7fa;
  transition: all 0.3s ease;
  border: 2px solid #666;
}

.favorite-button:hover {
  border: 2px solid #ff9821;
  transform: scale(1.1);
  box-shadow: 0 0 15px rgba(255, 165, 0, 0.3);
}

.favorite-button.active {
  border: 2px solid #ff9821;
}

:deep(.el-icon) {
  font-size: 24px;
  color: #666;
  transition: color 0.3s ease;
}

:deep(.favorite-button.active .el-icon) {
  color: #ff9821;
  transform: scale(1.1);
  text-shadow: 0 0 10px rgba(255, 87, 34, 0.7);
}

/* 章节+推荐课程布局 */
.course-bottom-container {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  align-items: stretch;
}

/* 章节区域 */
.chapter-section {
  flex: 1;
  background-color: #fff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e9e5;
}

/* 推荐课程：粘性定位 */
.recommend-section {
  width: 380px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  box-sizing: border-box;
  position: sticky;
  top: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  align-self: flex-start;
}

.section-title {
  font-size: 18px;
  color: #2b6a3d;
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #e5e5e5;
  font-weight: 600;
}

/* 章节列表 */
.chapter-list {
  list-style: none;
  padding: 0;
}

.chapter-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.chapter-number {
  color: #2b6a3d;
  margin-left: 20px;
  font-size: 18px;
  font-weight: bold;
  min-width: 40px;
  text-align: center;
}

.chapter-title-text{
  margin-left: 20px;
  font-size: 18px;
}

/* 推荐课程列表 */
.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommend-item {
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
}

/* 卡片样式 */
.card-frame {
  border: 1px solid #e0e9e5;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-frame:hover {
  border-color: #20c997;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

/* 推荐课程名称 */
.rec-course-name {
  font-size: 17px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 信息列布局 */
.info-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 15px;
}

.info-column {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item {
  font-size: 14px;
  color: #6b7280;
  display: flex;
  align-items: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-item i {
  margin-right: 6px;
  color: #9ca3af;
  font-size: 14px;
}

/* 课程元数据（价格/时间） */
.course-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid #e5e7eb;
}

.course-price {
  font-size: 16px;
  font-weight: 600;
}

.course-price.free {
  color: #2b6a3d;
}

.course-price.paid {
  color: #ef4444;
}

.course-time {
  font-size: 13px;
  color: #6b7280;
}

/* 空状态 */
.empty-state {
  padding: 60px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

/* 支付结果弹窗 */
:deep(.payment-result) {
  text-align: center;
  padding: 20px 0;
}

:deep(.result-icon) {
  font-size: 48px;
  margin-bottom: 16px;
}

:deep(.result-icon.success) {
  color: #198754;
}

:deep(.result-icon.error) {
  color: #dc3545;
}

:deep(.result-message) {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

:deep(.dialog-footer) {
  display: flex;
  justify-content: center;
  gap: 10px;
}

/* 空提示 */
.empty-tip {
  text-align: center;
  padding: 40px 0;
  color: #999;
  font-size: 16px;
}

/* 页脚固定 */
.footer-fixed {
  width: 100%;
  margin-top: auto; 
}
</style>