// src/composables/useMap.ts
// 封装地图交互逻辑：底图切换、框选绘制、识别结果渲染
import { onMounted, ref, shallowRef } from 'vue';
import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: iconRetina,
  iconUrl: icon,
  shadowUrl: iconShadow,
});

const BASEMAPS = {
  satellite: {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles © Esri',
  },
  street: {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '© OpenStreetMap contributors',
  },
};

export function useMap(
  mapId: string,
  center: [number, number] = [30.5853, 114.29],
  zoom: number = 18,
) {
  const map = shallowRef<L.Map | null>(null);
  const basemap = ref<keyof typeof BASEMAPS>('satellite');
  const mode = ref<'point' | 'box'>('point');

  // 各图层引用
  let tileLayer: L.TileLayer | null = null;
  let boxRect: L.Rectangle | null = null;
  let resultLayer: L.LayerGroup | null = null;

  onMounted(() => {
    map.value = L.map(mapId).setView(center, zoom);
    tileLayer = L.tileLayer(BASEMAPS[basemap.value].url, {
      attribution: BASEMAPS[basemap.value].attribution,
    }).addTo(map.value);
  });

  /** 切换底图 */
  function setBasemap(key: keyof typeof BASEMAPS) {
    if (!map.value || !tileLayer) return;
    basemap.value = key;
    map.value.removeLayer(tileLayer);
    tileLayer = L.tileLayer(BASEMAPS[key].url, {
      attribution: BASEMAPS[key].attribution,
    }).addTo(map.value);
    tileLayer.bringToBack();
  }

  /** 切换选择模式 */
  function setMode(m: 'point' | 'box') {
    mode.value = m;
    clearSelection();
  }

  /** 清除当前选区与结果 */
  function clearSelection() {
    if (boxRect && map.value) {
      map.value.removeLayer(boxRect);
      boxRect = null;
    }
  }

  function clearResult() {
    if (resultLayer && map.value) {
      map.value.removeLayer(resultLayer);
      resultLayer = null;
    }
  }

  /** 绘制一个矩形选区，corners 为 [[lat,lng],[lat,lng]] */
  function drawBox(corners: [[number, number], [number, number]]) {
    if (!map.value || !corners) return;
    clearSelection();
    boxRect = L.rectangle(L.latLngBounds(corners[0], corners[1]), {
      color: '#3da9f0',
      weight: 2,
      fillColor: '#3da9f0',
      fillOpacity: 0.12,
      dashArray: '6,4',
    }).addTo(map.value);
  }

  /** 取当前选区 bbox=[minlon,minlat,maxlon,maxlat]；无选区返回 null */
  function getBox(): [number, number, number, number] | null {
    if (!boxRect || !map.value) return null;
    const b = boxRect.getBounds();
    return [b.getWest(), b.getSouth(), b.getEast(), b.getNorth()];
  }

  /** 在指定坐标放置标记 */
  function placeMarker(lat: number, lon: number) {
    if (!map.value) return;
    clearSelection();
    L.circleMarker([lat, lon], {
      radius: 7,
      color: '#ffd166',
      weight: 2,
      fillColor: '#ffd166',
      fillOpacity: 0.85,
    }).addTo(map.value);
  }

  /** 渲染 GeoJSON 建筑轮廓 */
  function renderResult(geojson: any) {
    if (!map.value) return;
    clearResult();
    resultLayer = L.geoJSON(geojson, {
      style: {
        color: '#3da9f0',
        weight: 2,
        fillColor: '#3da9f0',
        fillOpacity: 0.25,
      },
      onEachFeature: (f, lyr) => {
        const area = f?.properties?.area;
        if (area != null) {
          lyr.bindTooltip(`${area} m²`, { sticky: true });
        }
      },
    }).addTo(map.value);
  }

  /** 跳转到坐标 */
  function flyTo(lat: number, lon: number, z = 19) {
    map.value?.flyTo([lat, lon], z, { duration: 0.8 });
  }

  return {
    map,
    basemap,
    mode,
    setBasemap,
    setMode,
    drawBox,
    getBox,
    placeMarker,
    renderResult,
    flyTo,
    clearResult,
    clearSelection,
  };
}