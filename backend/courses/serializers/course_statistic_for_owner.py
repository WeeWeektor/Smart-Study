from django.db.models import Avg
from rest_framework import serializers

from courses.models import Course, UserCourseEnrollment


class StudentCourseStatisticSerializer(serializers.ModelSerializer):
    """
    Серіалізує студента для таблиці статистики.
    Працює з моделлю UserCourseEnrollment.
    """
    id = serializers.UUIDField(source='user.id', read_only=True)
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    progress = serializers.DecimalField(source='progress', max_digits=5, decimal_places=2, read_only=True)
    status = serializers.SerializerMethodField()
    joined_at = serializers.DateTimeField(source='enrolled_at', format="%d.%m.%Y")

    class Meta:
        model = UserCourseEnrollment
        fields = [
            'id',
            'name',
            'email',
            'progress',
            'status',
            'joined_at',
        ]

    @staticmethod
    def get_name(obj):
        full_name = f"{getattr(obj.user, 'name', '')} {getattr(obj.user, 'surname', '')}".strip()
        return full_name if full_name else obj.user.email

    @staticmethod
    def get_status(obj):
        if obj.completed:
            if obj.progress == 100:
                return 'success'
            return 'failed'

        return 'in_progress'


class CourseStatisticForOwnerSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для статистики курсу (аналітика проходження та успішності студентів),
    призначений для власника курсу.
    """

    total_students = serializers.SerializerMethodField()
    total_in_progress_course_students = serializers.SerializerMethodField()
    total_completed_course_students = serializers.SerializerMethodField()
    total_success_complete = serializers.SerializerMethodField()
    total_failed_complete = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'total_students',
            'total_in_progress_course_students',
            'total_completed_course_students',
            'total_success_complete',
            'total_failed_complete',
            'average_rating',
            'total_reviews',
            'students',
        ]

    @staticmethod
    def get_total_students(obj):
        return obj.enrollments.count()

    @staticmethod
    def get_total_in_progress_course_students(obj):
        return obj.enrollments.filter(completed=False).count()

    @staticmethod
    def get_total_completed_course_students(obj):
        return obj.enrollments.filter(completed=True).count()

    @staticmethod
    def get_total_success_complete(obj):
        return obj.enrollments.filter(completed=True, progress=100).count()

    @staticmethod
    def get_total_failed_complete(obj):
        return obj.enrollments.filter(completed=True).exclude(progress=100).count()

    @staticmethod
    def get_average_rating(obj):
        if hasattr(obj, 'reviews'):
            avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
            return round(avg, 1) if avg else 0
        return 0

    @staticmethod
    def get_total_reviews(obj):
        if hasattr(obj, 'reviews'):
            return obj.reviews.count()
        return 0

    @staticmethod
    def get_students(obj):
        enrollments = obj.enrollments.select_related('user').order_by('-enrolled_at')
        return StudentCourseStatisticSerializer(enrollments, many=True).data
