<template>
  <div class="map-container">
    <!-- 左侧控制面板 -->
    <div class="sidebar">
      <!-- 控制按钮、输入框等 -->
      <div class="controls">
        <h2>建筑物智能提取</h2>
        <div class="mode-switch">
          <button @click="switchMode('point')">点选模式</button>
          <button @click="switchMode('rectangle')">框选模式</button>
        </div>
        <!-- 其他控件 -->
        <div class="map-controls">
          <label>切换底图</label>
          <select v-model="basemap">
            <option value="satellite">卫星图</option>
            <option value="street">街道图</option>
          </select>
        </div>
        <!-- ... existing code ... -->
      </div>
    </div>

    <!-- 地图区域 -->
    <div class="map-view">
      <l-map :zoom="zoom" :center="center" style="height: 100%; width: 100%;">
        <l-tile-layer :url="tileUrl" />
        <!-- 其他图层 -->
      </l-map>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.map-container {
  display: flex;
  height: 100vh;
  /* 确保无额外 padding 导致布局错乱 */
  padding: 0;
}

.sidebar {
  width: 250px; /* 固定宽度 */
  background-color: #f0f2f5;
  padding: 20px;
  box-sizing: border-box;
}

.map-view {
  flex: 1; /* 占据剩余空间 */
  overflow: hidden;
  /* 确保地图填满剩余宽度 */
}
</style>