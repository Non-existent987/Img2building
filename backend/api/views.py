from django.http import JsonResponse
import math
import requests
from django.views.decorators.csrf import csrf_exempt
import json
def say_hello(request):
    # 返回一个 JSON 响应
    return JsonResponse({"message": "你好来自后端"})

def lonlat_to_tile(lon, lat, zoom):
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    xtile = math.floor((lon + 180.0) / 360.0 * n)
    ytile = math.floor((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

@csrf_exempt # 取消 CSRF 验证
def download_image_view(request):
    # 处理下载图片的逻辑
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = float(data.get('lat'))
            lng = float(data.get('lng'))
            print(f"接收到坐标: lat={lat}, lng={lng}")
            if lat is None or lng is None:
                return JsonResponse({"status": "error", "message": "缺少参数"}, status=400)
            #计算瓦片坐标
            zoom = 18
            tile_x, tile_y = lonlat_to_tile(lng, lat, zoom)
            print(f"计算的瓦片坐标: x={tile_x}, y={tile_y}, zoom={zoom}")
            # 构建下载 URL
            image_url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{tile_y}/{tile_x}"
            # 下载图片
            print(f"下载图片 URL: {image_url}")
            response = requests.get(image_url, stream=True)
            response.raise_for_status()  # 检查请求是否成功

            #保存图片到本地
            save_path = 'd:/下载的图片.png'
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"图片已保存到 {save_path}")
            return JsonResponse({"status": "success", "message": f"图片已保存到 {save_path}"})
        except Exception as e:
            print(f"处理请求时出错: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '仅支持 POST 请求'}, status=405)
