import random

from django.shortcuts import render
from django_redis import get_redis_connection
# Create your views here.
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as http_status
from rest_framework.viewsets import ModelViewSet
from rest_framework_jwt.settings import api_settings

from edu_api.libs.geetest import GeetestLib
from edu_api.settings import constants
from edu_api.untils.send_msg import Message
from user.models import UserInfo
from user.serializers import UserModelSerializer
from user.service import get_user_by_account
from rest_framework.generics import CreateAPIView, ListAPIView

pc_geetest_id = "759d5436a6bfe1e0a94d222e9452097b"
pc_geetest_key = "2061a99f3c25e50989a0c04536132953"

class CaptchaAPIView(APIView):
    """极验验证码"""

    user_id = 1
    status = False

    def get(self, request):
        """获取验证码"""
        username = request.query_params.get("username")
        user = get_user_by_account(username)
        if user is None:
            return Response({"message": "该用户不存在"},
                            status=http_status.HTTP_400_BAD_REQUEST)

        self.user_id = user.id

        # 通过极验类生成验证码对象
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        self.status = gt.pre_process(self.user_id)
        response_str = gt.get_response_str()
        return Response(response_str)

    def post(self, request):
        """验证验证码"""

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.data.get("geetest_challenge")
        validate = request.data.get("geetest_validate")
        seccode = request.data.get("geetest_seccode")
        # 判断用户是否存在
        if self.user_id:
            result = gt.success_validate(challenge, validate, seccode, self.user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        print(result)
        result = {"status": "success"} if result else {"status": "fail"}
        return Response(result)


class UserAPIView(CreateAPIView):
    queryset = UserInfo.objects.all()
    serializer_class = UserModelSerializer

class PhoneAPIView(ModelViewSet):
    serializer_class = UserModelSerializer

    def get_phone(self,request,*args,**kwargs):
        phone = request.data.get('phone')

        try:
            user = UserInfo.objects.get(phone=phone)
            return Response({'message':'手机号已被注册'},status=http_status.HTTP_400_BAD_REQUEST)
        except:
            return Response('ok')


class SendMessageAPIView(APIView):
    def get(self,request,*args,**kwargs):
        redis_connection = get_redis_connection('sms_code')
        phone = request.query_params.get('phone')
        phone_code = redis_connection.get('sms_%s' % phone)
        if phone_code is not None:
            return Response({
                'message':'您已经在60s内发送过请求啦'
            },
            status=http_status.HTTP_400_BAD_REQUEST
            )

        code = random.randint(100000,999999)

        redis_connection.setex('sms_%s' % phone,constants.SMS_EXPIRE_TIME,code)
        redis_connection.setex('mobile_%s' % phone,constants.PHONE_EXPIRE_TIME,code)
        try:
            msg = Message(constants.API_KEY)
            msg.send_message(phone,code)
        except:
            return Response({'message': '短信发送失败'}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message':'短信发送成功'},status=http_status.HTTP_200_OK)

class Phone(ModelViewSet):
    """登录手机号验证"""

    def phone_code(self, request, *args, **kwargs):
        username = request.data.get('phone')
        phone = UserInfo.objects.filter(phone=username)
        if phone:
            return Response({
                'message': 'ok',
            }, status=http_status.HTTP_200_OK)
        else:
            return Response({
                'message': '手机号不存在',
            }, status=http_status.HTTP_400_BAD_REQUEST)


class PhoneLoginAPIView(ModelViewSet):
    """短信登录"""

    def phone_login(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        user = UserInfo.objects.filter(phone=phone).first()
        code = request.data.get('code')
        # 获取redis连接
        conn = get_redis_connection('sms_code')
        phone_code = conn.get("mobile_%s" % phone)
        phone_code = phone_code.decode('utf-8')
        if code != phone_code:
            return Response({
                'message': '验证码错误',
            }, status=http_status.HTTP_400_BAD_REQUEST)
        if user:
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            # 根据用户生成载荷
            payload = jwt_payload_handler(user)
            # 根据载荷生成token
            user.token = jwt_encode_handler(payload)

            return Response({
                'message': '登陆成功',
                'data': UserModelSerializer(user).data
            }, status=http_status.HTTP_200_OK)
        return Response({
            'message': '登陆失败，手机号没有被注册',
        }, status=http_status.HTTP_400_BAD_REQUEST)