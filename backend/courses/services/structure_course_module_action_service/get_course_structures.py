from asgiref.sync import sync_to_async
from django.core.cache import caches

from common.services import mongo_repo, register_cache_key
from common.utils import validate_uuid
from courses.models import Course, Module


async def _structure_course_cache_key(course_id) -> str:
    key = f"course_structure_id_{course_id}"

    await register_cache_key(key, "courses_get")
    return key


async def get_course_structures(course_id):
    uuid_obj = validate_uuid(course_id)
    instance_cache = caches["courses_get"]
    cache_key = await _structure_course_cache_key(course_id)

    structureResponse = await sync_to_async(instance_cache.get)(cache_key, version=1, default=None)
    if structureResponse:
        return structureResponse

    course = await sync_to_async(Course.objects.only("structure_ids", "is_published").get)(pk=uuid_obj)
    if course is None:
        raise Course.DoesNotExist

    structureResponse = await _get_cs_from_db(course.structure_ids)

    if course.is_published:
        await sync_to_async(instance_cache.set)(cache_key, structureResponse, 60 * 60, version=1)

    return structureResponse


async def _get_cs_from_db(course_structure_ids) -> dict:
    structureResponse = {}

    course_structure = await sync_to_async(mongo_repo.get_document_by_id)("course_structures", course_structure_ids)
    structureResponse["courseStructure"] = course_structure.get('structure', [])

    for structure in course_structure.get('structure', []):
        if structure.get('type') == 'module':
            module = await sync_to_async(Module.objects.only("structure_ids").get)(pk=structure.get('module_id'))
            module_structure = await sync_to_async(mongo_repo.get_document_by_id)("module_structures",
                                                                                  module.structure_ids)
            structureResponse[f"moduleStructure_order_{structure.get("order")}"] = module_structure.get('structure', [])

    return structureResponse
