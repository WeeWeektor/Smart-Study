async def upload_course_cover_image(course, file):
    """Завантаження або оновлення обкладинки курсу"""

    return await course.upload_cover_image(file)
