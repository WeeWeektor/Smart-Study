from asgiref.sync import sync_to_async

from common.services import mongo_repo
from courses.models import Test


async def update_path_in_mongo_questions_data(old_prefix, new_prefix, module_id=None, course_id=None):
    if module_id:
        tests = await sync_to_async(lambda: list(Test.objects.filter(module_id=module_id).only('test_data_ids')))()
    elif course_id:
        tests = await sync_to_async(lambda: list(
            Test.objects.filter(course_id=course_id, module_id__isnull=True).only('test_data_ids')))()
    else:
        return

    for test in tests:
        test_data_id = str(test.test_data_ids)
        if not test_data_id:
            continue

        doc = await sync_to_async(mongo_repo.get_document_by_id)("questions_data_for_test", test_data_id)

        if not doc or "questions" not in doc:
            continue

        updated_questions = doc["questions"]
        changed = False

        for q in updated_questions:
            url = q.get("image_url")
            if url and old_prefix in url:
                q["image_url"] = url.replace(old_prefix, new_prefix)
                changed = True

        if changed:
            await sync_to_async(mongo_repo.update_document)(
                collection_name="questions_data_for_test",
                doc_id=test_data_id,
                update_data={"questions": updated_questions},
                action="set"
            )
