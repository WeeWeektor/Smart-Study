from courses.services.structure_course_module_action_service import save_files_in_supabase


async def convert_to_markdown(lesson, files, courseId):
    markdown_output = ""

    if lesson['typeCategory'] == 'custom':
        for content_block in lesson['contentBlocks']:
            fileKey = content_block['data']['fileKey']
            content_type = content_block['type']
            file = files.get(fileKey)

            if content_type == 'image' or content_type == 'video':
                url = await save_files_in_supabase(courseId, file, fileKey, 'lesson', content_type)
                print("\n\n", url, "\n\n")

    elif lesson['typeCategory'] == 'link':
        pass

    else:
        fileKey = lesson['singleContentData']['fileKey']
        content_type = lesson['typeCategory']
        file = files.get(fileKey)

        url = await save_files_in_supabase(courseId, file, fileKey, 'lesson', content_type)
        print("\n\n", url, "\n\n")

    return markdown_output
