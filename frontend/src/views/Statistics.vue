<template>
  <div class="pc-container">
    <!-- 顶部导航栏 -->
    <NavigationBar :currentNav="currentNav" />

    <!-- 主体内容包裹层 -->
    <div class="content-wrapper">
      <div class="stats-container">
        <div class="stats-header">
          <h1>平台运营数据统计中心</h1>
        </div>

        <!-- 核心筛选区 -->
        <div class="filter-container">
          <el-card class="filter-card">
            <div class="filter-row">
              <!-- 范围筛选 -->
              <div class="range-filter">
                <div class="filter-item">
                  <span class="filter-label">年级：</span>
                  <el-select
                      v-model="selectedGradeIds"
                      multiple
                      placeholder="全部年级"
                      class="filter-select"
                      @change="handleFilterChange"
                      collapse-tags
                      collapse-tags-tooltip
                  >
                    <el-option
                        v-for="grade in allGrades"
                        :key="grade.id"
                        :label="grade.name"
                        :value="grade.id"
                    ></el-option>
                  </el-select>
                </div>
                <div class="filter-item">
                  <span class="filter-label">科目：</span>
                  <el-select
                      v-model="selectedSubjectIds"
                      multiple
                      placeholder="全部科目"
                      class="filter-select"
                      @change="handleFilterChange"
                      collapse-tags
                      collapse-tags-tooltip
                  >
                    <el-option
                        v-for="subject in allSubjects"
                        :key="subject.id"
                        :label="subject.name"
                        :value="subject.id"
                    ></el-option>
                  </el-select>
                  <el-button type="primary" @click="resetFilters" size="default">重置</el-button>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 统计概览卡片 -->
        <div class="stats-overview">
          <el-card class="overview-card">
            <div class="overview-item">
              <span class="item-label">📚 总课程数</span>
              <span class="item-value">{{ filteredStats.totalCourses || 0 }}</span>
            </div>
          </el-card>
          <el-card class="overview-card">
            <div class="overview-item">
              <span class="item-label">👥 总订阅人数</span>
              <span class="item-value">{{ filteredStats.totalSubscribers || 0 }}</span>
            </div>
          </el-card>
          <el-card class="overview-card">
            <div class="overview-item">
              <span class="item-label">👨‍🏫 总讲师数</span>
              <span class="item-value">{{ filteredStats.totalTeachers || 0 }}</span>
            </div>
          </el-card>
          <el-card class="overview-card">
            <div class="overview-item">
              <span class="item-label">💰 课程平均价格</span>
              <span class="item-value">{{ (filteredStats.averagePrice || 0).toFixed(2) }} 元</span>
            </div>
          </el-card>
          <el-card class="overview-card">
            <div class="overview-item">
              <span class="item-label">📊 总收益</span>
              <span class="item-value">{{ (filteredStats.totalRevenue || 0).toFixed(2) }} 元</span>
            </div>
          </el-card>
          <el-card class="overview-card">
            <div class="overview-item">
              <span class="item-label">📈 课程平均收益</span>
              <span class="item-value">{{ (filteredStats.averageRevenue || 0).toFixed(2) }} 元</span>
            </div>
          </el-card>
        </div>

        <!-- 图表选择区 -->
        <div class="chart-selection">
          <h3>可选图表</h3>

          <!-- 图表筛选区 -->
          <div class="chart-filter">
            <div class="filter-row">
              <div class="range-filter">
                <div class="filter-item">
                  <span class="filter-label">图表年级：</span>
                  <el-select
                      v-model="chartSelectedGradeIds"
                      multiple
                      placeholder="全部年级"
                      class="filter-select"
                      @change="handleChartFilterChange"
                      collapse-tags
                      collapse-tags-tooltip
                  >
                    <el-option
                        v-for="grade in allGrades"
                        :key="grade.id"
                        :label="grade.name"
                        :value="grade.id"
                    ></el-option>
                  </el-select>
                </div>
                <div class="filter-item">
                  <span class="filter-label">图表科目：</span>
                  <el-select
                      v-model="chartSelectedSubjectIds"
                      multiple
                      placeholder="全部科目"
                      class="filter-select"
                      @change="handleChartFilterChange"
                      collapse-tags
                      collapse-tags-tooltip
                  >
                    <el-option
                        v-for="subject in allSubjects"
                        :key="subject.id"
                        :label="subject.name"
                        :value="subject.id"
                    ></el-option>
                  </el-select>
                </div>
                <div class="filter-item">
                  <span class="filter-label">TOP数量：</span>
                  <el-select
                      v-model="chartTopCount"
                      class="filter-select chart-top-select"
                      @change="handleChartTopCountChange"
                      placeholder="选择数量"
                  >
                    <el-option label="TOP5" value="5"></el-option>
                    <el-option label="TOP10" value="10"></el-option>
                  </el-select>
                  <el-button type="primary" @click="resetChartFilters" class="chart-reset-btn">重置筛选</el-button>
                </div>
              </div>
            </div>
          </div>

          <div class="chart-options">
            <el-tag
                v-for="(chart, key) in allAvailableCharts"
                :key="key"
                :closable="false"
                :type="selectedCharts.includes(key) ? 'success' : ''"
                @click="toggleChart(key)"
                class="chart-tag"
            >
              {{ chart.name }}
            </el-tag>
          </div>
          <p class="selection-info">
            已选 {{ selectedCharts.length }}/{{ maxChartCount }} 个图表
          </p>
        </div>

        <!-- 图表显示区 -->
        <div class="charts-container">
          <div
              class="chart-wrapper"
              v-for="chartKey in selectedCharts"
              :key="chartKey"
          >
            <el-card>
              <div slot="header" class="chart-header">
                <!-- 动态显示图表标题，包含TOP数量 -->
                <h2>
                  {{ getChartTitle(chartKey) }}
                </h2>
                <div class="chart-actions">
                  <el-button
                      icon="delete"
                      size="default"
                      circle
                      @click="removeChart(chartKey)"
                  ></el-button>
                </div>
              </div>
              <div class="chart-content">
                <div :ref="el => chartRefs[chartKey] = el" class="chart" />
              </div>
            </el-card>
          </div>

          <div class="empty-state" v-if="selectedCharts.length === 0">
            <el-empty description="请从上方选择需要查看的图表"></el-empty>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部页脚 -->
    <Footer class="footer-fixed" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElLoading } from 'element-plus';
import * as echarts from 'echarts';
import NavigationBar from '../components/NavigationBar.vue';
import Footer from '../components/Footer.vue';
import axiosInstance from "@/service/api.js";

// 状态定义
const currentNav = ref('statistics');
const summary = ref({
  total_courses: 0,
  total_subscribers: 0,
  total_teachers: 0,
  total_grades: 0,
  total_subjects: 0
});

// 原始数据存储
const originalGradeSubjectStats = ref([]);
const originalTeacherCourseStats = ref([]);

// 筛选相关
const allGrades = ref([]);
const allSubjects = ref([]);
const selectedGradeIds = ref([]);
const selectedSubjectIds = ref([]);

// 图表相关筛选
const chartSelectedGradeIds = ref([]);
const chartSelectedSubjectIds = ref([]);
const chartTopCount = ref('5');

// 图表相关
const chartInstances = ref({});
const maxChartCount = 6;
const chartRefs = ref({});
const allAvailableCharts = ref({
  subjectSubscription: { name: '科目订阅占比', isTopChart: false },
  gradeSubscription: { name: '年级订阅分布', isTopChart: false },
  teacherSubscription: { name: '讲师订阅数', isTopChart: true },
  teacherRevenue: { name: '讲师总收益', isTopChart: true },
  courseRevenue: { name: '课程总收益', isTopChart: true },
  gradeRevenue: { name: '年级收益分布', isTopChart: false },
  subjectRevenue: { name: '科目收益分布', isTopChart: false },
  priceDistribution: { name: '课程价格分布', isTopChart: false }
});
const selectedCharts = ref([]);

// 筛选后的数据统计 - 重构计算逻辑
const filteredStats = computed(() => {
  const { gradeSubject, teacherCourse } = getFilteredData();

  // 计算总课程数
  const courseMap = new Map();
  teacherCourse.forEach(course => {
    courseMap.set(course.course_id, true);
  });
  const totalCourses = courseMap.size;

  // 计算总订阅人数
  const totalSubscribers = teacherCourse.reduce(
      (sum, course) => sum + (Number(course.subscriber_count) || 0),
      0
  );

  // 计算总讲师数
  const teacherMap = new Map();
  teacherCourse.forEach(course => {
    teacherMap.set(course.teacher_id, true);
  });
  const totalTeachers = teacherMap.size;

  // 计算总收益
  const totalRevenue = teacherCourse.reduce((sum, course) => {
    const price = Number(course.price) || 0;
    const subscribers = Number(course.subscriber_count) || 0;
    return sum + (price * subscribers);
  }, 0);

  // 计算平均价格
  const validCourses = teacherCourse.filter(course => Number(course.price) > 0);
  const averagePrice = validCourses.length > 0
      ? validCourses.reduce((sum, course) => sum + Number(course.price), 0) / validCourses.length
      : 0;

  // 计算平均收益
  const averageRevenue = totalCourses > 0 ? totalRevenue / totalCourses : 0;

  return {
    totalCourses,
    totalSubscribers,
    totalTeachers,
    totalRevenue,
    averagePrice,
    averageRevenue
  };
});

// 获取图表标题（包含TOP数量）
const getChartTitle = (chartKey) => {
  const chart = allAvailableCharts.value[chartKey];
  if (chart.isTopChart) {
    return `${chart.name} TOP${chartTopCount.value}`;
  }
  return chart.name;
};

const router = useRouter();

// 获取统计数据
const fetchStatistics = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '加载统计数据...',
    background: 'rgba(255, 255, 255, 0.7)'
  });

  try {
    const res = await axiosInstance.get('/api/admin/statistics');
    if (res.data.success) {
      summary.value = res.data.data.summary || {
        total_courses: 0,
        total_subscribers: 0,
        total_teachers: 0
      };
      originalGradeSubjectStats.value = res.data.data.grade_subject_statistics || [];
      originalTeacherCourseStats.value = res.data.data.teacher_course_statistics || [];
      extractGradesAndSubjects();
    } else {
      ElMessage.error(res.data.message || '获取数据失败');
    }
  } catch (error) {
    ElMessage.error(error.response?.status === 403 ? '无权限访问' : '服务器错误');
    if (error.response?.status === 403) router.push('/login');
  } finally {
    loading.close();
  }
};

// 提取年级和科目列表
const extractGradesAndSubjects = () => {
  const gradeMap = {};
  originalGradeSubjectStats.value.forEach(item => {
    if (!gradeMap[item.grade_id]) {
      gradeMap[item.grade_id] = { id: item.grade_id, name: item.grade_name };
    }
  });
  allGrades.value = Object.values(gradeMap);

  const subjectMap = {};
  originalGradeSubjectStats.value.forEach(item => {
    if (!subjectMap[item.subject_id]) {
      subjectMap[item.subject_id] = { id: item.subject_id, name: item.subject_name };
    }
  });
  allSubjects.value = Object.values(subjectMap);

  chartSelectedGradeIds.value = [...selectedGradeIds.value];
  chartSelectedSubjectIds.value = [...selectedSubjectIds.value];
};

// 筛选变化处理
const handleFilterChange = () => {};

// 重置筛选
const resetFilters = () => {
  selectedGradeIds.value = [];
  selectedSubjectIds.value = [];
  handleFilterChange();
};

// 获取筛选后的数据（用于概览卡片）
const getFilteredData = () => {
  const gradeSubject = originalGradeSubjectStats.value.filter(item => {
    const gradePass = !selectedGradeIds.value.length || selectedGradeIds.value.includes(item.grade_id);
    const subjectPass = !selectedSubjectIds.value.length || selectedSubjectIds.value.includes(item.subject_id);
    return gradePass && subjectPass;
  });

  const teacherCourse = originalTeacherCourseStats.value.filter(item => {
    const gradePass = !selectedGradeIds.value.length || selectedGradeIds.value.includes(item.grade_id);
    const subjectPass = !selectedSubjectIds.value.length || selectedSubjectIds.value.includes(item.subject_id);
    return gradePass && subjectPass;
  });

  return { gradeSubject, teacherCourse };
};

// 获取图表筛选后的数据
const getChartFilteredData = () => {
  const gradeSubject = originalGradeSubjectStats.value.filter(item => {
    const gradePass = !chartSelectedGradeIds.value.length || chartSelectedGradeIds.value.includes(item.grade_id);
    const subjectPass = !chartSelectedSubjectIds.value.length || chartSelectedSubjectIds.value.includes(item.subject_id);
    return gradePass && subjectPass;
  });

  const teacherCourse = originalTeacherCourseStats.value.filter(item => {
    const gradePass = !chartSelectedGradeIds.value.length || chartSelectedGradeIds.value.includes(item.grade_id);
    const subjectPass = !chartSelectedSubjectIds.value.length || chartSelectedSubjectIds.value.includes(item.subject_id);
    return gradePass && subjectPass;
  });

  return { gradeSubject, teacherCourse };
};

// 图表筛选变化处理
const handleChartFilterChange = () => {
  renderAllCharts();
};

// 图表TOP数量变化处理
const handleChartTopCountChange = () => {
  renderAllCharts();
};

// 重置图表筛选
const resetChartFilters = () => {
  chartSelectedGradeIds.value = [];
  chartSelectedSubjectIds.value = [];
  chartTopCount.value = '5';
  handleChartFilterChange();
};

// 图表管理
const toggleChart = (chartKey) => {
  if (selectedCharts.value.includes(chartKey)) {
    removeChart(chartKey);
  } else {
    if (selectedCharts.value.length >= maxChartCount) {
      ElMessage.warning(`已达到图表数量上限(${maxChartCount}个)，请先移除不需要的图表`);
      return;
    }
    selectedCharts.value = [...selectedCharts.value, chartKey];
    setTimeout(() => {
      renderChart(chartKey);
    }, 0);
  }
};

const removeChart = (chartKey) => {
  if (chartInstances.value[chartKey]) {
    chartInstances.value[chartKey].dispose();
    chartInstances.value[chartKey] = null;
  }
  selectedCharts.value = selectedCharts.value.filter(key => key !== chartKey);
};

// 渲染所有选中的图表
const renderAllCharts = () => {
  selectedCharts.value.forEach(chartKey => {
    renderChart(chartKey);
  });
};

// 渲染单个图表
const renderChart = (chartKey) => {
  const element = chartRefs.value[chartKey];
  if (!element) return;

  if (chartInstances.value[chartKey]) {
    chartInstances.value[chartKey].dispose();
  }

  switch (chartKey) {
    case 'subjectSubscription':
      renderSubjectSubscriptionChart(chartKey, element);
      break;
    case 'gradeSubscription':
      renderGradeSubscriptionChart(chartKey, element);
      break;
    case 'teacherSubscription':
      renderTeacherSubscriptionChart(chartKey, element);
      break;
    case 'teacherRevenue':
      renderTeacherRevenueChart(chartKey, element);
      break;
    case 'courseRevenue':
      renderCourseRevenueChart(chartKey, element);
      break;
    case 'gradeRevenue':
      renderGradeRevenueChart(chartKey, element);
      break;
    case 'subjectRevenue':
      renderSubjectRevenueChart(chartKey, element);
      break;
    case 'priceDistribution':
      renderPriceDistributionChart(chartKey, element);
      break;
  }
};

// 1. 科目订阅占比图表
const renderSubjectSubscriptionChart = (chartKey, element) => {
  const { gradeSubject } = getChartFilteredData();
  const instance = echarts.init(element);
  chartInstances.value[chartKey] = instance;

  const subjectData = {};
  gradeSubject.forEach(item => {
    const key = item.subject_id;
    if (!subjectData[key]) {
      subjectData[key] = { name: item.subject_name, value: 0 };
    }
    subjectData[key].value += Number(item.total_subscribers) || 0;
  });

  const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#556EE6', '#F7B824', '#FF8A4C', '#7367F0', '#2B9348'];
  instance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const total = Object.values(subjectData).reduce((sum, item) => sum + item.value, 0);
        const percentage = total > 0 ? ((params.value / total) * 100).toFixed(1) : '0.0';
        return `
          <div style="font-weight: bold;">${params.name}</div>
          <div>订阅人数: ${params.value}</div>
          <div>占比: ${percentage}%</div>
        `;
      }
    },
    legend: {
      orient: 'vertical',
      left: 10,
      formatter: name => {
        const item = Object.values(subjectData).find(i => i.name === name);
        const total = Object.values(subjectData).reduce((sum, i) => sum + i.value, 0);
        const percentage = total > 0 && item ? ((item.value / total) * 100).toFixed(1) : '0.0';
        return `${name} (${percentage}%)`;
      }
    },
    series: [{
      name: '订阅人数',
      type: 'pie',
      radius: ['45%', '75%'],
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2,
        color: function (params) {
          return colors[params.dataIndex % colors.length];
        }
      },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
      data: Object.values(subjectData).filter(i => i.value > 0)
    }]
  });

  const resizeHandler = () => instance.resize();
  window.addEventListener('resize', resizeHandler);
  instance.__resizeHandler = resizeHandler;
};

// 2. 年级订阅分布图表
const renderGradeSubscriptionChart = (chartKey, element) => {
  const { gradeSubject } = getChartFilteredData();
  const instance = echarts.init(element);
  chartInstances.value[chartKey] = instance;

  const gradeData = {};
  gradeSubject.forEach(item => {
    const key = item.grade_id;
    if (!gradeData[key]) gradeData[key] = { name: item.grade_name, value: 0 };
    gradeData[key].value += Number(item.total_subscribers) || 0;
  });

  instance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const data = params[0];
        return `
          <div style="font-weight: bold;">${data.name}</div>
          <div>订阅人数: ${data.value}</div>
        `;
      }
    },
    grid: { left: '5%', right: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: Object.values(gradeData).map(i => i.name) },
    yAxis: { type: 'value', name: '订阅人数' },
    series: [{
      name: '订阅人数',
      type: 'bar',
      data: Object.values(gradeData).map(i => i.value),
      itemStyle: {
        color: '#3b82f6'
      },
      barWidth: '60%'
    }]
  });

  const resizeHandler = () => instance.resize();
  window.addEventListener('resize', resizeHandler);
  instance.__resizeHandler = resizeHandler;
};

// 3. 讲师订阅数TOP图表
const renderTeacherSubscriptionChart = (chartKey, element) => {
  const { teacherCourse } = getChartFilteredData();
  const instance = echarts.init(element);
  chartInstances.value[chartKey] = instance;

  const teacherData = {};
  teacherCourse.forEach(course => {
    const key = course.teacher_id;
    if (!teacherData[key]) {
      teacherData[key] = {
        name: course.teacher_name,
        value: 0,
        courseCount: 0
      };
    }
    teacherData[key].value += Number(course.subscriber_count) || 0;
    teacherData[key].courseCount += 1;
  });

  const sortedData = Object.values(teacherData)
      .sort((a, b) => b.value - a.value)
      .slice(0, Number(chartTopCount.value))
      .reverse();

  instance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const data = params[0];
        const teacher = sortedData.find(t => t.name === data.name);
        return teacher ? `
          <div style="font-weight: bold;">${teacher.name}</div>
          <div>课程数: ${teacher.courseCount}门</div>
          <div>总订阅: ${teacher.value}人</div>
          <div>平均订阅: ${Math.round(teacher.value / teacher.courseCount)}人/门</div>
        ` : data.name;
      }
    },
    grid: { left: '5%', right: '15%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: '总订阅人数' },
    yAxis: {
      type: 'category',
      data: sortedData.map(item => item.name),
      axisLabel: { formatter: v => v.length > 10 ? v.slice(0, 10) + '...' : v }
    },
    series: [{
      name: '订阅人数',
      type: 'bar',
      data: sortedData.map(item => item.value),
      itemStyle: {
        color: '#2e7d32'
      },
      label: {
        show: true,
        position: 'right',
        fontSize: 12,
        formatter: (valueObj) => {
          const value = valueObj.value || 0;
          return value.toString();
        }
      },
      barWidth: '60%'
    }]
  });

  const resizeHandler = () => instance.resize();
  window.addEventListener('resize', resizeHandler);
  instance.__resizeHandler = resizeHandler;
};

// 4. 讲师总收益TOP图表
const renderTeacherRevenueChart = (chartKey, element) => {
  const { teacherCourse } = getChartFilteredData();
  const instance = echarts.init(element);
  chartInstances.value[chartKey] = instance;

  const teacherData = {};
  teacherCourse.forEach(course => {
    const key = course.teacher_id;
    if (!teacherData[key]) {
      teacherData[key] = {
        name: course.teacher_name,
        revenue: 0,
        courseCount: 0
      };
    }

    const price = Number(course.price) || 0;
    const subscribers = Number(course.subscriber_count) || 0;
    teacherData[key].revenue += price * subscribers;
    teacherData[key].courseCount += 1;
  });

  const sortedData = Object.values(teacherData)
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, Number(chartTopCount.value))
      .reverse();

  instance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const data = params[0];
        const teacher = sortedData.find(t => t.name === data.name);
        return teacher ? `
          <div style="font-weight: bold;">${teacher.name}</div>
          <div>课程数: ${teacher.courseCount}门</div>
          <div>总收益: ${teacher.revenue.toFixed(2)}元</div>
          <div>平均收益: ${(teacher.revenue / teacher.courseCount).toFixed(2)}元/门</div>
        ` : data.name;
      }
    },
    grid: { left: '5%', right: '15%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: '总收益（元）' },
    yAxis: {
      type: 'category',
      data: sortedData.map(item => item.name),
      axisLabel: { formatter: v => v.length > 10 ? v.slice(0, 10) + '...' : v }
    },
    series: [{
      name: '总收益',
      type: 'bar',
      data: sortedData.map(item => item.revenue),
      itemStyle: {
        color: '#FF7A45'
      },
      label: {
        show: true,
        position: 'right',
        fontSize: 12,
        formatter: (valueObj) => {
          const value = Number(valueObj.value) || 0;
          return `${value.toFixed(2)}元`;
        }
      },
      barWidth: '60%'
    }]
  });

  const resizeHandler = () => instance.resize();
  window.addEventListener('resize', resizeHandler);
  instance.__resizeHandler = resizeHandler;
};

// 5. 课程总收益TOP图表
const renderCourseRevenueChart = (chartKey, element) => {
  const { teacherCourse } = getChartFilteredData();
  const instance = echarts.init(element);
  chartInstances.value[chartKey] = instance;

  const courseData = [...teacherCourse]
      .map(course => ({
        ...course,
        revenue: (Number(course.price) || 0) * (Number(course.subscriber_count) || 0)
      }))
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, Number(chartTopCount.value))
      .reverse();

  instance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const data = params[0];
        const course = courseData.find(c => c.course_name === data.name);
        return course ? `
          <div style="font-weight: bold;">${course.course_name}</div>
          <div>讲师: ${course.teacher_name}</div>
          <div>价格: ${Number(course.price).toFixed(2)}元</div>
          <div>订阅: ${Number(course.subscriber_count)}人</div>
          <div>总收益: ${course.revenue.toFixed(2)}元</div>
        ` : data.name;
      }
    },
    grid: { left: '5%', right: '15%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: '总收益（元）' },
    yAxis: {
      type: 'category',
      data: courseData.map(item => item.course_name),
      axisLabel: { formatter: v => v.length > 12 ? v.slice(0, 12) + '...' : v }
    },
    series: [{
      name: '总收益',
      type: 'bar',
      data: courseData.map(item => item.revenue),
      itemStyle: {
        color: '#8E2DE2'
      },
      label: {
        show: true,
        position: 'right',
        fontSize: 12,
        formatter: (valueObj) => {
          const value = Number(valueObj.value) || 0;
          return `${value.toFixed(2)}元`;
        }
      },
      barWidth: '60%'
    }]
  });

  const resizeHandler = () => instance.resize();
  window.addEventListener('resize', resizeHandler);
  instance.__resizeHandler = resizeHandler;
};

// 6. 年级收益分布图表
const renderGradeRevenueChart = (chartKey, element) => {
  const { teacherCourse } = getChartFilteredData();
  const instance = echarts.init(element);
  chartInstances.value[chartKey] = instance;

  const gradeData = {};
  teacherCourse.forEach(course => {
    const key = course.grade_id;
    if (!gradeData[key]) {
      gradeData[key] = {
        name: course.grade_name,
        revenue: 0,
        courseCount: 0
      };
    }

    const price = Number(course.price) || 0;
    const subscribers = Number(course.subscriber_count) || 0;
    gradeData[key].revenue += price * subscribers;
    gradeData[key].courseCount += 1;
  });

  const sortedData = Object.values(gradeData).sort((a, b) => a.name.localeCompare(b.name));

  instance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const data = params[0];
        const grade = sortedData.find(g => g.name === data.name);
        return grade ? `
          <div style="font-weight: bold;">${grade.name}</div>
          <div>课程数: ${grade.courseCount}门</div>
          <div>总收益: ${grade.revenue.toFixed(2)}元</div>
          <div>平均收益: ${(grade.revenue / grade.courseCount).toFixed(2)}元/门</div>
        ` : data.name;
      }
    },
    grid: { left: '5%', right: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: sortedData.map(item => item.name) },
    yAxis: { type: 'value', name: '总收益（元）' },
    series: [{
      name: '年级收益',
      type: 'bar',
      data: sortedData.map(item => item.revenue),
      itemStyle: {
        color: '#3b82f6'
      },
      barWidth: '60%'
    }]
  });

  const resizeHandler = () => instance.resize();
  window.addEventListener('resize', resizeHandler);
  instance.__resizeHandler = resizeHandler;
};

// 7. 科目收益分布图表
const renderSubjectRevenueChart = (chartKey, element) => {
  const { teacherCourse } = getChartFilteredData();
  const instance = echarts.init(element);
  chartInstances.value[chartKey] = instance;

  const subjectData = {};
  teacherCourse.forEach(course => {
    const key = course.subject_id;
    if (!subjectData[key]) {
      subjectData[key] = {
        name: course.subject_name,
        revenue: 0,
        courseCount: 0
      };
    }

    const price = Number(course.price) || 0;
    const subscribers = Number(course.subscriber_count) || 0;
    subjectData[key].revenue += price * subscribers;
    subjectData[key].courseCount += 1;
  });

  const sortedData = Object.values(subjectData).sort((a, b) => b.revenue - a.revenue);

  instance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const data = params[0];
        const subject = sortedData.find(s => s.name === data.name);
        return subject ? `
          <div style="font-weight: bold;">${subject.name}</div>
          <div>课程数: ${subject.courseCount}门</div>
          <div>总收益: ${subject.revenue.toFixed(2)}元</div>
          <div>平均收益: ${(subject.revenue / subject.courseCount).toFixed(2)}元/门</div>
        ` : data.name;
      }
    },
    grid: { left: '5%', right: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: sortedData.map(item => item.name) },
    yAxis: { type: 'value', name: '总收益（元）' },
    series: [{
      name: '科目收益',
      type: 'bar',
      data: sortedData.map(item => item.revenue),
      itemStyle: {
        color: '#f97316'
      },
      barWidth: '60%'
    }]
  });

  const resizeHandler = () => instance.resize();
  window.addEventListener('resize', resizeHandler);
  instance.__resizeHandler = resizeHandler;
};

// 8. 课程价格分布图表
const renderPriceDistributionChart = (chartKey, element) => {
  const { teacherCourse } = getChartFilteredData();
  const instance = echarts.init(element);
  chartInstances.value[chartKey] = instance;

  const prices = teacherCourse
      .filter(c => Number(c.price) > 0)
      .map(c => Number(c.price) || 0);

  if (prices.length === 0) {
    instance.setOption({
      title: { text: '无付费课程数据', left: 'center', top: 'center' },
      grid: { show: false },
      xAxis: { show: false },
      yAxis: { show: false }
    });
    return;
  }

  const maxPrice = Math.max(...prices);
  const binSize = Math.ceil(maxPrice / 8);
  const bins = Array.from({ length: 8 }, (_, i) => ({
    name: `${i * binSize}-${(i + 1) * binSize}元`,
    count: 0
  }));

  prices.forEach(price => {
    const binIndex = Math.min(Math.floor(price / binSize), 7);
    bins[binIndex].count++;
  });

  bins.forEach(bin => {
    const minPrice = bin.name.split('-')[0];
    const maxPrice = bin.name.split('-')[1].replace('元', '');
    const coursesInRange = teacherCourse.filter(
        c => Number(c.price) >= Number(minPrice) && Number(c.price) < Number(maxPrice)
    );

    bin.totalRevenue = coursesInRange.reduce(
        (sum, c) => sum + (Number(c.price) * Number(c.subscriber_count)),
        0
    );
  });

  instance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const data = params[0];
        const bin = bins.find(b => b.name === data.name);
        return bin ? `
          <div style="font-weight: bold;">${bin.name}</div>
          <div>课程数量: ${bin.count}门</div>
          <div>总收益: ${bin.totalRevenue.toFixed(2)}元</div>
        ` : data.name;
      }
    },
    grid: { left: '5%', right: '5%', bottom: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: bins.map(item => item.name),
      axisLabel: { rotate: 30, interval: 0, fontSize: 12 }
    },
    yAxis: { type: 'value', name: '课程数量' },
    series: [{
      name: '价格区间课程数',
      type: 'bar',
      data: bins.map(item => item.count),
      itemStyle: {
        color: '#ef4444'
      },
      barWidth: '70%'
    }]
  });

  const resizeHandler = () => instance.resize();
  window.addEventListener('resize', resizeHandler);
  instance.__resizeHandler = resizeHandler;
};

// 监听窗口大小变化，重绘所有图表
watch(() => window.innerWidth, () => {
  Object.values(chartInstances.value).forEach(instance => {
    instance?.resize();
  });
});

// 监听选中图表变化，确保新增图表被渲染
watch(selectedCharts, (newVal, oldVal) => {
  const addedCharts = newVal.filter(key => !oldVal.includes(key));
  addedCharts.forEach(chartKey => {
    setTimeout(() => {
      renderChart(chartKey);
    }, 0);
  });
});

// 监听TOP数量变化，更新图表标题
watch(chartTopCount, () => {
  // 不需要额外操作，标题会通过计算属性自动更新
});

// 组件挂载后初始化
onMounted(() => {
  fetchStatistics();

  window.addEventListener('resize', () => {
    Object.values(chartInstances.value).forEach(instance => {
      instance?.resize();
    });
  });
});

// 组件卸载前清理
onUnmounted(() => {
  Object.values(chartInstances.value).forEach(instance => {
    if (instance && instance.__resizeHandler) {
      window.removeEventListener('resize', instance.__resizeHandler);
      instance.dispose();
    }
  });
});
</script>

<style scoped>
/* 核心修改：flex布局让页脚固定底部 */
.pc-container {
  width: 100%;
  min-height: 100vh;
  background-color: #f0f7f4;
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

/* 中间内容包裹层：填充剩余空间，超出滚动 */
.content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 20px;
}

.stats-container {
  max-width: 1400px;
  margin: 20px auto;
  padding: 0 20px 40px;
}

.stats-header {
  margin: 20px 0;
  text-align: center;
}

.stats-header h1 {
  color: #1f2937;
  font-size: 26px;
  margin: 0 0 8px 0;
}

.stats-header p {
  color: #6b7280;
  font-size: 15px;
  margin: 0;
}

/* 筛选区域 */
.filter-container {
  margin-bottom: 20px;
  overflow: hidden;
}

.filter-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  padding: 10px 15px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
  min-width: 0;
}

.range-filter {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  margin-bottom: 8px;
}

.filter-label {
  color: #6b7280;
  font-size: 16px;
  white-space: nowrap;
}

.filter-select {
  width: 160px;
  min-width: 0;
}

/* 概览卡片 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.overview-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.overview-item {
  padding: 15px;
  text-align: center;
}

.item-label {
  display: block;
  color: #6b7280;
  font-size: 13px;
  margin-bottom: 6px;
}

.item-value {
  display: block;
  color: #1f2937;
  font-size: 22px;
  font-weight: 600;
  color: #20c997;
}

/* 图表选择区 */
.chart-selection {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  padding: 15px;
  margin-bottom: 20px;
}

.chart-selection h3 {
  margin-top: 0;
  color: #1f2937;
  font-size: 18px;
  margin-bottom: 15px;
}

.chart-filter {
  margin-bottom: 15px;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 15px;
}

.chart-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.chart-options .el-tag {
  cursor: pointer;
  padding: 6px 12px;
  font-size: 14px;
  transition: all 0.2s;
}

.chart-options .el-tag--success {
  background-color: #f0fdf4;
  color: #166534;
  border-color: #bbf7d0;
}

.selection-info {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

/* 图表显示区 */
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.chart-wrapper {
  width: 100%;
  transition: all 0.3s ease;
}

.el-card {
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.07);
  border: 1px solid #e5e7eb;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #e5e7eb;
}

.chart-header h2 {
  color: #1f2937;
  font-size: 18px;
  font-weight: 600;
  height: 30px;
  margin: 0;
}

.chart-actions {
  display: flex;
  gap: 8px;
}

.chart-content {
  padding: 15px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chart {
  width: 100%;
  flex: 1;
  min-height: 320px;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 40px 0;
  display: flex;
  justify-content: center;
}

/* 调整图表选择区按钮大小 */
.chart-tag {
  padding: 8px 16px !important;
  font-size:16px !important;
  margin: 4px !important;
}

.chart-top-select {
  width: 120px !important;
  font-size: 15px !important;
}

.chart-reset-btn {
  padding: 10px 20px !important;
  font-size: 15px !important;
  margin-left: 10px !important;
}

/* 页脚固定样式 */
.footer-fixed {
  width: 100%;
  margin-top: auto;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .charts-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .charts-container {
    grid-template-columns: 1fr;
  }

  .filter-select {
    width: 130px;
  }
}

@media (max-width: 600px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-header h2 {
    font-size: 14px;
  }

  .filter-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .range-filter {
    width: 100%;
  }
}

@media (max-width: 450px) {
  .stats-overview {
    grid-template-columns: 1fr;
  }

  .chart {
    min-height: 280px;
  }

  .charts-container {
    grid-template-columns: 1fr;
  }

  .filter-select {
    width: 100%;
  }
}
</style>