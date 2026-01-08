<template>
  <div class="course-management">
    <div class="page-header">
      <h2 class="page-title">我的课程</h2>
      <el-button type="primary" @click="openCreateCourse" class="create-btn">
        <span>新建课程</span>
      </el-button>
    </div>

    <div class="course-filter">
      <input
        v-model="searchKey"
        placeholder="搜索课程名称"
        class="search-input"
        @keyup.enter="filterCourses"
      >
      <el-button
        @click="filterCourses"
        class="filter-item-button"
        :icon="Search"
      >
        筛选
      </el-button>
    </div>

    <div class="course-list">
      <div class="cards-grid" v-if="!isLoading && courses.length > 0">
        <div
          v-for="course in visibleCourses"
          :key="course.id"
          class="course-card"
          @click="viewCourseDetail(course.id)"
          :data-cover="course.cover"
        >
          <div class="course-cover">
            <img
              :src="fixCoverPath(course.cover) || defaultCover"
              alt="课程封面"
              class="cover-image"
              @error="handleCoverLoadError(course)"
              @load="handleCoverLoadSuccess(course)"
            >
          </div>

          <div class="course-info">
            <h3 class="course-title">{{ course.name || '未命名课程' }}</h3>
            <div class="info-columns">
              <div class="info-column">
                <div class="info-item"><i class="el-icon-user-solid"></i> 学生人数：{{ course.student_count || 0 }}</div>
              </div>
              <div class="info-column">
                <div class="info-item"><i class="el-icon-time"></i> 创建时间：{{ formatTime(course.created_at) || '未知' }}</div>
              </div>
            </div>

            <div class="course-actions">
              <el-button
                class="course-edit-button"
                size="default"
                @click.stop="openChapterEdit(course)"
              >
                编辑课程内容
              </el-button>
              <el-button
                class="course-info-button"
                size="default"
                @click.stop="openCourseInfoEdit(course)"
              >
                修改课程信息
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="empty-state" v-if="courses.length === 0 && !isLoading">
        <el-icon size="64"><Document /></el-icon>
        <p>您还没有创建任何课程</p>
        <el-button type="primary" @click="openCreateCourse" class="create-empty-btn">
          立即创建
        </el-button>
      </div>

      <div class="loading-state" v-if="isLoading">
        <el-skeleton :rows="6" active></el-skeleton>
      </div>
    </div>

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

    <CreateCourseForm
      v-model:visible="createCourseDialogVisible"
      @create="handleCourseCreate"
      @close="handleDialogClose"
    />

    <CourseChapterManager
      v-model:visible="chapterManagerVisible"
      :course="currentEditingCourse"
      @save="handleChapterSave"
      @close="handleChapterManagerClose"
    />

    <CourseInfoEditor
      v-model:visible="courseInfoEditorVisible"
      :course="currentEditingCourseInfo"
      @close="handleCourseInfoEditorClose"
      @update-success="handleCourseInfoUpdateSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { Search, Document } from '@element-plus/icons-vue'
import axiosInstance from '@/service/api.js'
import { CancelToken } from 'axios'
import CreateCourseForm from './CreateCourseForm.vue'
import CourseChapterManager from './CourseChapterManager.vue'
import CourseInfoEditor from './CourseInfoEditor.vue'
import { fixCoverPath } from '@/utils/format.js'

const router = useRouter()
const isLoading = ref(true)
const teacherId = ref(null)
const defaultCover = 'https://picsum.photos/400/220?random=1'

const courses = ref([])
const filteredCourses = ref([])
const currentPage = ref(1)
const pageSize = ref(3)
const totalCourses = ref(0)
const searchKey = ref('')

const createCourseDialogVisible = ref(false)
const chapterManagerVisible = ref(false)
const courseInfoEditorVisible = ref(false)

const currentEditingCourse = reactive({
  id: null,
  title: '',
  chapters: [],
  version: 0,
  lastUpdateTime: 0,
  isUpdating: false
})

const currentEditingCourseInfo = reactive({
  id: null,
  name: '',
  introduction: '',
  price: 0,
  subject_id: '',
  grade_id: '',
  cover: ''
})

const visibleCourses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredCourses.value.slice(start, end)
})

const debounce = (fn, delay) => {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

const fetchCourseChapters = debounce(async (courseId, forceUpdate = false) => {
  if (currentEditingCourse.isUpdating && !forceUpdate) return

  const now = Date.now()
  const timeSinceLastUpdate = now - currentEditingCourse.lastUpdateTime

  if (!forceUpdate && timeSinceLastUpdate < 3000) {
    return
  }

  currentEditingCourse.isUpdating = true

  try {
    const response = await axiosInstance.get('/api/course/get-course-detail', {
      params: { course_id: courseId }
    })

    if (response.data.success) {
      currentEditingCourse.chapters = response.data.data.chapters || []
      currentEditingCourse.version += 1
      currentEditingCourse.lastUpdateTime = now
    } else {
      ElMessage.error(response.data.message || '获取章节失败')
    }
  } catch (error) {
    console.error('获取章节失败', error)
    ElMessage.error('获取章节失败，请重试')
  } finally {
    currentEditingCourse.isUpdating = false
  }
}, 300)

const handleCoverLoadError = (course) => {
  console.error(`课程${course.id}封面加载失败`, { coverUrl: fixCoverPath(course.cover) })
}

const handleCoverLoadSuccess = (course) => {
  console.log(`课程${course.id}封面加载成功`)
}

const openCreateCourse = () => {
  createCourseDialogVisible.value = true
}

const viewCourseDetail = (id) => {
  router.push({ name: 'CourseContent', params: { id } }).catch(err => {
    console.error('课程详情跳转失败', err)
    ElMessage.error('跳转课程详情失败')
  })
}

const openChapterEdit = (course) => {
  currentEditingCourse.id = course.id
  currentEditingCourse.title = course.name || '未命名课程'
  currentEditingCourse.chapters = []
  currentEditingCourse.version = 0
  currentEditingCourse.lastUpdateTime = 0
  currentEditingCourse.isUpdating = false

  chapterManagerVisible.value = true
  nextTick(() => fetchCourseChapters(course.id, true))
}

const openCourseInfoEdit = async (course) => {
  isLoading.value = true
  try {
    const response = await axiosInstance.get('/api/course/get-course-detail', {
      params: { course_id: course.id }
    })

    if (response.data.success) {
      const fullData = response.data.data
      Object.assign(currentEditingCourseInfo, {
        id: fullData.id,
        name: fullData.name || '',
        introduction: fullData.introduction || '',
        price: fullData.price || 0,
        subject_id: fullData.subject_id || undefined,
        grade_id: fullData.grade_id || undefined,
        cover: fullData.cover || ''
      })
      courseInfoEditorVisible.value = true
    } else {
      ElMessage.error(response.data.message || '获取课程详情失败')
    }
  } catch (error) {
    console.error('获取课程详情失败:', error)
    ElMessage.error('获取课程详情失败，请检查网络')
  } finally {
    isLoading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  updateFilteredCourses()
}

const handlePageChange = (val) => {
  currentPage.value = val
  updateFilteredCourses()
}

const filterCourses = () => {
  currentPage.value = 1
  updateFilteredCourses()
}

const handleDialogClose = () => {
  createCourseDialogVisible.value = false
}

const handleChapterManagerClose = () => {
  chapterManagerVisible.value = false
  Object.assign(currentEditingCourse, { id: null, title: '', chapters: [], version: 0, lastUpdateTime: 0, isUpdating: false })
}

const handleCourseInfoEditorClose = () => {
  courseInfoEditorVisible.value = false
  Object.assign(currentEditingCourseInfo, { id: null, name: '', introduction: '', price: 0, subject_id: '', grade_id: '', cover: '' })
}

const handleCourseInfoUpdateSuccess = () => {
  ElMessage.success('课程信息更新成功！')
  fetchCourses()
}

const handleChapterSave = () => {
  ElMessage.success('章节保存成功！')
  fetchCourses()
  chapterManagerVisible.value = false
}

const handleCourseCreate = async () => {
  ElMessage.success('课程创建成功')
  createCourseDialogVisible.value = false
  fetchCourses()
}

const updateFilteredCourses = () => {
  if (!Array.isArray(courses.value)) {
    filteredCourses.value = []
    totalCourses.value = 0
    return
  }

  let result = [...courses.value]
  if (searchKey.value) {
    const searchLower = searchKey.value.toLowerCase()
    result = result.filter(course =>
      course.name?.toLowerCase().includes(searchLower)
    )
  }

  filteredCourses.value = result
  totalCourses.value = result.length
}

const fetchCourses = async () => {
  if (cancelTokenSource) {
    cancelTokenSource.cancel('请求已取消')
  }
  cancelTokenSource = CancelToken.source()

  isLoading.value = true
  try {
    const id = sessionStorage.getItem('id')
    if (!id) {
      ElMessage.error('获取讲师ID失败，请重新登录')
      router.push({
        path: '/auth',
        query: { type: 'login', redirect: router.currentRoute.fullPath }
      })
      return
    }

    teacherId.value = id
    const response = await axiosInstance.get('/api/teacher/get-created-course', {
      params: { teacher_id: id },
      cancelToken: cancelTokenSource.token
    })

    if (response.data.success) {
      courses.value = response.data.data.courses || []
      updateFilteredCourses()
    } else {
      ElMessage.error(response.data.message || '获取课程列表失败')
    }
  } catch (error) {
    if (!axios.isCancel(error)) {
      console.error('获取课程列表失败', error)
      ElMessage.error('获取课程列表失败，请检查网络')
    }
  } finally {
    isLoading.value = false
  }
}

const formatTime = (timeString) => {
  if (!timeString) return ''
  return new Date(timeString).toLocaleDateString()
}

let cancelTokenSource = null
const debouncedSearch = debounce(() => {
  currentPage.value = 1
  updateFilteredCourses()
}, 500)

onMounted(() => {
  const id = sessionStorage.getItem('id')
  if (id) {
    teacherId.value = id
    fetchCourses()
  } else {
    ElMessage.error('请先登录')
    router.push({
      path: '/auth',
      query: { type: 'login', redirect: router.currentRoute.fullPath }
    })
  }
})

onUnmounted(() => {
  if (cancelTokenSource) {
    cancelTokenSource.cancel('组件已卸载，取消请求')
  }
})

watch(searchKey, debouncedSearch)

watch(() => currentEditingCourse.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    fetchCourseChapters(newId, true)
  }
})
</script>

<style scoped>
.course-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 600px;
  background-color: #fff;
  border-radius: 12px;
  padding: 24px;
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.create-btn {
  padding: 8px 16px;
  font-size: 16px;
  height: 50px;
  background-color: #4caf50;
  border: 1px solid #3c9641;
  transition: all 0.3s ease;
}

.create-btn:hover {
  border-color: #148264;
  background-color: #017852;
  transform: translateY(-1px);
}

.create-empty-btn {
  margin-top: 16px;
  background-color: #4caf50;
  border: none;
}

.course-filter {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 36px;
}

.search-input {
  flex: 1;
  height: 48px;
  padding: 0 16px;
  border: 2px solid #999;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.search-input:focus, .search-input:hover {
  outline: none;
  border-color: #20c997;
  box-shadow: 0 0 0 2px rgba(32, 201, 151, 0.2);
}

.filter-item-button {
  height: 52px;
  padding: 0 16px;
  font-size: 16px;
  border-radius: 8px;
  border: 2px solid #999;
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

.course-list {
  flex: 1;
  overflow-y: hidden;
  margin-bottom: 32px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 10px;
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
  height: 95%;
  will-change: transform, box-shadow;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  border-color: #20c997;
}

.course-cover {
  width: 100%;
  height: 200px;
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
  transform: scale(1.05);
}

.course-info {
  padding: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100px;
}

.course-title {
  font-size: 17px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
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
  margin-bottom: 5px;
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

.course-actions {
  display: flex;
  height: 48px;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid #e5e7eb;
  gap: 8px;
}

.course-edit-button, .course-info-button {
  flex: 1;
  padding: 20px 12px;
  font-size: 15px;
  height: 32px;
  border-radius: 6px;
}

.course-edit-button {
  background-color: #2b6a3d;
  color: #fff;
  border: none;
}

.course-edit-button:hover {
  background-color: #235530;
}

.course-info-button {
  background-color: #36b37e;
  color: #fff;
  border: none;
}

.course-info-button:hover {
  background-color: #259b65;
}

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

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: auto;
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

  .info-columns {
    grid-template-columns: 1fr;
  }

  .course-actions {
    flex-direction: column;
  }

  .course-edit-button, .course-info-button {
    width: 100%;
  }
}
</style>