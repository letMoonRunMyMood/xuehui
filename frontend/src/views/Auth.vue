<template>
  <div class="pc-container">
    <header class="auth-header">
      <div class="logo">学 汇</div>
    </header>

    <div class="content-wrapper">
      <div class="bg-decoration top-left circle"></div>
      <div class="bg-decoration bottom-right circle"></div>
      <div class="bg-decoration small-circle1 circle"></div>
      <div class="bg-decoration small-circle2 circle"></div>
      <div class="bg-decoration small-circle3 circle"></div>
      <div class="bg-decoration diagonal-line1 line"></div>
      <div class="bg-decoration diagonal-line2 line"></div>
      <div class="bg-decoration horizontal-line line"></div>
      <div class="bg-decoration vertical-line line"></div>
      <div class="bg-decoration triangle1 shape"></div>
      <div class="bg-decoration triangle2 shape"></div>
      <div class="bg-decoration diamond shape"></div>

      <div class="auth-card-container">
        <div class="auth-card">
          <div class="tab-bar">
            <button
              :class="{ active: currentTab === 'login' }"
              @click="switchTab('login')"
              class="tab-button"
            >登录</button>
            <button
              :class="{ active: currentTab === 'register' }"
              @click="switchTab('register')"
              class="tab-button"
            >注册</button>
          </div>

          <div class="form-section" v-if="currentTab === 'login'">
            <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" class="el-form">
              <el-form-item prop="email">
                <el-input
                  v-model="loginForm.email"
                  placeholder="邮箱"
                  prefix-icon="el-icon-user"
                  class="form-input"
                />
              </el-form-item>
              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  placeholder="密码"
                  type="password"
                  prefix-icon="el-icon-lock"
                  class="form-input"
                />
              </el-form-item>
              <el-form-item prop="verifyCode">
                <div class="verify-row">
                  <el-input
                    v-model="loginForm.verifyCode"
                    placeholder="验证码"
                    prefix-icon="el-icon-key"
                    class="verify-input"
                  />
                  <canvas
                    ref="loginVerifyCanvas"
                    class="verify-canvas"
                    @click="refreshLoginVerifyCode"
                    width="130"
                    height="50"
                  ></canvas>
                </div>
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="handleLogin"
                  class="form-button"
                >登 录</el-button>
              </el-form-item>
            </el-form>
          </div>

          <div class="form-section" v-if="currentTab === 'register'">
            <el-form-item class="identity-selector">
              <div class="identity-options">
                <label
                  :class="{ active: registerForm.identity === 'student' }"
                  @click="registerForm.identity = 'student'"
                >
                  <span>学生</span>
                  <span class="check-indicator"></span>
                </label>
                <label
                  :class="{ active: registerForm.identity === 'teacher' }"
                  @click="registerForm.identity = 'teacher'"
                >
                  <span>讲师</span>
                  <span class="check-indicator"></span>
                </label>
              </div>
            </el-form-item>
            <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" class="el-form">
              <el-form-item prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="用户名 (2-10个字符, 中文/字母/数字)"
                  prefix-icon="el-icon-user"
                  class="form-input"
                />
              </el-form-item>
              <el-form-item prop="email">
                <el-input
                  v-model="registerForm.email"
                  placeholder="邮箱"
                  prefix-icon="el-icon-envelope"
                  class="form-input"
                />
              </el-form-item>
              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
                  placeholder="密码 (6-20位, 含大小写字母和数字)"
                  type="password"
                  prefix-icon="el-icon-lock"
                  class="form-input"
                />
              </el-form-item>
              <el-form-item prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  placeholder="确认密码"
                  type="password"
                  prefix-icon="el-icon-lock"
                  class="form-input"
                />
              </el-form-item>
              <el-form-item prop="captcha">
                <div class="email-row">
                  <el-input
                    v-model="registerForm.captcha"
                    placeholder="邮箱验证码"
                    prefix-icon="el-icon-key"
                    class="verify-input"
                  />
                  <el-button
                    :loading="isSendingEmailCode"
                    @click="sendEmailCaptcha"
                    type="primary"
                    class="form-button small"
                  >
                    {{ isSendingEmailCode ? '发送中...' : emailCodeTips }}
                  </el-button>
                </div>
              </el-form-item>
              <el-form-item prop="invitationCode" v-if="registerForm.identity === 'teacher'">
                <el-input
                  v-model="registerForm.invitationCode"
                  placeholder="内部邀请码"
                  prefix-icon="el-icon-ticket"
                  class="form-input"
                />
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="handleRegister"
                  class="form-button"
                >注 册</el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>
    </div>

    <Footer class="footer-fixed" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElForm, ElInput, ElButton, FormRules } from 'element-plus'
import axiosInstance from '../service/api'
import Footer from '../components/Footer.vue'

type Timer = ReturnType<typeof setInterval> | null

const router = useRouter()
const currentTab = ref('login')

const loginForm = ref({
  email: '',
  password: '',
  verifyCode: ''
})

const registerForm = ref({
  identity: 'student',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  captcha: '',
  invitationCode: ''
})

const loginVerifyCode = ref('')
const loginVerifyCanvas = ref<HTMLCanvasElement | null>(null)

const isSendingEmailCode = ref(false)
const emailCodeTimer = ref<Timer>(null)
const emailCodeCount = ref(60)
const emailCodeTips = ref('点击获取邮箱验证码')

const generateVerifyCode = () => {
  let code = ''
  const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  for (let i = 0; i < 4; i++) code += chars.charAt(Math.floor(Math.random() * chars.length))
  return code
}

const drawVerifyCode = (canvas: HTMLCanvasElement, code: string) => {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  gradient.addColorStop(0, '#f0f0f0');
  gradient.addColorStop(1, '#e0e0e0');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < 4; i++) {
    ctx.strokeStyle = `rgba(${Math.floor(Math.random() * 150)}, ${Math.floor(Math.random() * 150)}, ${Math.floor(Math.random() * 150)}, 0.6)`;
    ctx.beginPath();
    ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  for (let i = 0; i < 20; i++) {
    ctx.fillStyle = `rgba(${Math.floor(Math.random() * 180)}, ${Math.floor(Math.random() * 180)}, ${Math.floor(Math.random() * 180)}, 0.5)`;
    ctx.beginPath();
    ctx.arc(Math.random() * canvas.width, Math.random() * canvas.height, 1 + Math.random(), 0, 2 * Math.PI);
    ctx.fill();
  }

  const chars = code.split('');
  const charWidth = canvas.width / (chars.length + 1);
  chars.forEach((char, index) => {
    const x = (index + 1) * charWidth;
    const fontSize = 28 + Math.floor(Math.random() * 6);
    const y = canvas.height / 2;
    const hue = Math.floor(Math.random() * 360);
    const color = `hsl(${hue}, 80%, 30%)`;
    const rotate = (Math.random() * 20 - 10) * Math.PI / 180;
    const fonts = ['Arial', 'Verdana', 'Tahoma', 'Georgia'];
    const font = fonts[Math.floor(Math.random() * fonts.length)];

    ctx.save();
    ctx.font = `${fontSize}px ${font}`;
    ctx.fillStyle = color;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.translate(x, y);
    ctx.rotate(rotate);
    ctx.fillText(char, 0, 0);
    ctx.restore();
  });
}

const refreshLoginVerifyCode = () => {
  loginVerifyCode.value = generateVerifyCode()
  if (loginVerifyCanvas.value) drawVerifyCode(loginVerifyCanvas.value, loginVerifyCode.value)
}

const sendEmailCaptcha = () => {
  if (!registerForm.value.email) {
    ElMessage.warning('请先输入邮箱')
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.value.email)) {
    ElMessage.warning('请输入正确的邮箱格式')
    return
  }

  isSendingEmailCode.value = true
  emailCodeTips.value = '验证码已发送，请查收邮箱'

  axiosInstance.get('/api/auth/captcha', {
    params: { email: registerForm.value.email }
  })
    .then(response => {
      if (response.status === 200) {
        startEmailCodeTimer()
        ElMessage.success('邮箱验证码已发送')
      } else {
        ElMessage.error(response.data.message || '发送验证码失败')
        resetEmailCodeStatus()
      }
    })
    .catch(error => {
      console.error('发送邮箱验证码错误:', error)
      ElMessage.error(error.message)
      resetEmailCodeStatus()
    })
}

const startEmailCodeTimer = () => {
  emailCodeCount.value = 60
  emailCodeTimer.value = setInterval(() => {
    emailCodeCount.value--
    emailCodeTips.value = `${emailCodeCount.value}秒后重新获取`
    if (emailCodeCount.value <= 0) {
      resetEmailCodeStatus()
    }
  }, 1000)
}

const resetEmailCodeStatus = () => {
  if (emailCodeTimer.value) {
    clearInterval(emailCodeTimer.value)
    emailCodeTimer.value = null
  }
  isSendingEmailCode.value = false
  emailCodeCount.value = 60
  emailCodeTips.value = '点击获取邮箱验证码'
}

const loginRules = ref<FormRules>({
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  verifyCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { 
      validator: (_, value, callback) => {
        if (value !== loginVerifyCode.value) callback(new Error('验证码不正确，请重新输入'))
        else callback()
      }, 
      trigger: 'blur' 
    }
  ]
})

const registerRules = ref<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 10, message: '用户名长度必须在2-10个字符之间', trigger: 'blur' },
    { pattern: /^[\u4e00-\u9fa5a-zA-Z0-9]+$/, message: '用户名只能包含中文、字母和数字', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度必须在6-20个字符之间', trigger: 'blur' },
    { pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/, message: '密码必须包含至少一个大写字母、小写字母和数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator: (_, value, callback) => {
        if (value !== registerForm.value.password) callback(new Error('两次输入的密码不一致'))
        else callback()
      }, 
      trigger: 'blur' 
    }
  ],
  captcha: [
    { required: true, message: '请输入邮箱验证码', trigger: 'blur' }
  ],
  invitationCode: [
    { 
      validator: (_, value, callback) => {
        if (registerForm.value.identity === 'teacher' && !value) {
          callback(new Error('讲师注册需要输入内部邀请码'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
})

const loginFormRef = ref<InstanceType<typeof ElForm>>()
const registerFormRef = ref<InstanceType<typeof ElForm>>()

const switchTab = (tab: string) => {
  currentTab.value = tab
  nextTick(() => {
    if (tab === 'login') {
      refreshLoginVerifyCode()
    } else {
      registerForm.value.confirmPassword = ''
      registerForm.value.captcha = ''
      resetEmailCodeStatus()
    }
  })
}

const handleLogin = () => {
  loginFormRef.value?.validate((valid) => {
    if (!valid) {
      ElMessage.warning('请检查输入信息');
      return;
    }

    const formData = new URLSearchParams();
    formData.append('email', loginForm.value.email);
    formData.append('password', loginForm.value.password);

    axiosInstance
      .post('/api/auth/login', formData)
      .then((response) => {
        if (response.status === 200) {
          const role = response.data.data.role;
          const id = response.data.data.user_id;

          sessionStorage.setItem('isLogin', '1');
          sessionStorage.setItem('role', role.toString());
          sessionStorage.setItem('id', id.toString());
          ElMessage.success("登录成功");
          router.push('/home');
        } else {
          ElMessage.error(response.data.message || "登录失败");
        }
      })
      .catch((error) => {
        ElMessage.error(`登录失败: ${error.message || '服务器错误'}`);
      });
  });
};

const handleRegister = () => {
  registerFormRef.value?.validate(valid => {
    if (valid) {
      const formData = new URLSearchParams()
      const role = registerForm.value.identity === 'teacher' ? 1 : 0
      
      formData.append('role', role.toString())
      formData.append('username', registerForm.value.username)
      formData.append('email', registerForm.value.email)
      formData.append('password', registerForm.value.password)
      formData.append('password_confirm', registerForm.value.confirmPassword)
      formData.append('captcha', registerForm.value.captcha)
      
      if (registerForm.value.identity === 'teacher') {
        formData.append('invitation_code', registerForm.value.invitationCode)
      }

      axiosInstance.post('/api/auth/register', formData)
        .then(response => {
          if (response.data.success) {
            ElMessage.success('注册成功，请登录')
            switchTab('login')
          } else {
            ElMessage.error(response.data.message || '注册失败')
          }
        })
        .catch(error => {
          ElMessage.error(`注册失败: ${error.message || '服务器错误'}`);
        })
    } else {
      ElMessage.warning('请检查输入信息')
    }
  })
}

onMounted(() => {
  nextTick(() => {
    if (currentTab.value === 'login') {
      refreshLoginVerifyCode()
    }
  })
})

onBeforeUnmount(() => {
  if (emailCodeTimer.value) clearInterval(emailCodeTimer.value)
})
</script>

<style scoped>
.pc-container {
  width: 100%;
  height: 100vh;
  background-color: #f5f9f6;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.auth-header {
  background-color: #e8f5e9;
  padding: 16px 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  z-index: 1;
  width: 100%;
  box-sizing: border-box;
}

.logo {
  font-size: 22px;
  font-weight: 600;
  color: #2e7d32;
  display: flex;
  align-items: center;
  padding: 8px 16px;
}

.logo::before {
  content: '';
  display: inline-block;
  width: 20px;
  height: 20px;
  background-color: #4caf50;
  border-radius: 4px;
  margin-right: 8px;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden; 
  padding: 40px 16px 60px; 
  box-sizing: border-box;
  position: relative;
  width: 100%; 
}

.bg-decoration {
  position: absolute;
  z-index: 0;
  opacity: 0.1;
  pointer-events: none;
}
.circle { border-radius: 50%; background-color: #4caf50; }
.top-left.circle { top: -100px; left: -100px; width: 200px; height: 200px; }
.bottom-right.circle { bottom: -100px; right: -100px; width: 200px; height: 200px; }
.small-circle1.circle { top: 15%; right: 10%; width: 60px; height: 60px; }
.small-circle2.circle { bottom: 20%; left: 15%; width: 50px; height: 50px; }
.small-circle3.circle { top: 30%; left: 5%; width: 30px; height: 30px; }
.line { background-color: #4caf50; }
.diagonal-line1.line { top: 10%; right: -80px; width: 120px; height: 2px; transform: rotate(25deg); }
.diagonal-line2.line { bottom: 10%; left: -80px; width: 120px; height: 2px; transform: rotate(-25deg); }
.horizontal-line.line { top: 50%; left: -60px; width: 100px; height: 2px; }
.vertical-line.line { right: -30px; top: 30%; width: 2px; height: 80px; }
.shape { position: absolute; background-color: #4caf50; transform-origin: center; }
.triangle1.shape { top: 15%; left: 85%; width: 0; height: 0; border-left: 25px solid transparent; border-right: 25px solid transparent; border-bottom: 40px solid #4caf50; }
.triangle2.shape { bottom: 20%; right: 5%; width: 0; height: 0; border-left: 20px solid transparent; border-right: 20px solid transparent; border-top: 30px solid #4caf50; }
.diamond.shape { top: 35%; right: 20%; width: 30px; height: 30px; background-color: #4caf50; transform: rotate(45deg); }

.auth-card-container {
  max-width: 450px; 
  margin: 0 auto;
  padding: 10px 0;
  position: relative;
  z-index: 1;
  width: 100%; 
}

.auth-card {
  width: 100%;
  padding: 24px 20px; /* 减小内边距，避免宽度溢出 */
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(76, 175, 80, 0.1);
  box-sizing: border-box;
}

.tab-bar {
  display: flex;
  border-bottom: 2px solid #e8f5e9;
  margin-bottom: 24px;
  height: 44px;
  box-sizing: border-box;
}

.tab-button {
  flex: 1;
  height: 44px;
  line-height: 44px;
  text-align: center;
  font-size: 16px;
  color: #666;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  position: relative;
}

.tab-button.active {
  color: #4caf50;
  font-weight: 600;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40%;
  height: 2px;
  background-color: #4caf50;
  border-radius: 1px;
}

.form-section {
  width: 100%;
  height: auto;
}

.el-form {
  width: 100%;
}

.form-input, .verify-input {
  height: 48px;
  border-radius: 6px;
  border-color: #dcdfe6;
  font-size: 16px;
  background-color: #f9f9f9;
  transition: all 0.3s;
  width: 100%;
  box-sizing: border-box;
}

.form-input:focus, .verify-input:focus {
  border-color: #4caf50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.15);
}

.identity-selector {
  margin-bottom: 20px;
}

.identity-options {
  display: flex;
  gap: 12px;
  width: 100%;
  justify-content: space-between;
}

.identity-options label {
  width: calc(50% - 6px);
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  color: #606266;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  position: relative;
  padding-left: 12px;
  background-color: #f9f9f9;
  box-sizing: border-box;
}

.identity-options label.active {
  border-color: #4caf50;
  color: #4caf50;
  font-weight: 500;
  background-color: #e8f5e9;
}

.identity-options .check-indicator {
  position: absolute;
  left: 12px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.identity-options label.active .check-indicator {
  border-color: #4caf50;
}

.identity-options label.active .check-indicator::after {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #4caf50;
  transform: scale(0);
  animation: checkAnimation 0.3s forwards;
}

@keyframes checkAnimation {
  to { transform: scale(1); }
}

.verify-row, .email-row {
  display: flex;
  align-items: center;
  gap: 8px; /* 减小间距，避免溢出 */
  width: 100%;
  box-sizing: border-box;
}

.verify-canvas {
  width: 120px; /* 减小宽度，避免溢出 */
  height: 48px;
  cursor: pointer;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background-color: #f9f9f9;
  flex-shrink: 0;
}

.form-button {
  height: 50px;
  font-size: 16px;
  border-radius: 6px;
  width: 100%;
  font-weight: 500;
  background-color: #4caf50;
  border-color: #4caf50;
  transition: all 0.3s;
  box-sizing: border-box;
}

.form-button.small {
  height: 48px;
  font-size: 14px;
  padding: 0 12px; /* 减小内边距，避免溢出 */
  width: auto;
  flex-shrink: 0;
}

.form-button:hover, .form-button.small:hover {
  background-color: #388e3c;
  border-color: #388e3c;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2);
}

.footer-fixed {
  width: 100%;
  margin-top: auto;
  box-sizing: border-box;
}
</style>