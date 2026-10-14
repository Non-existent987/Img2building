// src/composables/useMap.ts
// 这是一个Vue 3组合式函数(Composable)，用于封装地图相关的逻辑
// 组合式函数是Vue 3中将相关功能逻辑组织在一起的最佳实践

// 从Vue库导入onMounted生命周期钩子
// onMounted: 在组件挂载到DOM后执行，此时可以安全地访问DOM元素
// 这是关键：必须在DOM元素渲染后才能初始化地图
import { onMounted } from 'vue';

// 导入Leaflet库，这是一个用于交互式地图的JavaScript库
// L是Leaflet库的默认导出对象，包含所有Leaflet功能
import * as L from 'leaflet';

// 导入Leaflet的CSS样式文件
// 这是必需的，因为Leaflet的地图需要特定的样式才能正确显示
import 'leaflet/dist/leaflet.css';

// 导入Leaflet的默认图标资源文件
// 这是为了解决构建后图标路径问题
// 在构建过程中，静态资源路径可能会改变，需要显式导入
import icon from 'leaflet/dist/images/marker-icon.png';        // 普通分辨率图标
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png'; // 高分辨率图标
import iconShadow from 'leaflet/dist/images/marker-shadow.png';   // 图标阴影

// 修复Leaflet图标路径问题的关键代码
// 问题说明：Leaflet默认使用相对路径加载图标，但在构建后这些路径可能失效
// 解决方案：手动设置图标路径
// 1. 删除_getIconUrl方法以避免默认路径干扰
// (L.Icon.Default.prototype as any) 将类型转换为any以避免TypeScript类型检查错误
delete (L.Icon.Default.prototype as any)._getIconUrl;

// 2. 使用mergeOptions方法重新设置图标路径
L.Icon.Default.mergeOptions({
  // iconRetinaUrl: 高分辨率设备的图标路径
  iconRetinaUrl: iconRetina,
  // iconUrl: 普通设备的图标路径
  iconUrl: icon,
  // shadowUrl: 图标的阴影路径
  shadowUrl: iconShadow,
});

/**
 * 自定义组合式函数useMap
 * 
 * 组合式函数(Composable)是Vue 3 Composition API的最佳实践
 * 优点：
 * - 逻辑复用：可以在多个组件中使用相同的功能
 * - 代码组织：将相关功能组织在一起
 * - 类型安全：提供更好的TypeScript支持
 * 
 * @param mapId - 地图容器的DOM元素ID（必须与模板中div的id一致）
 * @param center - 地图中心点坐标，默认为北京坐标 [纬度, 经度]
 * @param zoom - 地图缩放级别，默认为10
 * @returns 包含地图实例的对象
 */
export function useMap(mapId: string, center: [number, number] = [39.9042, 116.4074], zoom: number = 18) {
  // 声明一个变量来存储地图实例，初始值为null
  // L.Map | null: TypeScript类型注解，表示变量可以是L.Map类型或null
  let map: L.Map | null = null;

  // 在组件挂载后执行地图初始化
  // 这是关键：必须在DOM元素渲染后才能初始化地图
  // onMounted钩子确保在DOM元素存在后执行地图初始化代码
  onMounted(() => {
    // 初始化地图
    // L.map(mapId) - 创建地图实例，参数是DOM元素的ID
    // setView([lat, lng], zoom) - 设置地图中心点和缩放级别
    // [lat, lng]是坐标数组，第一个是纬度，第二个是经度
    map = L.map(mapId).setView(center, zoom);

    // 添加瓦片图层（地图底图）
    // 使用ESRI World Imagery作为底图，这是一个高质量的卫星影像服务
    // URL模板：{z}表示缩放级别，{y}和{x}表示瓦片坐标
    // 这些大写字母变量会被Leaflet自动替换为实际值
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      // attribution: 版权信息，显示在地图底部，用于说明数据来源
      attribution: 'Tiles © Esri'
    })
    // 将图层添加到地图实例中
    .addTo(map);
  });

  // 返回地图实例，以便在需要时进行进一步操作
  // 这样调用此函数的组件可以访问地图实例
  return { map };
}

// 需要学习的关键知识点：
// 
// 1. Vue 3组合式API (Composition API):
//    - onMounted: 组件生命周期钩子，在组件挂载后执行
//    - 组合式函数: 将相关逻辑封装在一起的函数，便于复用
// 
// 2. Leaflet地图库:
//    - L.map(): 创建地图实例
//    - setView(): 设置地图中心点和缩放级别
//    - L.tileLayer(): 添加瓦片图层（地图底图）
//    - addTo(): 将图层添加到地图实例
// 
// 3. TypeScript类型注解:
//    - [number, number]: 元组类型，表示包含两个数字的数组
//    - L.Map | null: 联合类型，表示变量可以是L.Map或null
// 
// 4. 地图坐标系统:
//    - [纬度, 经度]: Leaflet使用[纬度, 经度]顺序，不同于常见的[经度, 纬度]
//    - 缩放级别: 数值越大表示缩放级别越高（地图越详细）
// 
// 5. 构建和资源路径:
//    - 静态资源导入: 使用import导入图片等资源
//    - 构建后路径问题: 构建工具会处理资源路径，需要显式导入