from rest_framework import serializers
from django.db.models import Q
from courses.models import UserCourseEnrollment, TestAttempt, Test, Lesson


class UserCourseEnrollmentSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для UserCourseEnrollment.
    Додає обчислювані поля для статусу завершення та сертифікату.
    """
    is_fully_completed = serializers.SerializerMethodField()
    is_failed = serializers.SerializerMethodField()
    certificate_url = serializers.SerializerMethodField()

    course_title = serializers.CharField(source='course.title', read_only=True)
    course_description = serializers.CharField(source='course.description', read_only=True)

    class Meta:
        model = UserCourseEnrollment
        fields = [
            'id',
            'progress',
            'is_fully_completed',
            'is_failed',
            'certificate_url',
            'course_title',
            'course_description',
        ]

    @staticmethod
    def get_is_fully_completed(obj):
        """
        Перевіряє, чи досяг прогрес 100%.
        """
        return obj.progress >= 100

    def get_is_failed(self, obj):
        """
        Визначає, чи провалено курс (немає можливості отримати сертифікат).
        Логіка: Курс провалено, якщо є хоча б один обов'язковий тест (з лімітом спроб),
        який користувач не здав, і використав всі доступні спроби.
        """
        if self.get_is_fully_completed(obj):
            return False

        required_tests = Test.objects.filter(
            Q(course=obj.course) | Q(module__course=obj.course),
            count_attempts__gt=0
        )

        for test in required_tests:
            has_passed = TestAttempt.objects.filter(
                enrollment=obj,
                test=test,
                passed=True
            ).exists()

            if has_passed:
                continue

            attempts_used = TestAttempt.objects.filter(
                enrollment=obj,
                test=test
            ).count()

            if attempts_used >= test.count_attempts:
                return True

        total_lessons = Lesson.objects.filter(module__course=obj.course).count()
        completed_lessons = obj.lesson_progresses.filter(completed_at__isnull=False).count()

        if completed_lessons < total_lessons:
            return False

        return False

    @staticmethod
    def get_certificate_url(obj):
        """
        Повертає посилання на сертифікат, якщо він існує та валідний.
        """
        cert = obj.user.certificates.filter(course=obj.course, is_valid=True).first()

        if cert:
            return f"/{cert.certificate_id}" # TODO

        return None
