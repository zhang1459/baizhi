from rest_framework.serializers import ModelSerializer

from course.models import CourseCategory, Course, Teacher, CourseChapter, CourseLesson


class CourseCategoryModelSerializer(ModelSerializer):
    """课程分类"""

    class Meta:
        model = CourseCategory
        fields = ("id", "name")


class TeacherModelSerializer(ModelSerializer):
    """讲师"""

    class Meta:
        model = Teacher
        fields = ("id", "name", "title","brief","image","signature")




class CourseLessonSerializer(ModelSerializer):

    model = CourseLesson
    fields = ('id','name','duration','free_trail')


class CourseChapterSerializer(ModelSerializer):
    course_lession = CourseLessonSerializer()
    model = CourseChapter
    fields = ('id','name','chapter','course_lession')

class CourseModelSerializer(ModelSerializer):
    """课程列表"""

    teacher = TeacherModelSerializer()
    class Meta:
        model = Course
        fields = ("id", "name", "course_img", "students", "lessons", "pub_lessons","brief_html","discount_price",
                  "price", "level", "teacher", "lesson_list","chapter_list","level_name","discount_name","active_time")
