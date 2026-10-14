// src/api.ts
// 后端接口封装。同源部署时留空即可；跨域时用 VITE_API_BASE 指定后端地址。

const BASE = import.meta.env.VITE_API_BASE || '';

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    let msg = `请求失败 (${res.status})`;
    try {
      const j = await res.json();
      if (j?.detail) msg = j.detail;
    } catch { /* 响应非 JSON，沿用默认文案 */ }
    throw new Error(msg);
  }
  return res.json();
}

export interface DetectResult {
  count: number;
  geojson: any;
  origin: { lon: number; lat: number };
  image_size: { w: number; h: number };
}

export function detectApi(payload: {
  bbox?: [number, number, number, number];
  lon?: number;
  lat?: number;
  zoom?: number;
  pixel_size?: number;
}) {
  return post<DetectResult>('/api/detect', payload);
}

export async function exportShpApi(geojson: any) {
  const res = await fetch(`${BASE}/api/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ geojson, epsg: 3857 }),
  });

  if (!res.ok) {
    let msg = `导出失败 (${res.status})`;
    try {
      const j = await res.json();
      if (j?.detail) msg = j.detail;
    } catch { /* 同上 */ }
    throw new Error(msg);
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'buildings_shp.zip';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function healthApi() {
  const res = await fetch(`${BASE}/api/health`);
  return res.json();
}