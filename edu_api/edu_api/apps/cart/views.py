
import logging
from datetime import datetime

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from course.models import Course, CourseExpire
from edu_api.settings.constants import IMG_SRC

log = logging.getLogger('django')

class CartViewSet(ViewSet):

    permission_classes = [IsAuthenticated]

    def add_cart(self,request):
        course_id = request.data.get('course_id')
        user_id = request.user.id
        expire = 0
        try:
            Course.objects.get(is_show=True,is_delete=False,id=course_id)
        except Course.DoesNotExist:
            return Response({'message':'您添加的课程不存在'},status=status.HTTP_400_BAD_REQUEST)

        try:
            redis_connection = get_redis_connection("cart")
            pipeline = redis_connection.pipeline()
            pipeline.multi()
            pipeline.hset('cart_%s' % user_id,course_id,expire)
            pipeline.sadd('selected_%s' % user_id,course_id)
            pipeline.execute()
            cart_length = redis_connection.hlen("cart_%s" % user_id)
        except:
            log.error("购物车储存数据失败")
            return Response({'message':'参数错误,添加失败'},status=status.HTTP_507_INSUFFICIENT_STORAGE)

        return Response({'message': '添加成功','cart_length':cart_length},status=status.HTTP_201_CREATED)

    def list_cart(self,request):
        user_id = request.user.id
        redis_connection = get_redis_connection("cart")
        cart_list = redis_connection.hgetall("cart_%s" % user_id)
        select_list = redis_connection.smembers("selected_%s" % user_id)
        data = []
        for course_id_byte,expire_id_byte in cart_list.items():
            course_id = int(course_id_byte)#课程id
            expire_id = int(expire_id_byte)# 有效期值
            print(55)
            try:
                course = Course.objects.get(is_show=True,is_delete=False,id=course_id)
            except Course.DoesNotExist:
                continue

            original_price = course.price
            # expire_text = "永久有效"
            try:
                if expire_id > 0:
                    course_expire = CourseExpire.objects.get(id=expire_id)
                    original_price = course_expire.price
                    # expire_text = course_expire.expire_text
                    # print(68,expire_text)
            except CourseExpire.DoesNotExist:
                # print(68, expire_text)
                pass
            final_price = course.final_price(expire_id)

            data.append({
                "selected": True if course_id_byte in select_list else False,
                "course_img": IMG_SRC + course.course_img.url,
                "name": course.name,
                "id": course.id,
                "price":"%.2f" % original_price,
                "final_price":"%.2f" %  final_price,
                "real_price":"%.2f" %  final_price,
                "expire_id": expire_id,
                "expire_list":course.expire_list,

            })
        return Response(data)

    def select_change(self,request):
        course_id = request.data.get('course_id')
        select = request.data.get('selected')
        user_id = request.user.id
        redis_connection = get_redis_connection("cart")
        if select:
            try:
                redis_connection.sadd('selected_%s' % user_id, course_id)
                return Response({'message': "选中成功"}, status=status.HTTP_200_OK)

            except:
                return Response({"message":"该课程不存在"},status=status.HTTP_400_BAD_REQUEST)
        else:
            redis_connection.srem('selected_%s' % user_id, course_id)
            return Response({'message': "取消成功"}, status=status.HTTP_200_OK)


    def delete_course(self,request):
        course_id = request.data.get('course_id')
        user_id = request.user.id
        redis_connection = get_redis_connection("cart")

        try:
            redis_connection.hdel('cart_%s' % user_id,course_id)
            redis_connection.srem('selected_%s' % user_id, course_id)
            cart_length = redis_connection.hlen("cart_%s" % user_id)
            return Response({'message': "删除成功" , "cart_length":cart_length}, status=status.HTTP_200_OK)

        except:
            return Response({"message":"该课程不存在"},status=status.HTTP_400_BAD_REQUEST)

    def expire_change(self,request):
        course_id = request.data.get('course_id')
        user_id = request.user.id
        expire_id = request.data.get("expire_id")
        print(122,expire_id)

        try:
            course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)

            if expire_id > 0:
                expire_item = CourseExpire.objects.filter(is_delete=False, is_show=True, pk=expire_id)
                if not expire_item:
                    raise CourseExpire.DoesNotExist()
        except Course.DoesNotExist:
            return Response({"message": "操作的课程不存在"}, status=status.HTTP_400_BAD_REQUEST)

        redis_connection = get_redis_connection("cart")
        redis_connection.hset("cart_%s" % user_id, course_id, expire_id)

        final_price = course.final_price(expire_id)
        print(137,expire_id)

        return Response({"message": "切换有效期成功", "price": final_price})

    def get_select_course(self, request):
        user_id = request.user.id
        redis_connection = get_redis_connection("cart")
        cart_list = redis_connection.hgetall("cart_%s" % user_id)
        select_list = redis_connection.smembers("selected_%s" % user_id)

        total_price = 0
        data = []

        for course_id_byte, expire_id_byte in cart_list.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_id_byte)

            if course_id_byte in select_list:

                try:
                    course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                except Course.DoesNotExist:
                    continue

                origin_price = course.price
                expire_text = "永久有效"

                if expire_id > 0:
                    try:
                        course_expire = CourseExpire.objects.get(pk=expire_id)

                        origin_price = course_expire.price
                        expire_text = course_expire.expire_text

                    except CourseExpire.DoesNotExist:
                        pass

                final_price = course.final_price(expire_id)

                data.append({
                    'id': course.id,
                    # 'price': course.real_price(),
                    "course_img": IMG_SRC + course.course_img.url,
                    "name": course.name,
                    # 课程对应的有效期文本
                    "expire_text": expire_text,
                    # 获取有效期真实价格
                    "final_price": "%.2f" % float(final_price),
                    # 原价
                    "price": "%.2f" % origin_price,
                })

                # 商品所有的总价
                total_price += float(final_price)

        total_price = "%.2f" % float(total_price)

        return Response({"course_list": data,"real_price": total_price, "total_price": total_price, "message": "获取成功"})
