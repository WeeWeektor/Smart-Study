import logging
from typing import Union

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext

from common.utils import error_response, validate_uuid
from courses.models import Test
from courses.services.builder_json import build_public_test_json, build_course_test_json, build_module_test_json
from users.models import CustomUser

logger = logging.getLogger(__name__)


async def get_public_tests_by_author(author_id) -> Union[dict, list]:
    try:
        uuid_obj = validate_uuid(author_id)

        tests = await sync_to_async(lambda: list(
            Test.objects.filter(owner=uuid_obj, is_public=True).select_related("owner")
        ))()

        return [build_public_test_json(t, t.owner) for t in tests]
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
        if not cate:
            if not level:
                tests = await sync_to_async(lambda: list(Test.objects.select_related("owner").filter(is_public=True)))()
            else:
                tests = await sync_to_async(lambda: list(Test.objects
                                                         .select_related("owner")
                                                         .filter(level=level, is_public=True)
                                                         ))()
        else:
            if not level:
                tests = await sync_to_async(lambda: list(Test.objects
                                                         .select_related("owner")
                                                         .filter(category_in=cate, is_public=True)
                                                         ))()
            else:
                tests = await sync_to_async(lambda: list(
                    Test.objects
                    .select_related("owner")
                    .filter(category__in=cate, level=level, is_public=True)
                ))()

        owner_ids = [t.owner.id for t in tests if getattr(t, 'owner', None)]
        tests_owners = await sync_to_async(lambda: list(CustomUser.objects.filter(id__in=owner_ids)))()
        owners_map = {o.id: o for o in tests_owners}

        tests_data = []
        for t in tests:
            owner = owners_map.get(t.owner.id) if getattr(t, 'owner', None) else None

            tests_data.append(
                build_public_test_json(t, owner)
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

        if is_public:
            test = await sync_to_async(lambda: Test.objects.select_related('owner').get(pk=uuid_obj))()
            test_data = build_public_test_json(test, test.owner)
        elif course:
            test = await sync_to_async(lambda: Test.objects.select_related('course').get(pk=uuid_obj))()
            test_data = build_course_test_json(test, course)
        elif module:
            test = await sync_to_async(lambda: Test.objects.select_related('module').get(pk=uuid_obj))()
            test_data = build_module_test_json(test, module)
        else:
            test_data = error_response(gettext("Insufficient parameters to retrieve the test"), status=400)

        return test_data

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
