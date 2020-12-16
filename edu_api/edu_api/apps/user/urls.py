from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token

from user import views

urlpatterns = [
    path("login/", obtain_jwt_token),
    path("register/", views.UserAPIView.as_view()),
    path("captcha/", views.CaptchaAPIView.as_view()),
    path("message/", views.SendMessageAPIView.as_view()),
    path("phone_code/", views.Phone.as_view({'post': 'phone_code'})),
    path("phone_login/", views.PhoneLoginAPIView.as_view({'post': 'phone_login'})),
    path("phone/", views.PhoneAPIView.as_view({'post':'get_phone'})),
]
