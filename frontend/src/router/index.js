import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import Auth from '../views/Auth.vue'
import Home from '../views/Home.vue'
import PersonalCenter from '@/views/PersonalCenter.vue'
import CourseCenter from '@/views/CourseCenter.vue'
import CourseDetail from '@/views/CourseDetail.vue'
import CourseContent from '@/views/CourseContent.vue'
import Statistics from '@/views/Statistics.vue'
import InvitationCodeManagement from '@/components/managementTool/InvitationCodeManagement.vue'
import AdManagement from '@/components/managementTool/AdManagement.vue'
import MySubscribe from '@/components/studentCourse/MySubscribe.vue'
import MyFavorite from '@/components/studentCourse/MyFavorite.vue'
import StudentProfile from "@/components/profile/StudentProfile.vue";
import CourseManagement from "@/components/course/CourseManagement.vue";
import TeacherProfile from "@/components/profile/TeacherProfile.vue";

const routes = [
  {
    path: '/auth',
    name: 'Auth',
    component: Auth
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/personalCenter',
    name: 'PersonalCenter',
    component: PersonalCenter,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'mySubscribe',
        name: 'MySubscribe',
        component: MySubscribe
      },
      {
        path: 'myFavorite',
        name: 'MyFavorite',
        component: MyFavorite
      },
      {
        path: 'studentProfile',
        name: 'StudentProfile',
        component: StudentProfile
      },
      {
        path:'courseManagement',
        name: 'CourseManagement',
        component: CourseManagement
      },
      {
        path:'teacherProfile',
        name: 'TeacherProfile',
        component: TeacherProfile
      },
      {
        path: 'invitationCode',
        name: 'InvitationCodeManagement',
        component: InvitationCodeManagement,
        meta: { title: '邀请码管理' }
      },
      {
        path: 'adManagement',
        name: 'AdManagement',
        component: AdManagement,
        meta: { title: '广告管理' }
      }
    ]
  },
  {
    path: '/course',
    name: 'CourseCenter',
    component: CourseCenter,
    meta: { requiresAuth: true },
  },
  {
    path: '/course/:id',
    name: 'CourseDetail',
    component: CourseDetail,
    meta: {
      title: '课程详情',
      requiresAuth: true
    }
  },
  {
    path: '/course/:id/content',
    name: 'CourseContent',
    component: CourseContent,
    meta: {
      title: '课程内容',
      requiresAuth: true
    }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics,
  },
  {
    path: '/',
    redirect: '/auth?type=login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    console.log(sessionStorage.getItem('isLogin'))
    const isLogin = sessionStorage.getItem('isLogin') === '1';
    if (!isLogin) {
      ElMessage.warning('请先登录！')
      next({
        path: '/auth',
        query: {
          type: 'login',
          redirect: to.fullPath
        }
      });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router