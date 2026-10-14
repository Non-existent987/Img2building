<template>
  <div class="container">
    <div class="left-pane">
      <h2>建筑物智能提取</h2>

      <div class="field">
        <label>切换模式</label>
        <div class="btn-group">
          <button :class="{ active: mode === 'point' }" @click="setMode('point')">点选模式</button>
          <button :class="{ active: mode === 'box' }" @click="setMode('box')">框选模式</button>
        </div>
      </div>

      <div class="field">
        <label>切换底图</label>
        <select v-model="basemapSel" @change="onBasemapChange">
          <option value="satellite">卫星图</option>
          <option value="street">街道图</option>
        </select>
      </div>

      <div class="field">
        <label>经度</label>
        <input v-model.number="lon" type="number" step="0.00001" />
      </div>

      <div class="field">
        <label>纬度</label>
        <input v-model.number="lat" type="number" step="0.00001" />
      </div>

      <button class="full" :disabled="busy" @click="locate">定位到经纬度</button>

      <div class="divider"></div>

      <button class="full primary" :disabled="busy || !canDetect" @click="detect">
        {{ busy ? '识别中…' : '开始识别' }}
      </button>

      <div class="btn-group mt">
        <button :disabled="!hasResult" @click="onClearResult">清除识别</button>
        <button :disabled="busy || !hasResult" @click="exportShp">导出 shp</button>
      </div>

      <div class="divider"></div>

      <div class="status">
        <div v-if="status" :class="['msg', statusKind]">{{ status }}</div>
        <div v-if="hasResult" class="result-info">
          识别到 <b>{{ buildingCount }}</b> 栋建筑
        </div>
      </div>
    </div>

    <div class="right-pane">
      <div id="map"></div>
      <div v-if="mode === 'box' && !hasBox" class="map-hint">
        在地图上按住左键拖动，框选要识别的区域
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useMap } from './composables/useMap';
import { detectApi, exportShpApi } from './api';

const {
  map, mode, setMode, setBasemap, drawBox, getBox, placeMarker,
  renderResult, flyTo, clearResult,
} = useMap('map');

const lon = ref(114.29);
const lat = ref(30.5853);
const basemapSel = ref<'satellite' | 'street'>('satellite');

const busy = ref(false);
const hasBox = ref(false);
const lastGeojson = ref<any>(null);
const status = ref('');
const statusKind = ref<'info' | 'ok' | 'err'>('info');

const buildingCount = computed(() => lastGeojson.value?.features?.length ?? 0);
const hasResult = computed(() => buildingCount.value > 0);
const canDetect = computed(() => (mode.value === 'box' ? hasBox.value : true));

function onBasemapChange() {
  setBasemap(basemapSel.value);
}

onMounted(() => {
  const m = map.value;
  if (!m) return;

  let dragging = false;
  let start: any = null;

  m.on('mousedown', (e: any) => {
    if (mode.value !== 'box') return;
    dragging = true;
    start = e.latlng;
  });

  m.on('mousemove', (e: any) => {
    if (!dragging || !start) return;
    drawBox([[start.lat, start.lng], [e.latlng.lat, e.latlng.lng]] as any);
  });

  m.on('mouseup', (e: any) => {
    if (!dragging || !start) return;
    dragging = false;

    // 拖动距离过小视为误点击
    const dh = Math.abs(e.latlng.lat - start.lat);
    const dw = Math.abs(e.latlng.lng - start.lng);
    if (dh < 1e-5 || dw < 1e-5) return;

    hasBox.value = true;
    status.value = '已框选区域，点击「开始识别」';
    statusKind.value = 'info';
  });
});

function locate() {
  if (lon.value == null || lat.value == null) return;
  flyTo(lat.value, lon.value, 19);
  placeMarker(lat.value, lon.value);
  status.value = `已定位到 ${lon.value}, ${lat.value}`;
  statusKind.value = 'ok';
}

async function detect() {
  busy.value = true;
  status.value = '正在推理…';
  statusKind.value = 'info';

  try {
    const payload: any = { zoom: 19 };
    if (mode.value === 'box') {
      const b = getBox();
      if (!b) {
        status.value = '请先框选区域';
        statusKind.value = 'err';
        return;
      }
      payload.bbox = b;
    } else {
      payload.lon = lon.value;
      payload.lat = lat.value;
    }

    const res = await detectApi(payload);
    lastGeojson.value = res.geojson;
    renderResult(res.geojson);

    const n = res.geojson.features.length;
    status.value = n ? `识别完成，共 ${n} 栋` : '该区域未识别到建筑，可放大或换个区域';
    statusKind.value = n ? 'ok' : 'info';
  } catch (e: any) {
    status.value = e?.message || '识别失败';
    statusKind.value = 'err';
  } finally {
    busy.value = false;
  }
}

function onClearResult() {
  clearResult();
  lastGeojson.value = null;
  status.value = '';
}

async function exportShp() {
  if (!lastGeojson.value) return;
  busy.value = true;
  try {
    await exportShpApi(lastGeojson.value);
    status.value = '已导出 buildings_shp.zip';
    statusKind.value = 'ok';
  } catch (e: any) {
    status.value = e?.message || '导出失败';
    statusKind.value = 'err';
  } finally {
    busy.value = false;
  }
}
</script>

<style scoped>
#app { margin: 0; height: 100vh; }

.container { display: flex; height: 100vh; }

.left-pane {
  flex: 0 0 300px;
  padding: 16px;
  background: #fafbfc;
  border-right: 1px solid #e3e6ea;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.left-pane h2 { margin: 0 0 4px; font-size: 17px; color: #1a2430; }

.field { display: flex; flex-direction: column; gap: 5px; }
.field label { font-size: 13px; color: #5a6672; }

input, select {
  padding: 7px 9px;
  border: 1px solid #ccd3da;
  border-radius: 6px;
  font-size: 13px;
  font-family: inherit;
  background: #fff;
}
input:focus, select:focus { outline: none; border-color: #3da9f0; }

button {
  padding: 8px 12px;
  border: 1px solid #ccd3da;
  border-radius: 6px;
  background: #fff;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  transition: background .15s, border-color .15s;
}
button:hover:not(:disabled) { background: #f0f4f8; }
button:disabled { opacity: .5; cursor: not-allowed; }
button.active { background: #3da9f0; border-color: #3da9f0; color: #fff; }
button.full { width: 100%; }
button.primary { background: #1a7fd4; border-color: #1a7fd4; color: #fff; font-weight: 500; }
button.primary:hover:not(:disabled) { background: #1668b4; }

.btn-group { display: flex; gap: 8px; }
.btn-group button { flex: 1; }
.mt { margin-top: 8px; }
.divider { height: 1px; background: #e3e6ea; margin: 4px 0; }

.right-pane { flex: 1; position: relative; }
#map { width: 100%; height: 100%; z-index: 1; }

.map-hint {
  position: absolute;
  top: 16px; left: 50%;
  transform: translateX(-50%);
  background: rgba(26,36,48,.88);
  color: #fff;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  pointer-events: none;
  z-index: 1000;
}

.status { font-size: 12.5px; line-height: 1.6; }
.msg.info { color: #5a6672; }
.msg.ok { color: #17803d; }
.msg.err { color: #c0392b; }
.result-info { color: #1a2430; margin-top: 4px; }
</style>