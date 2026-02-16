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
    progress = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
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

    total_students = serializers.IntegerField(source='stat_total_students', read_only=True)
    total_in_progress_course_students = serializers.IntegerField(source='stat_in_progress', read_only=True)
    total_completed_course_students = serializers.IntegerField(source='stat_completed', read_only=True)
    total_success_complete = serializers.IntegerField(source='stat_success', read_only=True)
    total_failed_complete = serializers.IntegerField(source='stat_failed', read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.IntegerField(source='stat_total_reviews', read_only=True)
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
    def get_average_rating(obj):
        avg = getattr(obj, 'stat_avg_rating', 0)
        return round(avg, 1) if avg else 0

    @staticmethod
    def get_students(obj):
        students = getattr(obj, 'prefetched_students', [])
        return StudentCourseStatisticSerializer(students, many=True).data
