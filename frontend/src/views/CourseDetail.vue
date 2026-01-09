<template>
  <div class="pc-container">
    <NavigationBar :currentNav="currentNav" />

    <div class="content-wrapper">
      <div class="pc-main breadcrumb-wrapper">
        <div class="breadcrumb">
          <span @click="navigateTo('/home')" class="breadcrumb-link">首页</span>
          <span class="breadcrumb-separator">></span>
          <span @click="navigateTo('/course')" class="breadcrumb-link">课程中心</span>
          <span class="breadcrumb-separator">></span>
          <span class="breadcrumb-current">课程详情</span>
        </div>
      </div>

      <div class="pc-main content-main">
        <div v-if="isLoading" class="loading-state">
          <el-skeleton :rows="10" active></el-skeleton>
        </div>

        <div v-if="errorMessage" class="error-state">
          <el-alert type="error" :message="errorMessage" show-icon></el-alert>
        </div>

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
                <div v-if="isStudent">
                  <el-button
                    :type="isSubscribed ? 'primary' : 'success'"
                    class="enroll-button"
                    size="large"
                    :loading="buttonLoading || payLoading"
                    :disabled="buttonLoading || favoriteLoading || payLoading"
                    @click="handleEnrollClick"
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

      <div class="pc-main course-bottom-container">
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

    <Footer class="footer-fixed"/>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElSkeleton, ElAlert, ElMessage, ElMessageBox, ElButton, ElIcon } from 'element-plus';
import { Star, Document } from '@element-plus/icons-vue';
import NavigationBar from '../components/NavigationBar.vue';
import axiosInstance from "@/service/api.js";
import Footer from '../components/Footer.vue';
import { fixCoverPath } from '@/utils/format.js';

const route = useRoute();
const router = useRouter();

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

const payLoading = ref(false);
const orderId = ref('');
const baseUrl = ref(`${window.location.origin}/course/${route.params.id}`);
let paymentCheckInterval = null;

const toNumber = (value) => {
  const num = Number(value);
  return isNaN(num) ? null : num;
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return typeof dateStr === 'string' ? dateStr.split(' ')[0] :
      `${dateStr.getFullYear()}-${(dateStr.getMonth() + 1).toString().padStart(2, '0')}-${dateStr.getDate().toString().padStart(2, '0')}`;
};

const checkStudentRole = () => {
  const role = sessionStorage.getItem('role');
  isStudent.value = role === '0';
};

const getSubscriptionParams = () => {
  const courseId = route.params.id;
  const studentId = sessionStorage.getItem('id');
  if (!courseId || !studentId) return null;
  return {
    student_id: toNumber(studentId),
    course_id: toNumber(courseId)
  };
};

const getFavoriteParams = () => {
  const courseId = route.params.id;
  const studentId = sessionStorage.getItem('id');
  if (!courseId || !studentId) return null;
  return {
    student_id: toNumber(studentId),
    course_id: toNumber(courseId)
  };
};

const checkSubscription = async () => {
  const params = getSubscriptionParams();
  if (!params) {
    isSubscribed.value = false;
    return Promise.resolve(false);
  }

  try {
    buttonLoading.value = true;
    const response = await axiosInstance.get('/api/student/check-subscribe', { params });
    if (response.data.success) {
      isSubscribed.value = response.data.data.is_subscribed;
      return Promise.resolve(isSubscribed.value);
    } else {
      ElMessage.error(response.data.message || '检查订阅状态失败');
      isSubscribed.value = false;
      return Promise.resolve(false);
    }
  } catch (error) {
    if (error.name !== 'CanceledError') {
      console.error('检查订阅状态失败:', error);
      ElMessage.error('网络错误，请稍后再试');
    }
    isSubscribed.value = false;
    return Promise.resolve(false);
  } finally {
    buttonLoading.value = false;
  }
};

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
    if (error.name !== 'CanceledError') {
      console.error('检查收藏状态失败:', error);
      ElMessage.error('网络错误，请稍后再试');
    }
  } finally {
    favoriteLoading.value = false;
  }
};

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
      const response = await axiosInstance.delete('/api/student/cancel-favorite', { data: params });
      if (response.data.success) {
        ElMessage.success('取消收藏成功！');
        isFavorited.value = false;
      } else ElMessage.error(response.data.message || '取消收藏失败');
    } else {
      const response = await axiosInstance.post('/api/student/create-favorite', params);
      if (response.data.success) {
        ElMessage.success('收藏成功！');
        isFavorited.value = true;
      } else ElMessage.error(response.data.message || '收藏失败');
    }
  } catch (error) {
    if (error.name !== 'CanceledError') {
      console.error('收藏操作失败:', error);
      ElMessage.error('网络错误，请稍后再试');
    }
  } finally {
    favoriteLoading.value = false;
  }
};

const doSubscribeForFree = async (params) => {
  try {
    payLoading.value = true;
    const response = await axiosInstance.post('/api/student/create-subscribe', params);
    if (response.data.success) {
      ElMessage.success('订阅成功！');
      isSubscribed.value = true;
      navigateToCourseContent();
    } else {
      ElMessage.error(response.data.message || '订阅失败');
    }
  } catch (error) {
    console.error('订阅异常:', error);
    ElMessage.error('订阅失败，请稍后再试');
  } finally {
    payLoading.value = false;
  }
};

const doCreatePaymentOrder = async (params) => {
  const coursePrice = course.value.price || 0;
  try {
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
      const paymentWindow = window.open(payUrl, '_blank');
      if (!paymentWindow) {
        ElMessage.error('弹出窗口被阻止，请允许浏览器弹出窗口后重试');
        return;
      }
      startPaymentCheck(paymentWindow, Date.now());
    } else {
      ElMessage.error(response.data.message || '创建支付订单失败');
    }
  } catch (error) {
    console.error('创建支付订单异常:', error);
    ElMessage.error('创建支付订单失败，请稍后再试');
  } finally {
    payLoading.value = false;
  }
};

const handleEnrollClick = () => {
  const params = getSubscriptionParams();
  if (!params) {
    ElMessage.error('请先登录');
    router.push('/login');
    return;
  }

  if (isSubscribed.value) {
    navigateToCourseContent();
    return;
  }

  const coursePrice = course.value.price || 0;
  if (coursePrice <= 0) {
    ElMessageBox.confirm(
      '确定要订阅该免费课程吗？',
      '订阅确认',
      {
        confirmButtonText: '确认订阅',
        cancelButtonText: '取消',
        type: 'info'
      }
    ).then(() => {
      doSubscribeForFree(params);
    }).catch(() => {
      return;
    });
  } else {
    ElMessageBox.confirm(
      `确定要支付 ¥${coursePrice.toFixed(2)} 订阅《${course.value.name || '该课程'}》吗？`,
      '支付确认',
      {
        confirmButtonText: '确认支付',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      doCreatePaymentOrder(params);
    }).catch(() => {
      return;
    });
  }
};

const checkPaymentStatus = async () => {
  if (!orderId.value) return;
  try {
    const response = await axiosInstance.get(`/api/pay/query_sandbox_order/${orderId.value}`);
    
    if (response.data.success) {
      const alipayResult = response.data.alipay_result;
      if (alipayResult && alipayResult.trade_status === 'TRADE_SUCCESS') {
        ElMessage.success('支付成功！');
        isSubscribed.value = true;
        navigateToCourseContent();
      } else {
        ElMessage.warning('订单未支付成功，请完成支付后再试');
      }
    } else {
      ElMessage.error(response.data.message || '订单查询失败');
    }
  } catch (error) {
    if (error.response?.status === 404) {
      ElMessage.warning('订单不存在，可能已取消或过期');
      return;
    }
    if (error.name !== 'CanceledError') {
      console.error('检查支付状态失败:', error);
      ElMessage.error('网络错误或支付接口未就绪，请稍后再试');
    }
  } finally {
    orderId.value = '';
    if (paymentCheckInterval) {
      clearInterval(paymentCheckInterval);
      paymentCheckInterval = null;
    }
  }
};

const startPaymentCheck = (paymentWindow, startTime) => {
  if (paymentCheckInterval) {
    clearInterval(paymentCheckInterval);
  }
  const timeoutDuration = 3 * 60 * 1000;

  paymentCheckInterval = setInterval(async () => {
    if (Date.now() - startTime > timeoutDuration) {
      clearInterval(paymentCheckInterval);
      paymentCheckInterval = null;
      orderId.value = '';
      ElMessage.warning('支付超时，请重新创建订单支付');
      return;
    }

    if (paymentWindow && paymentWindow.closed) {
      clearInterval(paymentCheckInterval);
      paymentCheckInterval = null;
      await checkPaymentStatus();
      return;
    }
  }, 5000);
};

const navigateToCourseContent = () => {
  const courseId = route.params.id;
  if (!courseId) {
    console.error('课程ID不存在，无法跳转');
    ElMessage.error('课程ID不存在，无法跳转');
    return;
  }

  if (isStudent.value) {
    checkSubscription().then(() => {
      if (isSubscribed.value) {
        router.push(`/course/${courseId}/content`).catch(err => {
          if (err.message !== 'cancel') {
            console.error('课程内容跳转失败:', err);
            ElMessage.error('跳转课程内容失败，请手动返回课程中心重试');
          }
        });
      } else {
        ElMessage.warning('您尚未订阅该课程，无法进入');
        router.push(`/course/${courseId}`);
      }
    });
  } else {
    router.push(`/course/${courseId}/content`).catch(err => {
      if (err.message !== 'cancel') {
        console.error('课程内容跳转失败:', err);
        ElMessage.error('跳转课程内容失败，请手动返回课程中心重试');
      }
    });
  }
};

const navigateToCourseDetail = (courseId) => {
  if (courseId) router.push(`/course/${courseId}`);
  else {
    console.error('课程ID不存在，无法跳转');
    ElMessage.error('课程ID不存在，无法跳转');
  }
};

const navigateTo = (path) => {
  router.push(path);
};

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
      baseUrl.value = `${window.location.origin}/course/${courseId}`;
    } else errorMessage.value = response.data.message || '获取课程详情失败';
  } catch (error) {
    if (error.name !== 'CanceledError') {
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

const fetchRecommendCourses = async () => {
  try {
    const response = await axiosInstance.get('/api/course/recommend', { params: { limit: 4 } });
    if (response.data.success) recommendCourses.value = response.data.data.courses || [];
    else console.warn('获取推荐课程失败:', response.data.message);
  } catch (error) {
    console.warn('获取推荐课程网络错误:', error.message);
    recommendCourses.value = [];
  }
};

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
  if (paymentCheckInterval) {
    clearInterval(paymentCheckInterval);
    paymentCheckInterval = null;
  }
  orderId.value = '';
});
</script>

<style scoped>
.pc-container {
  width: 100%;
  height: 100vh;
  background-color: #f0f7f4;
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

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

.breadcrumb-wrapper {
  margin-top: 20px;
  margin-bottom: 12px;
}

.content-main {
  margin-bottom: 20px;
}

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

.loading-state {
  padding: 60px 0;
  text-align: center;
}

.error-state {
  padding: 30px 0;
}

.course-detail-wrapper {
  display: flex;
  flex-direction: column;
}

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

.course-bottom-container {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  align-items: stretch;
}

.chapter-section {
  flex: 1;
  background-color: #fff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e9e5;
}

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

.empty-state {
  padding: 60px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

.empty-tip {
  text-align: center;
  padding: 40px 0;
  color: #999;
  font-size: 16px;
}

.footer-fixed {
  width: 100%;
  margin-top: auto; 
}
</style>