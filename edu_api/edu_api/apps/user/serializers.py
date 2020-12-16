import re

from django.contrib.auth.hashers import make_password
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_jwt.settings import api_settings

from user.models import UserInfo
from user.service import get_user_by_account


class UserModelSerializer(ModelSerializer):
    token = serializers.CharField(max_length=1024,read_only=True,help_text='用户token')
    sms_code = serializers.CharField(max_length=1024,write_only=True,help_text='sms_code')

    class Meta:
        model = UserInfo
        fields = ('username','phone','password','id','token','sms_code')

        extra_kwargs = {
            "phone":{
                "write_only":True
            },
            "password": {
                "write_only": True
            },
            "username": {
                "read_only": True,
                # "default":
            },
            "id": {
                "read_only": True
            },

        }

    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")
        sms_code = attrs.get('sms_code')
        redis_connection = get_redis_connection('sms_code')
        phone_code = redis_connection.get('mobile_%s' % phone)
        if phone_code.decode('utf-8') != sms_code:
            raise serializers.ValidationError('验证码错误')
        if not re.match(r'^1[3-9]\d{9}$',phone):
            raise serializers.ValidationError("手机号不符合格式")

        if not re.match(r'^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z\W_]+$)(?![a-z0-9]+$)(?![a-z\W_]+$)(?![0-9\W_]+$)[a-zA-Z0-9\W_]{8,}$',password):
            raise serializers.ValidationError("密码要包含数字，字母和特殊字符，至少八位")

        try:
            user = get_user_by_account(phone)
        except UserInfo.DoesNotExist:
            user = None

        if user:
            raise serializers.ValidationError("手机号已被注册")
        return attrs

    def create(self, validated_data):
        password = validated_data.get("password")
        hash_pwd = make_password(password)

        phone = validated_data.get("phone")
        user =  UserInfo.objects.create(
            phone=phone,
            username=phone,
            password=hash_pwd
        )


        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        user.token = jwt_encode_handler(payload)
        return user

