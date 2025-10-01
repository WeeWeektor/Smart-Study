import logging
from typing import Union

from asgiref.sync import sync_to_async
from bson import ObjectId
from django.core.exceptions import ValidationError
from django.utils.translation import gettext

from common.services import mongo_repo
from common.utils import validate_uuid, error_response
from courses.choices import SORTING_DICT
from courses.models import Course, CourseMeta, Module
from courses.services.builder_json import build_course_json_success
from users.models import CustomUser

logger = logging.getLogger(__name__)


async def get_published_courses_by_autor(author_id, sort_keys: Union[list, None]) -> Union[dict, list]:
    try:
        uuid_obj = validate_uuid(author_id)

        qs = Course.objects.select_related("details").filter(owner=uuid_obj, is_published=True)
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


async def get_courses(cate: Union[list, None], level: Union[str, None], sort_keys: Union[list, None]) -> Union[dict, list]:
    try:
        qs = Course.objects.select_related("details", "owner").filter(is_published=True)

        if cate:
            qs = qs.filter(category__in=cate)
        if level:
            qs = qs.filter(details__level=level)
        if sort_keys:
            order_fields = [SORTING_DICT[k] for k in sort_keys if k in SORTING_DICT]
            if order_fields:
                qs = qs.order_by(*order_fields)

        courses = await sync_to_async(lambda: list(qs))()

        details_ids = [c.details.id for c in courses if getattr(c, 'details', None)]
        owner_ids = [c.owner.id for c in courses if getattr(c, 'owner', None)]

        course_details = await sync_to_async(lambda: list(CourseMeta.objects.filter(id__in=details_ids)))()
        course_owners = await sync_to_async(lambda: list(CustomUser.objects.filter(id__in=owner_ids)))()

        details_map = {d.id: d for d in course_details}
        owners_map = {o.id: o for o in course_owners}

        course_data = []
        for c in courses:
            details = details_map.get(c.details.id) if getattr(c, "details", None) else None
            owner = owners_map.get(c.owner.id) if getattr(c, "owner", None) else None

            course_data.append(
                build_course_json_success(c, details, owner)
            )

        return course_data
    except Exception as e:
        logger.error(f"{gettext('Error retrieving courses from DB:')} {str(e)}")
        return error_response(gettext("Error retrieving courses from DB"), status=500)

async def get_course_by_id(course_id) -> dict:
    try:
        uuid_obj = validate_uuid(course_id)
        course = await sync_to_async(lambda: Course.objects.select_related('details', 'owner').get(pk=uuid_obj))()

        structure = await sync_to_async(mongo_repo.get_document_by_id)("course_structures", str(course.structure_ids))
        structure = _convert_object_id_to_str(structure)

        if structure and "structure" in structure:
            for item in structure["structure"]:
                await _fill_module_structure(item)

        course_data = build_course_json_success(course, course.details, course.owner, structure)

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


def _convert_object_id_to_str(doc):
    if not doc:
        return {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            doc[k] = str(v)
        elif isinstance(v, list):
            for item in v:
                _convert_object_id_to_str(item) if isinstance(item, dict) else None
        elif isinstance(v, dict):
            _convert_object_id_to_str(v)
    return doc


async def _fill_module_structure(item: dict):
    """Підвантажує тести всередині модуля (module_id з PostgreSQL)"""
    if item.get("type") != "module" or "module_id" not in item:
        return

    structure_module_ids = await sync_to_async(Module.objects.only("structure_ids").get)(pk=item["module_id"])

    module_doc = await sync_to_async(mongo_repo.get_document_by_id)(
        collection_name="module_structures",
        doc_id=structure_module_ids.structure_ids
    )

    module_doc = _convert_object_id_to_str(module_doc)

    item["structure"] = module_doc.get("structure", [])
