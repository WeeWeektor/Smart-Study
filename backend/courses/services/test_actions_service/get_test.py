import logging
from typing import Union

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext

from common.services import mongo_repo
from common.utils import error_response, validate_uuid
from courses.models import Test
from courses.services.builder_json import build_public_test_json, build_course_test_json, build_module_test_json
from users.models import CustomUser

logger = logging.getLogger(__name__)


def fetch_questions(document_name, test_data_id):
    return mongo_repo.get_document_by_id(document_name, test_data_id)


async def get_public_tests_by_author(author_id) -> Union[dict, list]:
    try:
        uuid_obj = validate_uuid(author_id)

        tests = await sync_to_async(lambda: list(
            Test.objects.filter(owner=uuid_obj, is_public=True).select_related("owner")
        ))()

        result = []
        for t in tests:
            questions_data = await sync_to_async(fetch_questions)("questions_data_for_test", t.test_data_ids)
            result.append(build_public_test_json(t, t.owner, questions_data))

        return result
    except CustomUser.DoesNotExist:
        return error_response(gettext("Author not found"), status=404)
    except ValidationError as e:
        return error_response(str(e), status=400)
    except Exception as e:
        logger.error(f"{gettext('Error receiving public tests by author id')} ({author_id}): {str(e)}")
        return error_response(
            f"{gettext('Error receiving public tests by author id')} ({author_id}): {str(e)})",
            status=500
        )


async def get_public_tests(cate: Union[list, None], level: Union[str, None]) -> Union[dict, list]:
    try:
        # if not cate:
        #     if not level:
        #         tests = await sync_to_async(lambda: list(Test.objects.select_related("owner").filter(is_public=True)))()
        #     else:
        #         tests = await sync_to_async(lambda: list(Test.objects
        #                                                  .select_related("owner")
        #                                                  .filter(level=level, is_public=True)
        #                                                  ))()
        # else:
        #     if not level:
        #         tests = await sync_to_async(lambda: list(Test.objects
        #                                                  .select_related("owner")
        #                                                  .filter(category__in=cate, is_public=True)
        #                                                  ))()
        #     else:
        #         tests = await sync_to_async(lambda: list(
        #             Test.objects
        #             .select_related("owner")
        #             .filter(category__in=cate, level=level, is_public=True)
        #         ))()

        qs = Test.objects.select_related("owner").filter(is_public=True)

        if cate:
            qs = qs.filter(category__in=cate)
        if level:
            qs = qs.filter(level=level)

        tests = await sync_to_async(lambda: list(qs))()

        owner_ids = [t.owner.id for t in tests if getattr(t, 'owner', None)]
        tests_owners = await sync_to_async(lambda: list(CustomUser.objects.filter(id__in=owner_ids)))()
        owners_map = {o.id: o for o in tests_owners}

        tests_data = []
        for t in tests:
            owner = owners_map.get(t.owner.id) if getattr(t, 'owner', None) else None

            questions_data = await sync_to_async(fetch_questions)("questions_data_for_test", t.test_data_ids)

            tests_data.append(
                build_public_test_json(t, owner, questions_data)
            )

        return tests_data
    except Exception as e:
        logger.error(f"{gettext('Error receiving public tests')}: {str(e)}")
        return error_response(f"{gettext('Error receiving public tests')}: {str(e)}", status=500)


async def get_test_by_id(
        test_id,
        is_public: bool | None = None,
        course: bool | None = None,
        module: bool | None = None
) -> dict:
    try:
        uuid_obj = validate_uuid(test_id)

        strategies = {
            "is_public": (
                lambda: Test.objects.select_related("owner").get(pk=uuid_obj),
                lambda t, q: build_public_test_json(t, t.owner, q),
            ),
            "course": (
                lambda: Test.objects.select_related("course").get(pk=uuid_obj),
                lambda t, q: build_course_test_json(t, t.course, q),
            ),
            "module": (
                lambda: Test.objects.select_related("module__course").get(pk=uuid_obj),
                lambda t, q: build_module_test_json(t, t.module, q),
            ),
        }

        key = None
        if is_public:
            key = "is_public"
        elif course:
            key = "course"
        elif module:
            key = "module"

        if not key:
            return error_response(gettext("Insufficient parameters to retrieve the test"), status=400)

        test_loader, build_func = strategies[key]
        test = await sync_to_async(test_loader)()
        questions_data = await sync_to_async(fetch_questions)("questions_data_for_test", test.test_data_ids)

        return build_func(test, questions_data)

    except ValidationError as e:
        return error_response(str(e), status=400)
    except Test.DoesNotExist:
        return error_response(gettext("Test not found"), status=404)
    except Exception as e:
        logger.error(f"{gettext('Error receiving test by id')} ({test_id}): {str(e)}")
        return error_response(
            f"{gettext('Error receiving test by id')} ({test_id}): {str(e)})",
            status=500
        )
