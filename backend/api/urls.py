from django.urls import path
from . import views

urlpatterns = [
    # 示例接口
    # path('', views.hello_world),
    path('hello/', views.say_hello, name='say_hello'),
    path('download_image/', views.download_image_view, name='download_image'),
]

