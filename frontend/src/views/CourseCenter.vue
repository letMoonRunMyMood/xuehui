<template>
  <!-- 全局容器：Flex垂直布局，占满视口高度 -->
  <div class="pc-container">
    <NavigationBar :currentNav="currentNav" />

    <!-- 内容区域：自动填充剩余空间，超出时滚动 -->
    <div class="content-wrapper">
      <div class="main-container">
        <div class="filter-section">
          <div class="search-header">
            <h3 class="search-title">课程搜索</h3>
            <div class="search-container">
              <el-input
                v-model="searchKeyword"
                placeholder="输入课程名或讲师名来搜索课程..."
                class="search-input"
                @keyup.enter="handleSearch"
              >
                <template #append>
                  <button class="search-icon-btn" @click="handleSearch">
                    <svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="feather feather-search">
                      <circle cx="11" cy="11" r="8" />
                      <line x1="21" y1="21" x2="16.65" y2="16.65" />
                    </svg>
                  </button>
                </template>
              </el-input>
            </div>
          </div>

          <div class="filter-groups-column">
            <div class="filter-group">
              <h3>选择年级</h3>
              <div class="filter-buttons">
                <el-button
                  v-for="grade in gradeOptions"
                  :key="grade.id"
                  @click="handleGradeSelect(grade.id)"
                  :class="{ 'active': selectedGrade.includes(grade.id) }"
                  type="text"
                >
                  {{ grade.name }}
                </el-button>
              </div>
            </div>

            <div class="filter-group">
              <h3>选择科目</h3>
              <div class="filter-buttons">
                <el-button
                  v-for="subject in subjectOptions"
                  :key="subject.id"
                  @click="handleSubjectSelect(subject.id)"
                  :class="{ 'active': selectedSubject.includes(subject.id) }"
                  type="text"
                >
                  {{ subject.name }}
                </el-button>
              </div>
            </div>

            <div class="filter-group date-group">
              <h3>时间范围</h3>
              <div class="date-filters">
                <el-button @click="clearDateRange" type="text" class="filter-reset-button">全部</el-button>
                <el-date-picker
                  v-model="startDate"
                  type="date"
                  placeholder="开始日期"
                  style="width: 180px; margin-right: 10px;"
                  @change="handleDateChange('start')"
                ></el-date-picker>
                <el-date-picker
                  v-model="endDate"
                  type="date"
                  placeholder="结束日期"
                  style="width: 180px;"
                  @change="handleDateChange('end')"
                ></el-date-picker>
              </div>
            </div>

            <div class="filter-group price-group">
              <h3>最高价格</h3>
              <div class="price-filters">
                <el-button @click="resetMaxPrice" type="text" class="filter-reset-button">全部</el-button>
                <el-input-number
                  v-model="maxPrice"
                  :min="0"
                  :precision="1"
                  placeholder="输入最高价格"
                  style="width: 180px; height: 30px;"
                  @change="fetchCourses"
                ></el-input-number>
              </div>
            </div>

            <div class="filter-group sort-group">
              <h3>排序方式</h3>
              <div class="sort-buttons">
                <el-button
                  type="text"
                  :class="{ 'active': activeSort === 'default' }"
                  @click="sortByDefault"
                >
                  综合排序
                </el-button>
                <el-button
                  type="text"
                  :class="{ 'active': activeSort === 'lowPrice' }"
                  @click="sortByLowPrice"
                >
                  最低价格
                </el-button>
                <el-button
                  type="text"
                  :class="{ 'active': activeSort === 'latest' }"
                  @click="sortByLatest"
                >
                  最新发布
                </el-button>
                <el-button
                  type="text"
                  :class="{ 'active': activeSort === 'mostSubscribed' }"
                  @click="sortByMostSubscribed"
                >
                  最多订阅
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <div class="course-list-section">
          <div class="section-header">
            <h2 class="section-title">全部课程</h2>
            <p class="result-count">共 {{ pagination.total }} 门课程</p>
          </div>

          <div v-if="isLoading" class="loading-state">
            <el-skeleton :rows="8" active></el-skeleton>
          </div>

          <div v-if="errorMessage" class="error-state">
            <el-alert type="error" :message="errorMessage" show-icon></el-alert>
          </div>

          <div class="course-grid" v-else-if="courses.length > 0" :key="activeSort">
            <div
              class="course-card"
              v-for="course in courses"
              :key="course.id"
              @click="handleCourseCardClick(course)"
              :class="{ 'loading-card': isDetailLoading && selectedCourseId === course.id }"
            >
              <div class="course-cover">
                <!-- 封面路径修正：兼容后端路径格式，拼接完整URL -->
                <img :src="fixCoverPath(course.cover) || defaultCover" alt="课程封面" />
              </div>

              <div class="course-info">
                <h3 class="course-title">{{ course.name }}</h3>
                <div class="info-columns">
                  <div class="info-column">
                    <div class="info-item"><i class="el-icon-user"></i> 讲师：{{ course.teacher_name }}</div>
                    <div class="info-item"><i class="el-icon-s-data"></i> 年级：{{ course.grade_name }}</div>
                  </div>
                  <div class="info-column">
                    <div class="info-item"><i class="el-icon-folder-opened"></i> 科目：{{ course.subject_name }}</div>
                    <div class="info-item"><i class="el-icon-user-solid"></i> 学习人数：{{ course.subscriber_count }}</div>
                  </div>
                </div>
                <div class="course-meta">
                  <div class="course-price {{ course.price === 0 ? 'free' : 'paid' }}">
                    {{ course.price === 0 ? '免费' : `¥${course.price.toFixed(2)}` }}
                  </div>
                  <div class="course-time">{{ course.created_at }}</div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <el-icon size="64"><Document /></el-icon>
            <p>未找到符合条件的课程</p>
          </div>

          <el-pagination
            class="pagination"
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="pagination.total"
            layout="prev, pager, next"
            @size-change="handlePageSizeChange"
            @current-change="handleCurrentPageChange"
            background
          />
        </div>
      </div>
    </div>

    <!-- 页脚：固定到底部 -->
    <Footer class="footer-fixed" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElButton, ElSkeleton, ElAlert, ElPagination, ElIcon, ElDatePicker, ElInputNumber, ElInput } from 'element-plus'
import NavigationBar from '../components/NavigationBar.vue'
import Footer from '../components/Footer.vue'
import axiosInstance from '@/service/api.js'
import { Document } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const currentNav = ref('courseCenter')
const defaultCover = 'https://picsum.photos/400/225?random=1'

// 封面路径修正：兼容Windows反斜杠、拼接后端域名
const fixCoverPath = (path) => {
  if (!path || typeof path !== 'string') {
    console.warn('无效的cover路径：', path);
    return '';
  }
  let fixedPath = path.replace(/\\/g, '/');
  const backendBaseUrl = 'http://localhost:5000';
  
  if (fixedPath.startsWith('/')) {
    fixedPath = `${backendBaseUrl}${fixedPath}`;
  } else {
    fixedPath = `${backendBaseUrl}/${fixedPath}`;
  }
  
  return fixedPath;
};

// 筛选选项配置
const gradeOptions = ref([
  { id: 0, name: '全部' },
  { id: 1, name: '初一' },
  { id: 2, name: '初二' },
  { id: 3, name: '初三' },
  { id: 4, name: '高一' },
  { id: 5, name: '高二' },
  { id: 6, name: '高三' }
])
const subjectOptions = ref([
  { id: 0, name: '全部' },
  { id: 1, name: '语文' },
  { id: 2, name: '数学' },
  { id: 3, name: '英语' },
  { id: 4, name: '物理' },
  { id: 5, name: '化学' },
  { id: 6, name: '生物' },
  { id: 7, name: '政治' },
  { id: 8, name: '历史' },
  { id: 9, name: '地理' }
])

// 筛选条件
const searchKeyword = ref('')
const selectedGrade = ref([])
const selectedSubject = ref([])
const startDate = ref('')
const endDate = ref('')
const maxPrice = ref(null)
const currentPage = ref(1)
const pageSize = ref(8)
const isLoading = ref(true)
const errorMessage = ref('')
const courses = ref([])
const pagination = ref({
  total: 0,
  page: 1,
  page_size: 8,
  total_pages: 0,
  has_prev: false,
  has_next: false
})

// 排序控制
const activeSort = ref('default')
const sortByDefault = () => {
  activeSort.value = 'default'
  currentPage.value = 1
  fetchCourses()
}
const sortByLowPrice = () => {
  activeSort.value = 'lowPrice'
  currentPage.value = 1
  fetchCourses()
}
const sortByLatest = () => {
  activeSort.value = 'latest'
  currentPage.value = 1
  fetchCourses()
}
const sortByMostSubscribed = () => {
  activeSort.value = 'mostSubscribed'
  currentPage.value = 1
  fetchCourses()
}

// 日期格式化：统一为YYYY-MM-DD格式
const formatDate = (date) => {
  if (!date) return ''
  if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(date)) return date
  date = new Date(date)
  return date instanceof Date && !isNaN(date.getTime())
      ? `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
      : ''
}
const parseRouteDate = (dateStr) => formatDate(dateStr)

// 核心：获取课程列表（带筛选、排序、分页）
const fetchCourses = async () => {
  isLoading.value = true
  try {
    let sortMode, sortDirection
    switch (activeSort.value) {
      case 'default':
        sortMode = 'default'
        sortDirection = 'desc'
        break
      case 'lowPrice':
        sortMode = 'price'
        sortDirection = 'asc'
        break
      case 'latest':
        sortMode = 'created_time'
        sortDirection = 'desc'
        break
      case 'mostSubscribed':
        sortMode = 'subscriber'
        sortDirection = 'desc'
        break
      default:
        sortMode = 'default'
        sortDirection = 'desc'
    }

    const params = {
      keyword: searchKeyword.value,
      grades: selectedGrade.value.length ? selectedGrade.value.join(',') : undefined,
      subjects: selectedSubject.value.length ? selectedSubject.value.join(',') : undefined,
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
      max_price: maxPrice.value ?? undefined,
      sort_mode: sortMode,
      sort_direction: sortDirection,
      page_size: pageSize.value,
      page: currentPage.value,
      t: new Date().getTime()
    }

    const response = await axiosInstance.get('/api/course/search-courses', { params })
    if (response.data.success) {
      courses.value = response.data.data.courses
      pagination.value = response.data.data.pagination
    } else {
      errorMessage.value = response.data.message || '获取课程失败'
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '网络错误，请重试'
  } finally {
    isLoading.value = false
  }
}

// 日期筛选变更处理
const handleDateChange = (type) => {
  if (type === 'start') startDate.value = formatDate(startDate.value)
  else endDate.value = formatDate(endDate.value)
  currentPage.value = 1
  fetchCourses()
}

// 监听路由参数：同步筛选条件
watch(
  () => route.query,
  (query) => {
    selectedGrade.value = query.grades ? (Array.isArray(query.grades) ? query.grades.map(Number) : [Number(query.grades)]) : []
    selectedSubject.value = query.subjects ? (Array.isArray(query.subjects) ? query.subjects.map(Number) : [Number(query.subjects)]) : []
    searchKeyword.value = query.keyword || ''
    startDate.value = parseRouteDate(query.start_date)
    endDate.value = parseRouteDate(query.end_date)
    maxPrice.value = query.max_price !== undefined ? Number(query.max_price) : null

    currentPage.value = Number(query.page) || 1
    pageSize.value = Number(query.page_size) || 8

    fetchCourses()
  },
  { immediate: true }
)

// 年级筛选
const handleGradeSelect = (gradeId) => {
  selectedGrade.value = gradeId === 0 ? [] :
      selectedGrade.value.includes(gradeId)
          ? selectedGrade.value.filter(id => id !== gradeId)
          : [...selectedGrade.value, gradeId]
  currentPage.value = 1
  fetchCourses()
}

// 科目筛选
const handleSubjectSelect = (subjectId) => {
  selectedSubject.value = subjectId === 0 ? [] :
      selectedSubject.value.includes(subjectId)
          ? selectedSubject.value.filter(id => id !== subjectId)
          : [...selectedSubject.value, subjectId]
  currentPage.value = 1
  fetchCourses()
}

// 搜索触发
const handleSearch = () => {
  currentPage.value = 1
  fetchCourses()
}

// 清空日期筛选
const clearDateRange = () => {
  startDate.value = ''
  endDate.value = ''
  fetchCourses()
}

// 重置价格筛选
const resetMaxPrice = () => {
  maxPrice.value = null
  fetchCourses()
}

// 分页尺寸变更
const handlePageSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchCourses()
}

// 分页页码变更
const handleCurrentPageChange = (page) => {
  currentPage.value = page
  fetchCourses()
}

// 课程卡片点击：跳转详情页
const isDetailLoading = ref(false)
const selectedCourseId = ref(null)
const handleCourseCardClick = (course) => {
  selectedCourseId.value = course.id
  isDetailLoading.value = true
  router.push({ name: 'CourseDetail', params: { id: course.id } }).catch(() => {
    isDetailLoading.value = false
  })
}
</script>

<style scoped>
/* 全局布局：Flex垂直布局，占满视口 */
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

.main-container {
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-section {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e9e5;
}

.search-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0;
}

.search-title {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.search-container {
  flex: 0 0 50%;
  max-width: 500px;
  border: 2px solid #999;
  border-radius: 4px;
}

.search-input {
  width: 100%;
}

.search-icon-btn {
  background: none;
  border: none;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
}

.search-icon-btn:hover {
  color: #20c997;
  transform: scale(1.1);
}

.search-icon-btn svg {
  width: 20px;
  height: 20px;
}

.filter-groups-column {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.filter-group {
  display: flex;
  align-items: flex-start;
  padding: 5px 0;
}

.filter-group h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
  min-width: 80px;
  padding-top: 5px;
}

.sort-buttons .el-button,
.filter-buttons .el-button,
.filter-reset-button {
  padding: 6px 16px;
  border-radius: 4px;
  transition: all 0.3s;
  color: #333;
  background-color: #fff;
}

.sort-buttons .el-button:hover,
.filter-buttons .el-button:hover,
.filter-reset-button:hover {
  background-color: #f5f5f5;
  color: #333;
  border-color: #d1d5db;
}

.sort-buttons .el-button.active,
.filter-buttons .el-button.active {
  color: #fff;
  background-color: #2b6a3d;
  border-color: #2b6a3d;
}

.sort-buttons {
  display: flex;
  gap: 15px;
  padding-top: 2px;
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding-top: 2px;
  margin-left: 0;
}

.date-group .date-filters, .price-group .price-filters {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: 0;
}

.course-list-section {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e9e5;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e9e5;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.result-count {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.course-card {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #e0e9e5;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  border-color: #20c997;
}

.course-cover {
  height: 180px;
  overflow: hidden;
}

.course-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.course-card:hover .course-cover img {
  transform: scale(1.05);
}

.course-info {
  padding: 15px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.course-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 10px 0;
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
  gap: 10px;
  margin-bottom: 15px;
  flex: 1;
}

.info-item {
  font-size: 14px;
  color: #6b7280;
  display: flex;
  align-items: center;
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

.loading-state {
  padding: 20px;
}

.empty-state {
  padding: 60px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.loading-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.7);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 页脚固定样式 */
.footer-fixed {
  width: 100%;
  margin-top: auto; 
}
</style>