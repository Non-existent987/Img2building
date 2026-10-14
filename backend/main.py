"""Img2Building 后端服务。

接口：
  GET  /api/health          健康检查与模型状态
  POST /api/detect          按 bbox 或 point 识别，返回 GeoJSON 矢量
  POST /api/export          把 GeoJSON 导出为 Shapefile(zip)
  GET  /                    前端静态页面（若已构建）
"""

import pathlib
from typing import List, Optional

import numpy as np
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import model as M
import tiles
import vectorize as V

app = FastAPI(title="Img2Building API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
FRONTEND_DIST = ROOT / "frontend" / "vue_project" / "dist"

_session = requests.Session()


class DetectReq(BaseModel):
    bbox: Optional[List[float]] = Field(None, description="[minlon,minlat,maxlon,maxlat]")
    lon: Optional[float] = None
    lat: Optional[float] = None
    zoom: int = Field(19, ge=10, le=21)
    pixel_size: float = Field(0.3, gt=0, le=5, description="每像素地面分辨率(米)")
    simplify: float = Field(1.5, ge=0, le=10)
    min_area: float = Field(12.0, ge=0)
    return_prob: bool = False


class ExportReq(BaseModel):
    geojson: dict
    epsg: int = 3857


@app.get("/api/health")
def health():
    ready = M.model_ready()
    return {
        "status": "ok",
        "model_loaded": ready,
        "device": M.device(),
        "model_path": M.MODEL_PATH,
    }


@app.post("/api/detect")
def detect(req: DetectReq):
    if not M.model_ready():
        raise HTTPException(503, "模型未就绪，请检查权重文件是否已放置")

    if req.bbox:
        bbox = tuple(req.bbox)
    elif req.lon is not None and req.lat is not None:
        # 点选：以该点为中心取一块小区域
        d = 0.0004
        bbox = (req.lon - d, req.lat - d, req.lon + d, req.lat + d)
    else:
        raise HTTPException(400, "需要提供 bbox 或 lon/lat")

    img, origin, ppd = tiles.fetch_region(bbox, req.zoom, _session)
    if img is None:
        raise HTTPException(502, "瓦片服务无响应，请稍后重试")

    tile = np.asarray(img)
    mask = M.predict_mask(tile)
    polys = V.mask_to_polygons(mask, simplify=req.simplify, min_area=req.min_area)
    gj = V.polygons_to_geojson(polys, pixel_size=req.pixel_size)

    # 平面坐标 -> WGS84经纬度，便于前端直接绘制
    _reproject_geojson(gj, origin, ppd, req.zoom)

    out = {
        "count": len(polys),
        "geojson": gj,
        "origin": {"lon": origin[0], "lat": origin[1]},
        "image_size": {"w": img.width, "h": img.height},
    }

    if req.return_prob:
        prob = M.prob_map(tile)
        out["prob"] = prob.astype(float).tolist()

    return JSONResponse(out)


@app.post("/api/export")
def export(req: ExportReq):
    if not req.geojson.get("features"):
        raise HTTPException(400, "没有可导出的矢量结果")

    # 导出为平面坐标系，避免经纬度直接写shp
    from pyproj import Transformer
    tr = Transformer.from_crs("EPSG:4326", f"EPSG:{req.epsg}", always_xy=True)
    planar = {"type": "FeatureCollection", "features": []}
    for f in req.geojson["features"]:
        g = f.get("geometry")
        if not g:
            continue
        rings = g["coordinates"]
        new_rings = []
        for ring in rings:
            xs, ys = zip(*ring)
            tx, ty = tr.transform(xs, ys)
            new_rings.append([[a, b] for a, b in zip(tx, ty)])
        planar["features"].append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": new_rings},
            "properties": f.get("properties", {}),
        })

    data = V.export_shapefile(planar, req.epsg)
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=buildings_shp.zip"},
    )


def _reproject_geojson(gj: dict, origin, ppd: float, zoom: int):
    """把 Web Mercator 平面坐标转回 WGS84 经纬度，原地写回 geojson。"""
    from pyproj import Transformer
    tr = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

    for f in gj["features"]:
        rings = f["geometry"]["coordinates"]
        converted = []
        for ring in rings:
            xs, ys = zip(*ring)
            lons, lats = tr.transform(xs, ys)
            converted.append([[a, b] for a, b in zip(lons, lats)])
        f["geometry"]["coordinates"] = converted


# 托管已构建的前端
if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/")
    def index():
        return FileResponse(FRONTEND_DIST / "index.html")