<template>
  <footer class="pc-footer">
    <div class="footer-inner">
      <div class="footer-left">
        <p>© {{ currentYear }} 学汇云课堂</p>
        <p>提供优质的在线教育服务</p>
      </div>
      <div class="footer-right">
        <div class="footer-links">
          <a href="#" @click.prevent>关于我们</a>
          <a href="#" @click.prevent>联系我们</a>
          <a href="#" @click.prevent>服务条款</a>
        </div>
        <div class="contact-info">
          <span>客服邮箱: support@xuehui.com</span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

const currentDate = new Date()
const currentYear = computed(() => currentDate.getFullYear())
</script>

<style scoped>
.pc-footer {
  background-color: #27423a;
  color: #d1d5db;
  padding: 25px 0;
  width: 100%;
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-sizing: border-box;
}

.footer-left,
.footer-right {
  display: flex;
  align-items: center;
}

.footer-left p {
  margin: 0;
  color: #e8f5e9;
  font-size: 14px;
}

.footer-links {
  display: flex;
  margin-right: 30px;
}

.footer-links a {
  color: #e8f5e9;
  font-size: 14px;
  text-decoration: none;
  margin: 0 12px;
  transition: color 0.3s;
  white-space: nowrap;
}

.footer-links a:hover {
  color: #b2ff59;
}

.contact-info {
  font-size: 13px;
  color: #a5d6a7;
}
</style>