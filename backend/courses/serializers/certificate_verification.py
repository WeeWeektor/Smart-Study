from rest_framework import serializers

from courses.models import Certificate


class CertificateVerificationSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='course.title', read_only=True)
    issued_at = serializers.DateTimeField(format="%d.%m.%Y", read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'certificate_id',
            'student_name',
            'course_title',
            'issued_at',
            'is_valid'
        ]

    @staticmethod
    def get_student_name(obj):
        user = obj.user
        full_name = f"{user.name} {user.surname}".strip()
        return full_name if full_name else user.email
