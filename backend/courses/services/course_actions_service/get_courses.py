import asyncio
import logging
from typing import Union

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext

from common.services import mongo_repo
from common.utils import validate_uuid, error_response
from courses.choices import SORTING_DICT
from courses.models import Course, Module, Test, Lesson
from courses.services.builder_json import build_course_json_success
from users.models import CustomUser
from .get_course_owner_data import get_course_owner_data
from ..test_actions_service import fetch_questions
from ...utils import generate_course_json_with_details_and_owner

logger = logging.getLogger(__name__)


async def get_published_courses_by_autor(
        author_id,
        sort_keys: Union[list, None],
        status: Union[str, None],
        search_query: Union[str, None] = None
) -> Union[dict, list]:
    try:
        uuid_obj = validate_uuid(author_id)

        publish = None
        if not status:
            publish = True
        elif status and status == 'false':
            publish = False
        elif status and status == 'is_published':
            publish = True

        qs = Course.objects.select_related("details").filter(owner=uuid_obj)
        if publish is not None:
            qs = qs.filter(is_published=publish)

        if search_query:
            qs = qs.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if sort_keys:
            order_fields = [SORTING_DICT[k] for k in sort_keys if k in SORTING_DICT]
            if order_fields:
                qs = qs.order_by(*order_fields)

        courses = await sync_to_async(lambda: list(qs))()
        owner = await sync_to_async(lambda: CustomUser.objects.get(id=uuid_obj))()

        return [build_course_json_success(c, getattr(c, "details", None), owner) for c in courses]
    except CustomUser.DoesNotExist:
        return error_response(gettext("Author not found"), status=404)
    except ValidationError as e:
        return error_response(str(e), status=400)
    except Exception as e:
        logger.error(f"{gettext('Error receiving courses by author id')} ({author_id}): {str(e)}")
        return error_response(
            f"{gettext('Error receiving courses by author id')} ({author_id}): {str(e)})",
            status=500
        )


async def get_courses(cate: Union[list, None], level: Union[str, None], sort_keys: Union[list, None],
                      search_query: Union[str, None] = None
                      ) -> Union[dict, list]:
    try:
        qs = Course.objects.filter(is_published=True)

        if cate:
            qs = qs.filter(category__in=cate)
        if level:
            qs = qs.filter(details__level=level)

        if search_query:
            qs = qs.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if sort_keys:
            order_fields = [SORTING_DICT[k] for k in sort_keys if k in SORTING_DICT]
            if order_fields:
                qs = qs.order_by(*order_fields)

        courses = await sync_to_async(lambda: list(qs))()

        return await generate_course_json_with_details_and_owner(courses)
    except Exception as e:
        logger.error(f"{gettext('Error retrieving courses from DB:')} {str(e)}")
        return error_response(gettext("Error retrieving courses from DB"), status=500)


async def get_course_by_id(course_id, for_edit) -> dict:
    try:
        uuid_obj = validate_uuid(course_id)
        course = await sync_to_async(lambda: Course.objects.select_related('details', 'owner').get(pk=uuid_obj))()

        structure = await _get_cs_from_db(course.structure_ids, for_edit)
        owner_data = await get_course_owner_data(course.owner.id)

        course_data = build_course_json_success(course, course.details, owner_data, structure, full_owner=True)
        return course_data

    except ValidationError as e:
        return error_response(str(e), status=400)
    except Course.DoesNotExist:
        return error_response(gettext("Course not found"), status=404)
    except Exception as e:
        logger.error(f"{gettext('Error receiving courses by id')} ({course_id}): {str(e)}")
        return error_response(
            f"{gettext('Error receiving courses by id')} ({course_id}): {str(e)})",
            status=500
        )


async def _enrich_test_item(structure_item):
    """Отримує деталі тесту з SQL та питання з Mongo, оновлює переданий словник."""
    try:
        t_id = structure_item.get('test_id')
        if not t_id:
            return

        test_obj = await Test.objects.aget(pk=t_id)

        if test_obj.test_data_ids:
            questions_data = await sync_to_async(fetch_questions)("questions_data_for_test", test_obj.test_data_ids)
            questions_len = len(questions_data.get('questions', [])) if questions_data else 0
        else:
            questions_len = 0

        structure_item.update({
            "questions_len": questions_len,
            "pass_score": test_obj.pass_score,
            "count_attempts": test_obj.count_attempts,
            "random_questions": test_obj.randomize_questions,
            "show_correct_answers": test_obj.show_correct_answers,
            "description": test_obj.description
        })
    except (Test.DoesNotExist, AttributeError):
        pass


async def _enrich_lesson_item(structure_item):
    """Отримує деталі уроку з SQL (опис, контент тощо), оновлює переданий словник."""
    try:
        l_id = structure_item.get('lesson_id')
        if not l_id:
            return

        lesson_obj = await Lesson.objects.aget(pk=l_id)

        structure_item.update({
            "description": lesson_obj.description,
        })
    except (Lesson.DoesNotExist, AttributeError):
        pass


async def _process_module(structure_item, for_edit):
    """Обробляє один модуль: дістає структуру і збагачує тести всередині."""
    try:
        module = await sync_to_async(Module.objects.only("structure_ids").get)(pk=structure_item.get('module_id'))
        module_structure = await sync_to_async(mongo_repo.get_document_by_id)("module_structures", module.structure_ids)

        items = module_structure.get('structure', []) if module_structure else []

        if for_edit == "true":
            tasks = []
            for item in items:
                if item.get('type') in ['test', 'module-test']:
                    tasks.append(_enrich_test_item(item))
                elif item.get('type') == 'lesson':
                    tasks.append(_enrich_lesson_item(item))

            if tasks:
                await asyncio.gather(*tasks)

        return structure_item.get("order"), items
    except Module.DoesNotExist:
        return structure_item.get("order"), []


async def _get_cs_from_db(course_structure_ids, for_edit) -> dict:
    course_structure_doc = await sync_to_async(mongo_repo.get_document_by_id)("course_structures", course_structure_ids)
    if not course_structure_doc:
        return {"courseStructure": []}

    structure_list = course_structure_doc.get('structure', [])
    structureResponse = {"courseStructure": structure_list}

    module_tasks = []
    root_test_tasks = []

    for item in structure_list:
        item_type = item.get('type')

        if item_type == 'module':
            module_tasks.append(_process_module(item, for_edit))

        elif item_type == 'test' and for_edit == "true":
            root_test_tasks.append(_enrich_test_item(item))

    if root_test_tasks:
        await asyncio.gather(*root_test_tasks)

    if module_tasks:
        results = await asyncio.gather(*module_tasks)

        for order, items in results:
            structureResponse[f"moduleStructure_order_{order}"] = items

    return structureResponse
