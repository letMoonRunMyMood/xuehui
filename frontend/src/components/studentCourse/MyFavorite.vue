<template>
  <div class="my-favorite">
    <!-- 页面标题与操作 -->
    <div class="page-header">
      <h2 class="page-title">我的收藏课程</h2>
    </div>

    <!-- 课程筛选 -->
    <div class="course-filter">
      <input
          v-model="searchKey"
          placeholder="搜索课程名称/教师"
          class="search-input"
          @keyup.enter="filterCourses"
      >
      <el-button
          @click="filterCourses"
          class="filter-item-button"
          :icon="Search"
      >筛选</el-button>
    </div>

    <!-- 课程列表 -->
    <div class="course-list">
      <!-- 课程网格 -->
      <div class="cards-grid" v-if="!isLoading && courses.length > 0">
        <div
            v-for="course in visibleCourses"
            :key="course.course_id"
            class="course-card"
            @click="viewCourseDetail(course.course_id)"
        >
          <!-- 课程封面：使用fixCoverPath修复路径 -->
          <div class="course-cover">
            <img
                :src="fixCoverPath(course.course_cover) || fixedDefaultCover"
                alt="课程封面"
                class="cover-image"
            >
          </div>

          <!-- 课程信息 -->
          <div class="course-info">
            <h3 class="course-title">{{ course.course_name }}</h3>

            <!-- 信息列展示 -->
            <div class="info-columns">
              <div class="info-column">
                <div class="info-item"><i class="el-icon-user"></i> 讲师：{{ course.teacher.teacher_username }}</div>
                <div class="info-item"><i class="el-icon-s-claim"></i> 年级：{{ course.grade.grade_name }}</div>
              </div>
              <div class="info-column">
                <div class="info-item"><i class="el-icon-s-marketing"></i> 科目：{{ course.subject.subject_name }}</div>
                <div class="info-item"><i class="el-icon-s-finance"></i> 价格：{{ course.course_price }}</div>
              </div>
            </div>

            <!-- 操作区域 -->
            <div class="course-actions">
              <el-button
                  class="course-detail-button"
                  size="default"
                  @click.stop="viewCourseDetail(course.course_id)"
              >查看详情</el-button>
              <el-button
                  class="course-delete-button"
                  size="default"
                  type="danger"
                  @click.stop="cancelFavorite(course.course_id)"
              >取消收藏</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态提示 -->
      <div class="empty-state" v-if="courses.length === 0 && !isLoading">
        <el-icon size="64"><Document /></el-icon>
        <p>您还没有收藏任何课程</p>
      </div>

      <!-- 加载状态 -->
      <div class="loading-state" v-if="isLoading">
        <el-skeleton :rows="6" active></el-skeleton>
      </div>
    </div>

    <!-- 分页组件 -->
    <div class="pagination-container">
      <el-pagination
          class="custom-pagination"
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          layout="prev, pager, next"
          :total="totalCourses"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox, ElIcon } from 'element-plus'
import { useRouter } from 'vue-router'
import { Search, Document } from '@element-plus/icons-vue'
import axiosInstance from '@/service/api.js'
import { fixCoverPath } from '@/utils/format.js'

const router = useRouter()
const isLoading = ref(true)
const studentId = ref(null)

const rawDefaultCover = ref('static/default/default_course_cover.jpg')
const fixedDefaultCover = computed(() => fixCoverPath(rawDefaultCover.value))

// 课程数据 - 同步订阅课程的分页数量
const courses = ref([])
const currentPage = ref(1)
const pageSize = ref(3)  // 与订阅课程保持一致
const totalCourses = ref(0)
const searchKey = ref('')

// 计算可见课程
const visibleCourses = computed(() => {
  if (!Array.isArray(courses.value)) {
    return []
  }

  let filteredCourses = [...courses.value]

  // 搜索筛选
  if (searchKey.value) {
    filteredCourses = filteredCourses.filter(course =>
        course.course_name.toLowerCase().includes(searchKey.value.toLowerCase()) ||
        course.teacher.teacher_username.toLowerCase().includes(searchKey.value.toLowerCase()) ||
        course.subject.subject_name.toLowerCase().includes(searchKey.value.toLowerCase()) ||
        course.grade.grade_name.toLowerCase().includes(searchKey.value.toLowerCase())
    )
  }

  totalCourses.value = filteredCourses.length

  // 分页处理
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredCourses.slice(start, end)
})

// 防抖函数
const debounce = (fn, delay) => {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

// 获取收藏课程列表
const fetchFavoriteCourses = debounce(async () => {
  isLoading.value = true

  try {
    // 从session获取学生ID
    const id = sessionStorage.getItem('id')
    if (!id) {
      ElMessage.error('获取学生ID失败，请重新登录')
      router.push('/login')
      isLoading.value = false
      return
    }

    studentId.value = id

    // 调用API获取收藏课程
    const response = await axiosInstance.get('/api/student/get-favorite-course', {
      params: {
        student_id: id,
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchKey.value
      }
    })

    if (response.data.success) {
      courses.value = response.data.data.courses || []
      totalCourses.value = response.data.data.total_courses || 0
    } else {
      ElMessage.error(response.data.message || '获取收藏课程失败')
    }
  } catch (error) {
    console.error('获取收藏课程失败', error)
    ElMessage.error('获取收藏课程失败，请检查网络连接')
  } finally {
    isLoading.value = false
  }
}, 300)

// 查看课程详情
const viewCourseDetail = (courseId) => {
  router.push({
    name: 'CourseDetail',
    params: { id: courseId }
  }).catch(err => {
    console.error('课程详情跳转失败', err)
    ElMessage.error('跳转课程详情失败，请重试')
  })
}

// 取消收藏
const cancelFavorite = async (courseId) => {
  try {
    // 确认对话框
    await ElMessageBox.confirm(
        '确定要取消该课程的收藏吗？',
        '提示',
        { type: 'warning', confirmButtonText: '确认取消', cancelButtonText: '取消' }
    )
        .then(() => {
          // 用户点击确认按钮
          return new Promise(async (resolve, reject) => {
            try {
              // 创建FormData并发送请求
              const formData = new FormData()
              formData.append('student_id', studentId.value)
              formData.append('course_id', courseId)

              const response = await axiosInstance.delete('/api/student/cancel-favorite', {
                data: formData,
                headers: {
                  'Content-Type': 'multipart/form-data'
                }
              })

              if (response.data.success) {
                ElMessage.success('取消收藏成功')
                fetchFavoriteCourses() // 刷新课程列表
                resolve()
              } else {
                ElMessage.error(response.data.message || '取消收藏失败')
                reject(response.data.message || '取消收藏失败')
              }
            } catch (error) {
              console.error('取消收藏失败', error)
              if (error.response) {
                ElMessage.error(error.response.data.message || '取消收藏失败')
              } else {
                ElMessage.error('网络错误，请检查您的网络连接')
              }
              reject(error)
            }
          })
        })
        .catch((err) => {
          // 用户点击取消按钮或关闭对话框
          if (err === 'cancel') {
            ElMessage.info('中止操作')
          } else {
            // 其他错误（如网络错误）
            console.error('操作出错', err)
          }
        })
  } catch (error) {
    console.error('取消收藏过程出错', error)
  }
}

// 分页事件处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchFavoriteCourses()
}

const handlePageChange = (val) => {
  currentPage.value = val
  fetchFavoriteCourses()
}

// 筛选课程
const filterCourses = () => {
  currentPage.value = 1
  fetchFavoriteCourses()
}

// 组件挂载时获取收藏课程
onMounted(() => {
  // 从sessionStorage获取学生ID
  const id = sessionStorage.getItem('id')
  if (id) {
    studentId.value = id
    fetchFavoriteCourses()
  } else {
    ElMessage.error('请先登录')
    router.push('/login')
  }
})

// 监听搜索关键词变化
watch(searchKey, () => {
  if (searchKey.value) {
    currentPage.value = 1
    fetchFavoriteCourses()
  }
})

// 监听学生ID变化（例如登录状态变化）
watch(studentId, (newId) => {
  if (newId) {
    fetchFavoriteCourses()
  }
})
</script>

<style scoped>
/* 基础容器样式 - 与订阅课程保持一致 */
.my-favorite {
  flex: 1;
  background-color: #fff;
  border-radius: 12px;
  padding: 24px;
  box-sizing: border-box;
  min-height: 600px;
}

/* 页面标题 */
.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

/* 筛选区域 - 与订阅课程统一样式 */
.course-filter {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 36px; /* 与订阅课程保持一致的间距 */
}

.search-input {
  flex: 1;
  height: 48px;
  padding: 0 16px;
  border: 2px solid #999; /* 加粗边框，与订阅课程一致 */
  border-radius: 8px; /* 增大圆角 */
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.search-input:hover {
  outline: none;
  border-color: #20c997;
  box-shadow: 0 0 0 2px rgba(32, 201, 151, 0.2);
}

.filter-item-button {
  height: 52px; /* 增高按钮，与订阅课程一致 */
  padding: 0 16px;
  border-radius: 8px; /* 增大圆角 */
  border: 2px solid #999; /* 加粗边框 */
  background-color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: border-color 0.3s ease;
}

.filter-item-button:hover {
  border-color: #20c997;
}

/* 课程列表区域 */
.course-list {
  margin-bottom: 32px;
}

/* 课程网格布局 */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

/* 课程卡片样式 */
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
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  border-color: #20c997;
}

/* 课程封面 */
.course-cover {
  width: 100%;
  height: 160px;
  overflow: hidden;
  background-color: #f9fafb;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.course-card:hover .cover-image {
  transform: scale(1.08);
}

/* 课程信息区域 */
.course-info {
  padding: 15px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.course-title {
  font-size: 17px;
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

/* 信息列布局 */
.info-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 15px;
  flex: 1;
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

/* 操作区域 - 按钮尺寸与订阅课程统一 */
.course-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid #e5e7eb;
}

.course-detail-button {
  background-color: #2b6a3d;
  color: #fff;
  border: none;
}

.course-detail-button:hover {
  background-color: #235530;
}

.course-delete-button {
  background-color: #fff;
  color: #ef4444;
  border: 1px solid #ef4444;
}

.course-delete-button:hover {
  background-color: #fef2f2;
}

/* 空状态与加载状态 */
.empty-state {
  padding: 60px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

.loading-state {
  padding: 20px;
}

/* 分页组件 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

.custom-pagination .el-pagination__item {
  border: 1px solid #dcdde0;
  border-radius: 4px;
  margin: 0 4px;
  transition: all 0.2s ease;
}

.custom-pagination .el-pagination__item.is-active {
  background-color: #20c997;
  border-color: #20c997;
  color: #fff;
}

/* 响应式适配 */
@media (max-width: 1100px) {
  .cards-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 800px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 500px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }

  .course-filter {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item-button {
    width: 100%;
  }
}
</style>