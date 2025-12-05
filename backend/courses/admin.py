from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import (
    Course,
    CourseMeta,
    CourseVersion,
    Module,
    Lesson,
    LessonProgress,
    UserCourseEnrollment,
    Test,
    TestAttempt,
    CourseReview,
    Certificate,
    Wishlist,
    CourseAnnouncement,
)


class LessonInline(admin.TabularInline):
    model = Lesson
    fields = ("title", "order", "content_type", "duration")
    extra = 0
    show_change_link = True


class TestInline(admin.TabularInline):
    model = Test
    fields = ("title", "order", "is_public")
    extra = 0
    show_change_link = True


class ModuleInline(admin.TabularInline):
    model = Module
    fields = ("title", "order")
    extra = 0
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "category", "is_published", "created_at", "version")
    search_fields = ("title", "description", "owner__email", "owner__name", "owner__surname")
    list_filter = ("category", "is_published")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("owner",)
    inlines = (ModuleInline,)
    actions = ("publish_selected", "create_version_snapshots")

    def publish_selected(self, request, queryset):
        now = timezone.now()
        count = 0
        for obj in queryset.filter(is_published=False):
            obj.is_published = True
            obj.published_at = now
            obj.save(update_fields=["is_published", "published_at"])
            count += 1
        self.message_user(request, _("%d course(s) published.") % count)

    publish_selected.short_description = _("Publish selected courses")

    def create_version_snapshots(self, request, queryset):
        count = 0
        for obj in queryset:
            obj.create_version_snapshot()
            count += 1
        self.message_user(request, _("%d version snapshot(s) created.") % count)

    create_version_snapshots.short_description = _("Create version snapshot(s)")


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    search_fields = ("title", "course__title")
    raw_id_fields = ("course",)
    inlines = (LessonInline, TestInline)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "order", "content_type", "duration")
    search_fields = ("title", "module__title", "description", "content")
    list_filter = ("content_type", "module__course")
    raw_id_fields = ("module",)
    ordering = ("module", "order")
    fieldsets = (
        (None, {
            "fields": ("module", "title", "description", "content_type", "order", "duration")
        }),
        (_("Content"), {
            "fields": ("content", "comment"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("title", "context", "is_public", "order")
    search_fields = ("title", "course__title", "module__title")
    list_filter = ("is_public",)
    raw_id_fields = ("course", "module")

    def context(self, obj):
        if obj.course_id:
            return f"Course: {obj.course.title}"
        if obj.module_id:
            return f"Module: {obj.module.title}"
        return _("Public")

    context.short_description = _("Context")


@admin.register(UserCourseEnrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "progress", "completed", "enrolled_at")
    search_fields = ("user__email", "user__name", "course__title")
    list_filter = ("completed", "course")
    raw_id_fields = ("user", "course")
    readonly_fields = ("enrolled_at", "completed_at")
    actions = ("mark_completed",)

    def mark_completed(self, request, queryset):
        now = timezone.now()
        count = 0
        for obj in queryset.filter(completed=False):
            obj.completed = True
            obj.completed_at = now
            obj.progress = 100
            obj.save(update_fields=["completed", "completed_at", "progress"])
            if hasattr(obj.course, "details"):
                obj.course.details.update_counters()
            count += 1
        self.message_user(request, _("%d enrollment(s) marked as completed.") % count)

    mark_completed.short_description = _("Mark selected enrollments as completed")


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("lesson", "enrollment", "completion_percentage", "started_at", "completed_at")
    search_fields = ("lesson__title", "enrollment__user__email")
    raw_id_fields = ("enrollment", "lesson")


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ("test", "user", "score", "passed", "started_at")
    search_fields = ("test__title", "user__email")
    raw_id_fields = ("test", "user")
    list_filter = ("passed",)


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "rating", "created_at", "is_verified")
    search_fields = ("course__title", "user__email", "comment")
    list_filter = ("rating", "is_verified")
    raw_id_fields = ("course", "user")
    actions = ("verify_reviews",)

    def verify_reviews(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, _("%d review(s) verified.") % updated)

    verify_reviews.short_description = _("Verify selected reviews")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("certificate_id", "user", "course", "issued_at", "is_valid")
    search_fields = ("certificate_id", "user__email", "course__title")
    list_filter = ("is_valid",)
    raw_id_fields = ("user", "course")
    actions = ("revoke_certificates",)

    def revoke_certificates(self, request, queryset):
        updated = queryset.update(is_valid=False)
        self.message_user(request, _("%d certificate(s) revoked.") % updated)

    revoke_certificates.short_description = _("Revoke selected certificates")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "added_at")
    search_fields = ("user__email", "course__title")
    raw_id_fields = ("user", "course")


@admin.register(CourseAnnouncement)
class CourseAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("course", "title", "is_important", "created_at")
    search_fields = ("title", "content", "course__title")
    list_filter = ("is_important",)
    raw_id_fields = ("course",)


@admin.register(CourseMeta)
class CourseMetaAdmin(admin.ModelAdmin):
    list_display = ("course", "total_modules", "total_lessons", "total_tests", "number_completed", "number_of_active")
    search_fields = ("course__title",)
    raw_id_fields = ("course",)


@admin.register(CourseVersion)
class CourseVersionAdmin(admin.ModelAdmin):
    list_display = ("title", "course_id", "version_number", "created_at")
    search_fields = ("title",)
    readonly_fields = ("course_data", "created_at")
    list_filter = ("version_number",)
