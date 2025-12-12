from common.services.markdown_generator import MarkdownHelper
from courses.services.structure_course_module_action_service import save_files_in_supabase


async def convert_to_markdown(lesson, files, courseId) -> str:
    lesson_type_category = lesson.get('typeCategory')
    markdown_output = ""

    markdown_output += MarkdownHelper.generate_block('title', lesson.get('title'))
    markdown_output += MarkdownHelper.generate_block('description', lesson.get('description'))

    if lesson_type_category == 'custom':
        for content_block in lesson.get('contentBlocks'):
            content_type = content_block.get('type')

            if content_type == 'image' or content_type == 'video':
                fileKey = content_block['data']['fileKey']
                file = files.get(fileKey)

                url = await save_files_in_supabase(courseId, file, fileKey, 'lesson', content_type)
                markdown_output += MarkdownHelper.generate_block(content_type, content_block.get('data'), url=url)

            markdown_output += MarkdownHelper.generate_block(content_type, content_block.get('data'),
                                                             url=content_block.get('url'))

    elif lesson_type_category == 'link':
        link_url = lesson.get('singleContentData')
        markdown_output += MarkdownHelper.generate_block('link', link_url, url=link_url)

    else:
        fileKey = lesson['singleContentData']['fileKey']
        file = files.get(fileKey)

        url = await save_files_in_supabase(courseId, file, fileKey, 'lesson', lesson_type_category)
        markdown_output += MarkdownHelper.generate_block(lesson_type_category, lesson.get('singleContentData'), url=url)

    if lesson_type_category != 'custom':
        markdown_output += MarkdownHelper.generate_block('comment', lesson.get('comment'))

    return markdown_output
