"""掩膜转矢量几何，并导出 Shapefile。

链路：二值掩膜 -> 形态学清理 -> 连通域 -> 轮廓简化 -> 多边形(带孔洞) -> SHP
"""

import io
import pathlib
import tempfile
import zipfile

import numpy as np
from shapely.geometry import shape


def mask_to_polygons(mask: "np.ndarray", simplify: float = 1.5, min_area: float = 12.0):
    """二值掩膜转轮廓环列表。

    mask: HW uint8，1=建筑物
    simplify: 轮廓简化容差（像素），越大顶点越少
    min_area: 最小面积阈值（像素），过滤噪点

    返回: [[外环坐标, 孔洞坐标...], ...]
    """
    try:
        import cv2
    except ImportError:
        cv2 = None

    binary = (mask > 0).astype(np.uint8)

    # 形态学清理：开运算去毛刺，闭运算补空洞
    if cv2 is not None:
        k = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, k, iterations=1)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, k, iterations=1)

    # 连通域标记
    if cv2 is not None:
        n, labels, _, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        target = labels
    else:
        from scipy import ndimage
        labels, n = ndimage.label(binary)
        target = labels

    polygons = []
    for i in range(1, n):
        comp = (target == i).astype(np.uint8)
        if comp.sum() < min_area:
            continue

        if cv2 is not None:
            contours, hier = cv2.findContours(comp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            if hier is None:
                continue
            hier = hier[0]

            for ci in range(len(contours)):
                if hier[ci][3] != -1:      # 跳过孔洞，只处理外环
                    continue
                outer = contours[ci]
                if simplify > 0:
                    outer = cv2.approxPolyDP(outer, simplify, True)
                if len(outer) < 3:
                    continue

                rings = [outer[:, 0, :].astype(float).tolist()]

                child = hier[ci][2]        # 收集该外环下的孔洞
                while child != -1:
                    hole = contours[child]
                    if simplify > 0:
                        hole = cv2.approxPolyDP(hole, simplify, True)
                    if len(hole) >= 3:
                        rings.append(hole[:, 0, :].astype(float).tolist())
                    child = hier[child][0]

                polygons.append(rings)
        else:
            from skimage import measure
            for c in measure.find_contours(comp, 0.5):
                pts = np.column_stack([c[:, 1], c[:, 0]]).tolist()
                if len(pts) >= 3:
                    polygons.append([pts])

    return polygons


def polygons_to_geojson(polys, pixel_size: float = 0.3):
    """像素坐标 -> GeoJSON FeatureCollection。

    pixel_size: 每像素地面分辨率（米）。默认 0.3，对应高分辨率卫星影像。
    """
    feats = []
    for rings in polys:
        xs = [p[0] * pixel_size for p in rings[0]]
        ys = [-p[1] * pixel_size for p in rings[0]]     # 图像 y 向下，翻转为平面 y 向上
        coords = [[[x, y] for x, y in zip(xs, ys)]]

        for hole in rings[1:]:
            hxs = [p[0] * pixel_size for p in hole]
            hys = [-p[1] * pixel_size for p in hole]
            coords.append([[x, y] for x, y in zip(hxs, hys)])

        feats.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": coords},
            "properties": {"area": round(abs(_ring_area(coords[0])), 2)},
        })

    return {"type": "FeatureCollection", "features": feats}


def _ring_area(ring):
    a = 0.0
    for i in range(len(ring) - 1):
        a += ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1]
    return a / 2.0


def export_shapefile(geojson: dict, epsg: int = 3857) -> bytes:
    """GeoJSON -> Shapefile(zip) 字节流。

    用 pyshp 手写，避免额外依赖。
    返回 zip 字节（含 .shp/.shx/.dbf/.prj/.cpg）
    """
    import shapefile

    features = geojson.get("features", [])
    buf = io.BytesIO()

    with tempfile.TemporaryDirectory() as td:
        base = str(pathlib.Path(td) / "buildings")

        w = shapefile.Writer(base, shapeType=shapefile.POLYGON)
        w.field("FID", "N")
        w.field("AREA", "N", 10, 2)

        for i, f in enumerate(features):
            geom = f.get("geometry") or {}
            shapeobj = shape(geom) if geom else None

            if shapeobj is None or shapeobj.is_empty:
                w.poly([[[]]])
                w.record(i, 0)
                continue

            polys = ([shapeobj] if shapeobj.geom_type == "Polygon"
                     else list(shapeobj.geoms))
            for p in polys:
                parts = [list(p.exterior.coords)]
                parts.extend(list(r.coords) for r in p.interiors)
                w.poly(parts)
                w.record(i, round(f.get("properties", {}).get("area", 0), 2))
        w.close()

        prj = _prj_text(epsg)
        if prj:
            with open(base + ".prj", "w", encoding="utf-8") as fp:
                fp.write(prj)
        with open(base + ".cpg", "w", encoding="utf-8") as fp:
            fp.write("UTF-8")

        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for ext in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
                p = pathlib.Path(base + ext)
                if p.is_file():
                    z.write(p, "buildings" + ext)

    return buf.getvalue()


def _prj_text(epsg: int) -> str:
    try:
        from pyproj import CRS
        return CRS.from_epsg(epsg).to_wkt()
    except Exception:
        # Web Mercator 兜底
        return (
            'PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",'
            'GEOGCS["WGS 84",DATUM["WGS_1984",'
            'SPHEROID["WGS 84",6378137,298.257223563]],'
            'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],'
            'PROJECTION["Mercator_1SP"],UNIT["metre",1]]'
        )