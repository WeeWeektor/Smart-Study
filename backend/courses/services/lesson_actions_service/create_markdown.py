from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from common.services import mongo_repo
from common.services.markdown_generator import MarkdownHelper
from courses.services.structure_course_module_action_service import save_files_in_supabase

# TODO Test full scenario
async def convert_to_markdown(lesson, files, courseId) -> str:
    lesson_type_category = lesson.get('typeCategory')
    markdown_output = ""

    if lesson_type_category is None:
        lesson_id_str = str(lesson.get("lesson_id"))
        lesson_mongo_data = await sync_to_async(mongo_repo.get_document_by_field)(
            collection_name="module_structures",
            field="structure.lesson_id",
            value=lesson_id_str,
        )
        lesson_type_category = _find_lesson_in_structure(lesson_mongo_data, lesson_id_str)

    markdown_output += MarkdownHelper.generate_block('title', lesson.get('title'))
    markdown_output += MarkdownHelper.generate_block('description', lesson.get('description'))

    if lesson_type_category == 'custom':
        for content_block in lesson.get('contentBlocks', []):
            content_type = content_block.get('type')
            block_data = content_block.get('data', {})

            existing_url = content_block.get('url') or block_data.get('url')

            if content_type in ['image', 'video']:
                file_key = block_data.get('fileKey')
                file = files.get(file_key) if file_key else None

                if file:
                    url = await save_files_in_supabase(courseId, file, file_key, 'lesson', content_type)
                    markdown_output += MarkdownHelper.generate_block(content_type, block_data, url=url)
                    # TODO delete old files from supabase if exists
                elif existing_url:
                    markdown_output += MarkdownHelper.generate_block(content_type, block_data, url=existing_url)
                else:
                    raise ValidationError(_(f"Missing file or URL for block type: {content_type}"))
            else:
                markdown_output += MarkdownHelper.generate_block(content_type, block_data, url=existing_url)

    elif lesson_type_category == 'link':
        link_url = lesson.get('singleContentData')
        if not link_url:
            raise ValidationError(_("Link URL is missing for lesson type 'link'"))
        markdown_output += MarkdownHelper.generate_block('link', link_url, url=link_url)

    else:
        single_data = lesson.get('singleContentData', {})
        existing_preview_url = single_data.get('previewUrl')
        file_key = single_data.get('fileKey') or single_data.get('fileName')
        file = files.get(file_key) if file_key else None

        if file:
            #TODO delete old file from supabase if exists
            url = await save_files_in_supabase(courseId, file, file_key, 'lesson', lesson_type_category)
            markdown_output += MarkdownHelper.generate_block(lesson_type_category, single_data, url=url)
        if existing_preview_url:
            markdown_output += MarkdownHelper.generate_block(lesson_type_category, single_data,
                                                             url=existing_preview_url)
        else:
            raise ValidationError(_(f"No file or preview URL provided for lesson type: {lesson_type_category}"))

    if lesson_type_category != 'custom':
        markdown_output += MarkdownHelper.generate_block('comment', lesson.get('comment'))

    return markdown_output


def _find_lesson_in_structure(lesson_mongo_data, lesson_id_str):
    if lesson_mongo_data and "structure" in lesson_mongo_data:
        for item in lesson_mongo_data["structure"]:
            if str(item.get("lesson_id")) == lesson_id_str:
                return item.get("content_type")
    return None
