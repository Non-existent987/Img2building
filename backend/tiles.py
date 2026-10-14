"""按经纬度范围抓取卫星影像瓦片并拼接。

数据源走ArcGIS World Imagery 公开瓦片服务，无需 API key。
"""

import io
import math

import requests
from PIL import Image

TILE_URL = "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
MAX_TILES = 64          # 单次请求最多瓦片数，防止误拉爆内存
TIMEOUT = 15


def lonlat_to_tile(lon: float, lat: float, z: int):
    """经纬度 -> 瓦片号"""
    n = 2 ** z
    xt = int((lon + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    yt = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xt, yt


def tile_to_lonlat(xt: int, yt: int, z: int):
    """瓦片号 -> 经纬度（左上角）"""
    n = 2 ** z
    lon = xt / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * yt / n)))
    return lon, math.degrees(lat_rad)


def fetch_tile(x: int, y: int, z: int, session=None) -> Image.Image | None:
    url = TILE_URL.format(z=z, y=y, x=x)
    try:
        s = session or requests
        r = s.get(url, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        return Image.open(io.BytesIO(r.content)).convert("RGB")
    except Exception:
        return None


def fetch_region(bbox, zoom: int = 19, session=None):
    """按 bbox=(minlon, minlat, maxlon, maxlat) 取影像。

    返回 (PIL.Image, origin_lonlat, pixels_per_degree_lon)
    """
    import numpy as np

    minlon, minlat, maxlon, maxlat = bbox
    s = session or requests

    x0, y0 = lonlat_to_tile(minlon, maxlat, zoom)
    x1, y1 = lonlat_to_tile(maxlon, minlat, zoom)

    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)

    cols, rows = x1 - x0 + 1, y1 - y0 + 1
    if cols * rows > MAX_TILES:
        # 瓦片过多时降一级分辨率
        zoom -= 1
        x0, y0 = lonlat_to_tile(minlon, maxlat, zoom)
        x1, y1 = lonlat_to_tile(maxlon, minlat, zoom)
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        cols, rows = x1 - x0 + 1, y1 - y0 + 1

    tile_size = 256
    canvas = Image.new("RGB", (cols * tile_size, rows * tile_size))

    filled = 0
    for dy in range(rows):
        for dx in range(cols):
            t = fetch_tile(x0 + dx, y0 + dy, zoom, s)
            if t is not None:
                canvas.paste(t, (dx * tile_size, dy * tile_size))
                filled += 1

    if filled == 0:
        return None, None, None

    origin = tile_to_lonlat(x0, y0, zoom)
    ppd_lon = 360.0 / (2 ** zoom * tile_size)   # 每像素经度跨度
    return canvas, origin, ppd_lon