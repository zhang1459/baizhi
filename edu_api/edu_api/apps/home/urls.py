from django.urls import path

from home.views import BannerAPIView, NavAPIView

urlpatterns = [
    path('banners/',BannerAPIView.as_view()),
    path('navs/',NavAPIView.as_view()),
]