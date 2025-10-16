from courses.services.test_actions_service import create_test


async def course_structure(courseStructure: list, ownerId, courseId):
    modules_list = []
    course_tests_list = []
    module_tests_list = []
    module_lessons_list = []

    print("Course structure type:", type(courseStructure))

    for structure in courseStructure:
        if structure['type'] == 'module':
            modules_list.append(structure)

            for moduleStructure in structure['moduleStructure']:
                if moduleStructure['type'] == 'module-test':
                    module_tests_list.append(moduleStructure)
                elif moduleStructure['type'] == 'lesson':
                    module_lessons_list.append(moduleStructure)

        elif structure['type'] == 'course-test':
            course_test = await create_test("course", ownerId, {**structure, "course_id": courseId})

            course_tests_list.append(structure)

    print("Modules:", modules_list)
    print("Course Tests:", course_tests_list)
    print("Module Tests:", module_tests_list)
    print("Module Lessons:", module_lessons_list)
