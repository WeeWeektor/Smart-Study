from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from common.services import mongo_repo
from common.services.markdown_generator import MarkdownHelper
from courses.services.structure_course_module_action_service import save_files_in_supabase, delete_files_from_supabase


async def convert_to_markdown(lesson, files, courseId, lesson_id, module_order) -> str:
    lesson_type_category = lesson.get('typeCategory')
    lesson_id_str = str(lesson_id) if lesson_id else None
    old_type = None

    if lesson_id_str:
        lesson_mongo_data = await sync_to_async(mongo_repo.get_document_by_field)(
            collection_name="module_structures",
            field="structure.lesson_id",
            value=lesson_id_str,
        )
        old_lesson_obj = _find_lesson_in_structure_obj(lesson_mongo_data, lesson_id_str)
        if old_lesson_obj:
            old_type = old_lesson_obj.get("content_type")
            if lesson_type_category is None:
                lesson_type_category = old_type

    if lesson_id_str and old_type and old_type != lesson_type_category:
        await _cleanup_files_on_type_change(courseId, lesson, module_order)

    markdown_output = ""
    markdown_output += MarkdownHelper.generate_block('title', lesson.get('title'))
    markdown_output += MarkdownHelper.generate_block('description', lesson.get('description'))

    if lesson_type_category == 'custom':
        markdown_output += await _process_custom_content_blocks(lesson, courseId, lesson_id_str, files)
    elif lesson_type_category == 'link':
        markdown_output += _process_link_lesson(lesson)
    else:
        markdown_output += await _process_another_lesson_types(lesson, files, lesson_id_str, courseId,
                                                               lesson_type_category)

    if lesson_type_category != 'custom':
        markdown_output += MarkdownHelper.generate_block('comment', lesson.get('comment'))

    return markdown_output


async def _process_custom_content_blocks(lesson, courseId, lesson_id_str, files) -> str:
    output = ""
    for content_block in lesson.get('contentBlocks', []):
        content_type = content_block.get('type')
        block_data = content_block.get('data', None)

        if content_type in ['image', 'video']:
            file_key = block_data.get('fileKey')
            file = files.get(file_key) if file_key else None

            if file:
                if lesson_id_str:
                    await delete_files_from_supabase(courseId, 'lesson', file_key)

                url = await save_files_in_supabase(courseId, file, file_key, 'lesson', content_type)
                output += MarkdownHelper.generate_block(content_type, block_data, url=url)
            else:
                existing_url = content_block.get('url') or block_data.get('url') or block_data.get('previewUrl')
                if not existing_url:
                    raise ValidationError(_(f"Missing file or URL for block type: {content_type}"))
                output += MarkdownHelper.generate_block(content_type, block_data, url=existing_url)
        else:
            output += MarkdownHelper.generate_block(content_type, block_data)

    return output


def _process_link_lesson(lesson) -> str:
    link_url = lesson.get('singleContentData')
    if not link_url:
        raise ValidationError(_("Link URL is missing for lesson type 'link'"))
    return MarkdownHelper.generate_block('link', link_url, url=link_url)


async def _process_another_lesson_types(lesson, files, lesson_id_str, courseId, lesson_type_category) -> str:
    single_data = lesson.get('singleContentData', {})
    file_key = single_data.get('fileKey') or single_data.get('fileName')
    file = files.get(file_key) if file_key else None

    if file:
        if lesson_id_str:
            await delete_files_from_supabase(courseId, 'lesson', file_key)

        url = await save_files_in_supabase(courseId, file, file_key, 'lesson', lesson_type_category)
        return MarkdownHelper.generate_block(lesson_type_category, single_data, url=url)
    elif single_data.get('previewUrl'):
        return MarkdownHelper.generate_block(lesson_type_category, single_data, url=single_data.get('previewUrl'))
    else:
        raise ValidationError(_(f"No file or preview URL provided for lesson type: {lesson_type_category}"))


def _find_lesson_in_structure_obj(lesson_mongo_data, lesson_id_str):
    if lesson_mongo_data and "structure" in lesson_mongo_data:
        for item in lesson_mongo_data["structure"]:
            if str(item.get("lesson_id")) == lesson_id_str:
                return item
    return None


async def _cleanup_files_on_type_change(courseId, lesson, module_order):
    """Видаляє старі файли, якщо тип уроку повністю змінився"""
    from courses.services.lesson_actions_service import delete_lesson_files_by_prefix

    lesson_order = lesson.get('order')

    if module_order and lesson_order:
        await delete_lesson_files_by_prefix(courseId, module_order, lesson_order)
