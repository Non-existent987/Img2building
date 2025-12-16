<script setup>
import HelloWorld from './components/HelloWorld.vue';
import axios from 'axios';
import { ref, onMounted } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// 数据属性被转换为引用
const backendMessage = ref(''); // 用于存储从后端获取的消息
const errorMessage = ref('');  // 用于存储请求错误信息

// 方法被转换为函数
const fetchData = async () => {
  // 清空之前的消息和错误
  backendMessage.value = '正在加载中......';
  errorMessage.value = '';
  try {
    // 发起 get 请求到后端
    const response = await axios.get('http://localhost:8000/hello/');
    backendMessage.value = response.data.message;
    console.log('获取数据成功：');
  } catch (error) {
    console.error('获取数据失败：', error);
    backendMessage.value = '获取数据失败。';
    if (error.response) {
      errorMessage.value = `服务器错误: ${error.response.status} - ${error.response.data?.message || error.response.statusText}`;
    } else if (error.request) {
      errorMessage.value = '网络错误: 未收到服务器响应。请检查后端是否运行或网络连接。';
    } else {
      errorMessage.value = `请求配置错误: ${error.message}`;
    }
  }
};

// 在 onMounted 钩子中初始化地图
let map = null;
onMounted(() => {
  // 使用 setTimeout 确保 DOM 渲染完成
  setTimeout(() => {
    if (L && document.getElementById('mapid')) { // 确保 L 已加载且容器存在
      // 初始化地图
      map = L.map('mapid', {
        zoomControl: false,// 不显示默认缩放控件
        maxZoom: 22// 最大缩放级别
      }).setView([30.585774, 114.288390], 18);
      // 添加 Esri 卫星影像图层
      const Esri_WorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 22,
        attribution: 'Tiles &copy; Esri'// Esri 版权信息
      });

      Esri_WorldImagery.addTo(map);

      // 再次强制刷新地图尺寸，这是最关键的修复
      map.invalidateSize();
      // ----添加地图点击获取经纬度-开始
      map.on('click', function(e) {
        const lat = e.latlng.lat.toFixed(8);
        const lng = e.latlng.lng.toFixed(8);
        L.popup()
        .setLatLng(e.latlng) // 设置弹出框位置
        .setContent(`经度：${lng}<br>纬度：${lat}`) // 设置弹出框内容
        .openOn(map);// 打开弹出框

        requestImageDownload(lng, lat);

      });// ----添加地图点击获取经纬度-结束

      // map.on('click',...) 函数外部，添加一个新的辅助函数 ---
      const requestImageDownload = async (lng, lat) => {
        try {
          console.log("请求图片下载，坐标：", lng, lat);
          // 这里可以添加实际的请求逻辑，例如调用后端API
          const response = await axios.post('http://localhost:8000/download_image/', {
            lng: lng,
            lat: lat
            
          });
          console.log('后端响应', response.data);
          alert('后端已开始下载图片！');
        } catch (error) {
          console.error('请求图片下载失败：', error);
          alert('请求图片下载失败，请检查控制台错误信息。');
        }
      };

    } else {
      console.error('Leaflet (L) or map container not found!');
    }
  }, 100); // 100ms 延迟通常足够
});
</script>

<template>
  <!--跟容器 -->
  <div class="app">
    <!-- 侧边栏内容，后续补充 -->
    <div class="sidebar">
      <h2>建筑物智能提取</h2>
      <p>切换模式</p>
      <div class="sidebar-buttons">
        
        <button class="sidebar-button-point">点选模式</button>
        <button class="sidebar-button-rectangle">框选模式</button>
      </div>
      <div class="sidebar-dropdown">
        <p>切换底图:</p>
        <select class="basemap-select">
          <option value="satellite" selected>卫星图</option>
          <option value="street">街道图</option>
        </select>
        <p>选择模型:</p>
        <select class="basemap-select">
          <option value="one" selected>建筑物识别模型1.0</option>
          <option value="two">建筑物识别模型2.0</option>
        </select>
        <p>经度:</p>
        <input class="basemap-select" type="text" placeholder="请输入经度">
        <p>纬度:</p>
        <input class="basemap-select" type="text" placeholder="请输入纬度">
        <button>定位到经纬度</button>
        <button>显示/隐藏图片</button>
        <button>清除识别</button>
        <button>编辑建筑物</button>
        <button>添加标记点</button>
        <button>导出结果shp</button>
      </div>

      <!-- 测试下按钮和后端联系：开始 -->
      <button @click="fetchData">点我测试</button>
      <p v-if="backendMessage">
        <strong>后端消息:</strong> {{ backendMessage }}
      </p>
      <p v-if="errorMessage" style="color:red;">
        <strong>错误信息:</strong> {{ errorMessage }}
      </p>
      <!-- 测试下按钮和后端联系：结束 -->
    </div>
    <!-- 主显示区域 -->
    <div class="main-content" >
      <!-- 这里可以放置地图组件或其他内容 -->
      <!-- <h2>主显示区域</h2> -->

      <!-- 地图容器 -->
      <div id="mapid" class="map-container"></div>

    </div>

  </div>

</template>

<style scoped>
/* 重置基础样式 */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden; /* 防止滚动条占用空间 */
}
app {
  display: flex;
  height: 100vh;
  position: relative; /* 添加定位上下文 */
}
.sidebar{
  width: 320px; 
  background-color: #fff; 
  box-shadow:0 0 15px rgba(0,0,0,0.1); 
  position: fixed; /* 如果想要固定侧边栏 */
  padding:20px;
  z-index:1000;
  left: 0;
  top: 0;
  height: 100vh;
  overflow-y: auto; /* 内容过多时可滚动 */
  text-align: left;
}
.sidebar-buttons {
  display: flex;
  border: 1px solid #0959c2;
  border-radius: 10px;
  overflow: hidden;
}
.sidebar-button-point {
  flex: 1; 
  border: none; 
  padding: 10px; 
  border-right: 1px solid #0959c2; 
  border-radius: 10px 0 0 10px; 
  background-color: #ffffff;
  color: #0959c2;
}
.sidebar-button-rectangle {
  flex: 1; 
  border: none; 
  padding: 10px; 
  border-radius: 0 10px 10px 0; 
  background-color: #ffffff;
  color: #0959c2;
}
.basemap-select {
  width: 100%;
  height: 40px;
  font-size: 16px;
  padding: 5px;
  border-radius: 5px;
  border: 1px solid #ccc;
}
.map-container {
  /* 关键修改：绝对定位占满父元素 */
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 1px solid #ccc;
  box-sizing: border-box;
}

/* 确保父元素（.main-content）是定位容器 */
.main-content {
  position: relative; 
  margin-left: 320px; /* 关键：为侧边栏留出空间 */
  height: 100vh;
  flex-grow: 1; /* 占据剩余空间 */
}
</style>
