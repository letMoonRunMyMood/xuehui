<template>
  <div class="pc-container">
    <!-- 顶部导航栏组件 -->
    <NavigationBar :currentNav="currentNav" />

    <!-- 主体内容（包裹所有中间内容） -->
    <div class="content-wrapper">
      <div class="pc-main">
        <!-- 侧边栏：年级和科目筛选 -->
        <div class="pc-sidebar">
          <div class="sidebar-section">
            <h3>选择年级</h3>
            <div class="option-grid">
              <el-button
                  v-for="grade in grades"
                  :key="grade"
                  @click="navigateToCourseCenter(grade, selectedSubject.value)"
                  class="option-btn"
                  :style="{ width: '100px', height: '36px' }"
                  :class="{ 'option-btn-active': selectedGrade === grade }"
              >
                {{ grade }}
              </el-button>
            </div>
          </div>
          <div class="sidebar-section">
            <h3>选择科目</h3>
            <div class="option-grid">
              <el-button
                  v-for="subject in subjects"
                  :key="subject"
                  @click="navigateToCourseCenter(selectedGrade.value, subject)"
                  class="option-btn"
                  :style="{ width: '100px', height: '36px' }"
                  :class="{ 'option-btn-active': selectedSubject === subject }"
              >
                {{ subject }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- 轮播图区域 -->
        <div class="pc-content">
          <div v-if="!isLoading && carouselSlides.length === 0" class="empty-carousel">
            <p>暂无广告数据</p>
          </div>
          <el-carousel
              v-else
              :interval="3000"
              arrow="always"
              indicator-position="outside"
              :height="carouselHeight"
              v-loading="isLoading"
              class="carousel-container"
          >
            <el-carousel-item v-for="slide in carouselSlides" :key="slide.id">
              <div class="carousel-content" @click="navigateToFeaturedCourse(slide.link)">
                <div class="carousel-img-wrapper">
                  <img :src="fixCoverPath(slide.image)" alt="carousel" class="carousel-img">
                </div>
                <div class="carousel-overlay">
                  <h3 class="carousel-title">{{ slide.title }}</h3>
                </div>
              </div>
            </el-carousel-item>
          </el-carousel>
        </div>
      </div>

      <!-- 推荐课程组件 -->
      <div class="recommend-courses">
        <div class="section-title">
          <h2>推荐课程</h2>
        </div>
        <Recommend class="recommend-wrapper" :limit="8" />
      </div>
    </div>

    <!-- 底部页脚（单独层级） -->
    <Footer class="footer-fixed" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavigationBar from '../components/NavigationBar.vue'
import Footer from '../components/Footer.vue'
import Recommend from '../components/main/RecommendComponent.vue'
import axiosInstance from "@/service/api.js"
import { fixCoverPath } from '@/utils/format.js'

const router = useRouter()
const currentNav = ref('home')
const selectedGrade = ref('')
const selectedSubject = ref('')
const carouselHeight = ref('350px')
const isLoading = ref(true)

// 年级和科目数据
const grades = ['初一', '初二', '初三', '高一', '高二', '高三']
const subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理']

// 轮播图数据
const carouselSlides = ref([])

// 名称转ID映射
const gradeNameToIdMap = { '初一':1, '初二':2, '初三':3, '高一':4, '高二':5, '高三':6 }
const subjectNameToIdMap = { '语文':1, '数学':2, '英语':3, '物理':4, '化学':5, '生物':6, '政治':7, '历史':8, '地理':9 }

// 获取轮播图数据
const fetchCarouselData = async () => {
  isLoading.value = true
  try {
    const res = await axiosInstance.get('/api/admin/get-advertisement')
    if (res.data.success) {
      carouselSlides.value = res.data.data.map(ad => ({
        id: ad.id, image: ad.image, title: ad.name, link: ad.link
      }))
    } else {
      ElMessage.warning(res.data.message || '获取广告数据失败')
    }
  } catch (error) {
    console.error('获取轮播图失败', error)
    ElMessage.error('获取广告数据失败')
  } finally {
    isLoading.value = false
  }
}

// 跳转课程中心
const navigateToCourseCenter = (grade, subject) => {
  selectedGrade.value = grade
  selectedSubject.value = subject
  const gradeId = grade ? gradeNameToIdMap[grade] : null
  const subjectId = subject ? subjectNameToIdMap[subject] : null
  
  const query = {}
  if (gradeId) query.grades = gradeId
  if (subjectId) query.subjects = subjectId
  router.push({ name: 'CourseCenter', query })
}

// 跳转特色课程
const navigateToFeaturedCourse = (url) => {
  if (!url) return
  url.startsWith('http') ? window.open(url, '_blank') : router.push(url)
}

// 初始化
onMounted(() => fetchCarouselData())
</script>

<style scoped>
/* 核心：容器占满视口，Flex垂直布局 */
.pc-container {
  width: 100%;
  height: 100vh; /* 强制占满视口高度（关键） */
  background-color: #f0f7f4;
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 避免容器本身滚动 */
}

/* 中间内容：自动填充，超出时滚动 */
.content-wrapper {
  flex: 1; /* 填充除页脚外的所有空间 */
  overflow-y: auto; /* 内容超出时滚动 */
  padding-bottom: 20px; /* 避免内容贴页脚 */
}

.pc-main {
  max-width: 1400px;
  height: 400px; /* 保留原有高度 */
  margin: 20px auto 0;
  display: flex;
  gap: 30px;
  padding: 0 20px;
  position: relative;
  align-items: stretch;
}

.pc-sidebar {
  width: 400px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px;
  box-sizing: border-box;
  position: sticky;
  top: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.sidebar-section {
  margin-bottom: 15px;
  margin-left: 10px;
}

.sidebar-section h3 {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
  color: #333;
  position: relative;
  padding-left: 12px;
  text-align: left;
}

.sidebar-section h3::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 20px;
  background-color: #20c997;
  border-radius: 3px;
}

.option-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.option-btn {
  display: inline-block;
  box-sizing: border-box;
  margin: 0;
  padding: 0 10px;
  font-size: 14px;
  line-height: 36px;
  text-align: center;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  color: #4b5563;
  background-color: #f9fafb;
  transition: all 0.3s;
}

.option-btn:hover {
  background-color: #e0e9e5;
  border-color: #20c997;
  color: #206644;
}

.option-btn-active {
  background-color: #ecfdf5;
  border-color: #20c997;
  color: #206644;
}

.pc-content {
  flex: 1;
  background-color: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e9e5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-carousel {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  border-radius: 12px;
  background-color: #f9fafb;
}

.carousel-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 12px;
}

.carousel-content {
  position: relative;
  width: 100%;
  height: 100%;
  cursor: pointer;
  overflow: hidden;
  border-radius: 12px;
}

.carousel-img-wrapper {
  width: 100%;
  height: 100%;
  transition: transform 0.5s ease;
}

.carousel-content:hover .carousel-img-wrapper {
  transform: scale(1.05);
}

.carousel-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.carousel-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: white;
}

.carousel-content:hover .carousel-overlay {
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.85));
}

.carousel-title {
  font-size: 20px;
  margin: 0 0 8px 0;
  transform: translateY(10px);
  transition: transform 0.3s ease;
}

.carousel-content:hover .carousel-title {
  transform: translateY(0);
}

.recommend-courses {
  max-width: 1400px;
  margin: 30px auto 0;
  padding: 0 20px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e9e5;
}

.section-title h2 {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.recommend-wrapper {
  width: 100%;
}

.footer-fixed {
  width: 100%;
  margin-top: auto; 
}
</style>