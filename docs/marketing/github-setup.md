# GitHub Topics 标签建议

仓库标签直接影响 **GitHub 站内搜索和 Explore 推荐的曝光**。Settings → Topics 里最多填 20 个，建议如下 15 个（填满，字符数上限 20/个）：

```
remote-sensing
building-extraction
semantic-segmentation
deep-learning
pytorch
computer-vision
gis
shapefile
geospatial
satellite-imagery
vue3
fastapi
leaflet
instance-segmentation
open-source
```

建议删除的（无搜索价值，纯占位）：

```
vue          # 太泛，vue3 已有
typescript   # 无人在 GitHub 按这个搜
```

## 设置方法

GitHub 网页端：
`仓库 → Settings → 侧栏 Topics → 输入标签并回车确认 → Save`

或命令行：

```bash
gh repo edit Non-existent987/Img2building --add-topic remote-sensing --add-topic building-extraction --add-topic deep-learning
```

---

# 一键社交卡片配置

仓库的 Social Preview（GitHub 生成的预览图）默认是灰色占位图，在 X / 微信 / 掘金转发时非常不吸引点击。

保存下方内容为 `docs/social-preview.svg`，上传到 https://img.shields.io/ 后取生成的 SVG URL，然后在
`仓库 → Settings → General → Social preview` 粘贴该 URL。

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0b1b2b"/>
      <stop offset="100%" stop-color="#123047"/>
    </linearGradient>
  </defs>
  <rect width="1280" height="640" fill="url(#bg)"/>

  <g fill="none" stroke="#1d5c8a" stroke-width="2" opacity="0.55">
    <rect x="700" y="120" width="180" height="110"/>
    <rect x="910" y="150" width="150" height="90"/>
    <rect x="760" y="290" width="130" height="100"/>
    <rect x="930" y="300" width="170" height="120"/>
    <rect x="700" y="450" width="190" height="95"/>
    <rect x="920" y="460" width="120" height="85"/>
  </g>

  <g fill="none" stroke="#3da9f0" stroke-width="3.5">
    <rect x="700" y="120" width="180" height="110"/>
    <rect x="760" y="290" width="130" height="100"/>
    <rect x="930" y="300" width="170" height="120"/>
  </g>

  <text x="90" y="250" font-family="Segoe UI, Roboto, sans-serif" font-size="82" font-weight="700" fill="#ffffff">Img2Building</text>
  <text x="92" y="320" font-family="Segoe UI, Roboto, sans-serif" font-size="30" fill="#9fc3dc">卫星影像建筑物智能识别与 GIS 导出</text>

  <g font-family="Segoe UI, Roboto, sans-serif" font-size="25" fill="#c8dced">
    <rect x="90" y="380" width="150" height="48" rx="24" fill="#164a70"/>
    <text x="165" y="411" text-anchor="middle">Vue 3</text>
    <rect x="256" y="380" width="150" height="48" rx="24" fill="#164a70"/>
    <text x="331" y="411" text-anchor="middle">FastAPI</text>
    <rect x="422" y="380" width="170" height="48" rx="24" fill="#164a70"/>
    <text x="507" y="411" text-anchor="middle">PyTorch</text>
    <rect x="608" y="380" width="170" height="48" rx="24" fill="#164a70"/>
    <text x="693" y="411" text-anchor="middle">Leaflet</text>
  </g>

  <text x="90" y="510" font-family="Segoe UI, Roboto, sans-serif" font-size="28" fill="#6fa8cc">框选即得 · 一键导出 SHP · 开源 MIT</text>
</svg>
```