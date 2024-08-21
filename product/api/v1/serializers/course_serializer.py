from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from rest_framework import serializers

from courses.models import Course, Group, Lesson
from users.models import Subscription, CustomUser

User = get_user_model()


class LessonSerializer(serializers.ModelSerializer):
    """Список уроков."""

    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class CreateLessonSerializer(serializers.ModelSerializer):
    """Создание уроков."""

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'slug',
            'course'
        )
    
        
class StudentSerializer(serializers.ModelSerializer):
    """Студенты курса."""

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class GroupSerializer(serializers.ModelSerializer):
    """Список групп."""

    course = serializers.SerializerMethodField(read_only=True)
    users_count = serializers.SerializerMethodField(read_only=True)
    users = StudentSerializer(many=True, read_only=True)

    def get_course(self, obj):
        return obj.course.title

    def get_users_count(self, obj):
        return obj.users.count()

    class Meta:
        model = Group
        fields = (
            'id',
            'course',
            'users_count',
            'users'
        )


class CreateGroupSerializer(serializers.ModelSerializer):
    """Создание групп."""

    class Meta:
        model = Group
        fields = '__all__'


class MiniLessonSerializer(serializers.ModelSerializer):
    """Список названий уроков для списка курсов."""

    class Meta:
        model = Lesson
        fields = (
            'title',
        )


class CourseSerializer(serializers.ModelSerializer):
    """Список курсов."""

    lessons = MiniLessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField(read_only=True)
    students_count = serializers.SerializerMethodField(read_only=True)
    groups_filled_percent = serializers.SerializerMethodField(read_only=True)
    demand_course_percent = serializers.SerializerMethodField(read_only=True)
    is_bought = serializers.SerializerMethodField(read_only=True)

    def get_lessons_count(self, obj) -> int:
        """Количество уроков в курсе."""
        return obj.lessons.count()

    def get_students_count(self, obj) -> int:
        """Общее количество студентов на курсе."""
        amount = Subscription.objects.filter(course=obj.pk).count()
        return amount
    
    def get_groups_filled_percent(self, obj) -> int:
        """Процент заполнения групп, если в группе максимум 30 чел.."""
        try:
            average = obj.groups.annotate(students=Count('users')).aggregate(Avg('students'))
            return (average['students__avg'] / 30) * 100
        except:
            return 0.0
     
    def get_demand_course_percent(self, obj) -> int:
        """Процент приобретения курса."""
        users = CustomUser.objects.all().count()
        return (self.get_students_count(obj) / users) * 100

    def get_is_bought(self, obj) -> bool:
        """Определяет, куплен ли курс пользователем"""
        target_user = CustomUser.objects.filter(pk=self.context['request'].user.pk).first()
        return target_user.is_student(obj.pk)

    class Meta:
        model = Course
        fields = (
            'id',
            'author',
            'title',
            'start_date',
            'price',
            'lessons',
            'lessons_count',
            'demand_course_percent',
            'students_count',
            'groups_filled_percent',
            'is_bought'
        )


class CreateCourseSerializer(serializers.ModelSerializer):
    """Создание курсов."""

    class Meta:
        model = Course
        fields = '__all__'
