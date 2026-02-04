from rest_framework import serializers


class CourseTestSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    test_type = serializers.SerializerMethodField()
    score = serializers.FloatField()
    pass_score = serializers.IntegerField()
    passed = serializers.BooleanField()
    attempts_used = serializers.IntegerField()
    max_attempts = serializers.IntegerField()

    @staticmethod
    def get_test_type(obj):
        return 'module_test' if obj.get('module_id') else 'course_test'
