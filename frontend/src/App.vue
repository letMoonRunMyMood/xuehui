<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
// 导入全局样式和配置
import 'element-plus/dist/index.css'
import './assets/main.css'
</script>

<style>
/* 全局样式重置：保证视口高度生效 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  box-sizing: border-box;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 0;
  height: 100%; /* 关键：根容器占满视口高度 */
  width: 100%;
  box-sizing: border-box;
}

/* 继承盒模型：避免布局错乱 */
* {
  box-sizing: inherit;
}
</style>