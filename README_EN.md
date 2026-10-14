<div align="center">

# Img2Building

**Deep-learning building extraction from satellite imagery, exported as GIS vectors**

Draw a box. Get building outlines. Export to Shapefile.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.3-42b883?style=flat-square&logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-ee4c2c?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-2ea44f?style=flat-square)](LICENSE)

English | [简体中文](README.md)

</div>

---

## What it does

Draw a rectangle or click a point on the satellite basemap. A deep learning model extracts building footprints inside that region and exports them as **Shapefile (SHP)** — load them straight into QGIS or ArcGIS.

No manual digitizing, no paid API. The output drops into your existing GIS workflow.

![Demo](docs/images/demo.jpg)

> Point click + coordinate jump (114.29, 30.59). Blue polygons are auto-extracted building footprints.

## Features

| Capability | Description |
|---|---|
| Box selection | Drag a rectangle, extract every building inside it |
| Point selection | Click a single coordinate, extract that building |
| Coordinate jump | Enter lat/lon directly — built for batch coordinate lists |
| Vector export | SHP output with a complete GIS attribute schema |
| Manual editing | Correct false negatives and false positives by hand |
| Multiple basemaps | Switch between satellite imagery and street map |

## Tech stack

**Frontend** Vue 3 + TypeScript + Vite 4 + Leaflet 1.9
**Backend** FastAPI + PyTorch
**Dataset** 8,000+ self-collected satellite images with annotations

## Project status

| Module | State |
|---|---|
| Map interaction & UI | Working |
| Building detection | Working (EfficientNet-B4 Unet, 20.2M params) |
| Backend API | Working (FastAPI) |
| Shapefile export | Working |
| Manual result editing | In development |

Trained on a self-collected dataset (8,000+ annotated images). **Results require human verification.**

## Quick start

### Backend (required)

```bash
cd backend
pip install -r requirements.txt

# place weights at frontend/model/Identification_model_file/ (see below)

uvicorn main:app --reload
# open http://127.0.0.1:8000
```

The server auto-serves the built frontend, so that URL is the full application.

### Frontend (development)

```bash
cd frontend/vue_project
npm install
npm run dev
```

The frontend talks to the same-origin backend by default. For a separately hosted API:

```bash
# .env.local
VITE_API_BASE=https://your-api-domain.com
```

### Model weights

`img2building_model.pth` (~226MB) is **not distributed with the repo** — it exceeds GitHub's 100MB hard per-file limit, and Git LFS on the free tier only includes 10GB/month of bandwidth, which a public project exhausts quickly and then breaks downloads for everyone.

Mirror links will be added here once published (ModelScope / Hugging Face).

Drop the file into `frontend/model/Identification_model_file/`. The backend auto-detects it at startup.

## API

| Endpoint | Description |
|---|---|
| `GET /api/health` | Health check, model status and device |
| `POST /api/detect` | Detect by `bbox` (box) or `lon`/`lat` (point), returns GeoJSON |
| `POST /api/export` | GeoJSON to Shapefile, returns zip |

Example `/api/detect` request:

```json
{
  "bbox": [114.285, 30.583, 114.290, 30.588],
  "zoom": 19,
  "pixel_size": 0.3
}
```

## Deployment

Frontend and backend ship together — `uvicorn main:app` gives you the whole application.

Static-only hosting of `dist/` works for the UI but detection needs the backend:

- **Cloudflare Pages** (recommended)
- **Vercel** / **Netlify**
- **EdgeOne Pages**

Full inference deployment needs a GPU. Hourly-billed GPU hosts (AutoDL, Alibaba Cloud PAI) are the practical option.

## Contributing

Issues and PRs welcome — especially on detection accuracy, regional adaptation, and domain-specific tuning.

## License

[MIT](LICENSE)