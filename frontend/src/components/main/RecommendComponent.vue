<template>
  <div class="recommend-container">
    <div class="content-wrapper">
      <div class="cards-section">
        <div class="cards-grid" v-if="!isLoading && recommendCourses.length > 0">
          <div
              v-for="(item, index) in recommendCourses"
              :key="item.id || index"
              class="course-card"
              @click="handleCourseClick(item)"
          >
            <div class="course-cover">
              <!-- 修复：添加fixCoverPath路径修复，保留默认封面逻辑 -->
              <img :src="fixCoverPath(item.cover) || defaultCover" alt="课程封面" class="cover-image" 
                @load="handleImgLoad(item.id, item.cover)"
                @error="handleImgError(item.id, item.cover)" />
            </div>

            <div class="course-info">
              <h3 class="course-title">{{ item.name }}</h3>

              <div class="info-columns">
                <div class="info-column">
                  <div class="info-item"><i class="el-icon-user"></i> 讲师：{{ item.teacher_name }}</div>
                  <div class="info-item"><i class="el-icon-s-data"></i> 年级：{{ item.grade_name }}</div>
                </div>
                <div class="info-column">
                  <div class="info-item"><i class="el-icon-folder-opened"></i> 科目：{{ item.subject_name }}</div>
                  <div class="info-item"><i class="el-icon-user-solid"></i> 学习人数：{{ item.subscriber_count }}</div>
                </div>
              </div>

              <div class="course-meta">
                <div class="course-price" :class="item.price === 0 ? 'free' : 'paid'">
                  {{ item.price === 0 ? '免费' : `¥${item.price.toFixed(2)}` }}
                </div>
                <div class="course-time">{{ formatDate(item.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="empty-state" v-else-if="!isLoading">
          <el-icon size="64"><Document /></el-icon>
          <p>暂无推荐课程</p>
        </div>
        <div class="loading-state" v-else>
          <el-skeleton :rows="6" active></el-skeleton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Document } from '@element-plus/icons-vue'
import { ElSkeleton, ElIcon } from 'element-plus'
import axiosInstance from "@/service/api.js";
// 新增：导入路径修复方法
import { fixCoverPath } from '@/utils/format.js'

const router = useRouter()
const recommendCourses = ref([])
const isLoading = ref(false)
const defaultCover = 'https://picsum.photos/seed/course/600/400?random=1'
const isDetailLoading = ref(false)

const formatDate = (date) => {
  if (!date) return ''
  return typeof date === 'string' ? date.split(' ')[0] :
      `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

const handleCourseClick = (course) => {
  isDetailLoading.value = true
  router.push({ name: 'CourseDetail', params: { id: course.id } }).catch(err => {
    console.error('路由跳转失败:', err)
    isDetailLoading.value = false
  })
}

// 新增：封面加载调试方法（保留原有console.log，新增调试信息）
const handleImgLoad = (courseId, originalCover) => {
  const processedPath = fixCoverPath(originalCover)
  console.log(`课程${courseId}封面加载成功`, {
    原始路径: originalCover,
    修复后路径: processedPath
  })
}

const handleImgError = (courseId, originalCover) => {
  const processedPath = fixCoverPath(originalCover)
  console.error(`课程${courseId}封面加载失败`, {
    原始路径: originalCover,
    修复后路径: processedPath,
    默认封面: defaultCover
  })
}

const loadRecommendCourses = async () => {
  isLoading.value = true
  try {
    const response = await axiosInstance.get('/api/course/recommend', { params: { limit: 8 } })
    recommendCourses.value = response.data.success ? response.data.data.courses.slice(0, 8) : []
    console.log('sdasfa')
    // 新增：打印课程封面原始数据，方便调试
    recommendCourses.value.forEach(course => {
      console.log(`课程${course.id}原始封面路径:`, course.cover)
      console.log(`课程${course.id}修复后封面路径:`, fixCoverPath(course.cover))
    })
  } catch (error) {
    console.error('请求课程失败:', error)
    recommendCourses.value = []
  } finally {
    isLoading.value = false
  }
}

onMounted(() => loadRecommendCourses())
</script>

<style scoped>
.recommend-container {
  width: 100%;
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-sizing: border-box;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  max-width: 1300px;
  margin: 0 auto;
  padding: 0 10px;
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
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  border-color: #20c997;
}

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

.info-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
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

.loading-state {
  padding: 20px;
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
}
</style>