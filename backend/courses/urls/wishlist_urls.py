from django.urls import path

from courses.views import UserWishlistView

app_name = 'wishlist'
urlpatterns = [
    path('add-course-to-wishlist/', UserWishlistView.as_view(), name='add-course-to-wishlist'),
    path('remove-course-from-wishlist/', UserWishlistView.as_view(), name='remove-course-from-wishlist'),
]
