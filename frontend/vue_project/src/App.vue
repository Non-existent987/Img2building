<template>
  <!-- 根元素，所有Vue组件都需要一个根元素 -->
  <div id="app">
    <!-- 容器元素，使用flexbox布局将页面分为左右两部分 -->
    <div class="container">
      <!-- 左侧面板，用于放置控制按钮和选项 -->
      <div class="left-pane">
        <div>
          <!-- 标题：建筑物智能提取 -->
          <h2>建筑物智能提取</h2>
          <p>切换模式</p>
          <!-- 模式切换按钮：点选模式 -->
          <button>点选模式</button>
          <!-- 模式切换按钮：框选模式 -->
          <button>框选模式</button>
          <p>切换底图</p>
          <!-- 底图选择下拉菜单 -->
          <select name="卫星图" id="">
            <option value="">卫星图</option>
            <option value="">街道图</option>
          </select>
          <p>选择模型</p>
          <!-- 模型选择下拉菜单 -->
          <select name="模型" id="">
            <option value="">模型1</option>
            <option value="">模型2</option>
          </select>
          <p>经度</p>
          <!-- 经度输入框 -->
          <input type="float"></input>
          <p>纬度</p>
          <!-- 纬度输入框 -->
          <input type="float"></input>
          <!-- 定位按钮 -->
          <button>定位到经纬度</button>
          <!-- 显示/隐藏图片按钮 -->
          <button>显示/隐藏图片</button>
          <!-- 清除识别按钮 -->
          <button>清除识别</button>
          <!-- 编辑建筑物按钮 -->
          <button>编辑建筑物</button>
          <!-- 添加标记点按钮 -->
          <button>添加标记点</button>
          <!-- 导出shp文件按钮 -->
          <button>导出shp</button>
        </div>
      </div>
      <!-- 右侧面板，用于显示地图 -->
      <div class="right-pane">
        <!-- 右侧内容标题 -->
        <!-- <h2>右侧页面</h2> -->
        <!-- 地图容器元素：这是Leaflet地图的容器，必须有唯一的id -->
        <!-- id="map"：这是关键，useMap函数会使用这个ID来初始化地图 -->
        <div id="map"></div>
      </div>
    </div>
  </div>
</template>

<!-- Vue 3的组合式API语法，使用setup关键字 -->
<script setup lang="ts">
// 从Vue库导入onMounted生命周期钩子
// onMounted: 在组件挂载到DOM后执行，此时可以安全地访问DOM元素
// 这是关键：必须在DOM元素渲染后才能初始化地图

// 导入自定义的组合式函数useMap
// 组合式函数(Composable)是Vue 3中封装可复用逻辑的最佳实践
// useMap函数封装了Leaflet地图初始化的逻辑，使代码更模块化
import { useMap } from './composables/useMap';

// 调用useMap函数，传入地图容器的ID 'map'
// 这会初始化Leaflet地图，并将其渲染到ID为'map'的div元素中
// useMap函数内部使用onMounted钩子确保在DOM渲染后执行
useMap('map');
</script>

<style scoped>
/* scoped: 表示这些CSS样式只应用于当前组件，不会影响其他组件 */
/* 这有助于避免样式冲突 */

/* #app: 选择ID为app的元素 */
#app {
  /* font-family: 设置字体族，定义文本的字体 */
  font-family: Avenir, Helvetica, Arial, sans-serif;
  /* -webkit-font-smoothing: 抗锯齿，使字体在Webkit浏览器中更平滑 */
  -webkit-font-smoothing: antialiased;
  /* -moz-osx-font-smoothing: 使字体在Mac OS X的Firefox浏览器中更平滑 */
  -moz-osx-font-smoothing: grayscale;
  /* text-align: 设置文本对齐方式为居中 */
  text-align: center;
  /* color: 设置文本颜色 */
  color: #2c3e50;
  /* 移除最大宽度限制，让应用占满整个视口宽度 */
  max-width: none;
  margin: 0;
  padding: 0;
}

/* .container: 选择class为container的元素 */
.container {
  /* display: flex: 使用弹性布局，使子元素可以灵活排列 */
  display: flex;
  /* height: 100vh: 设置高度为视口高度的100%，vh是viewport height的缩写 */
  height: 100vh;
  /* width: 100vw: 设置宽度为视口宽度的100%，避免内容限制在固定宽度内 */
  /* 这里100vw和100%的区别是，100vw是视口宽度的100%，而100%是父容器宽度的100%。使用100vw可以确保容器占满整个视口宽度，避免内容被限制在固定宽度内。 */
  width: 100vw;
  /* 移除可能的内边距 */
  padding: 0;
  margin: 0;
}

/* .left-pane: 选择class为left-pane的元素（左侧面板） */
.left-pane {
  /* flex: 0 0 300px: 设置固定宽度为300px，不放大，不缩小 */
  flex: 0 0 20%;
  /* background-color: 设置背景色 */
  background-color: #f0f0f0;
  /* padding: 设置内边距，元素内容与边框之间的距离 */
  padding: 20px;
  /* overflow-y: auto: 当内容垂直方向溢出时显示滚动条 */
  overflow-y: auto;
}

/* .right-pane: 选择class为right-pane的元素（右侧面板） */
.right-pane {
  /* flex: 1: 占据剩余的所有空间 */
  flex: 1;
  /* background-color: 设置背景色 */
  background-color: #ffffff;
  /* display: flex: 使用弹性布局 */
  display: flex;
  /* flex-direction: column: 设置弹性布局方向为垂直 */
  flex-direction: column;
  /* align-items: center: 水平居中对齐子元素 */
  align-items: stretch;
  /* 移除可能的内边距 */
  padding: 0;
  margin: 0;
}

/* #map: 选择ID为map的元素（地图容器） */
#map {
  /* width: 100%: 宽度占满父容器 */
  width: 100%;
  /* height: 100%: 高度占满父容器 */
  height: 100%;
  /* z-index: 设置元素的堆叠顺序，数值越大越靠前 */
  z-index: 1;
}
</style>