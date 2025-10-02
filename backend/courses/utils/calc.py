def average_rating(courses_list):
    rat = 0
    count = 0
    for course in courses_list:
        if course['course']['is_published']:
            rat += course['course']['details']['rating']
            count += 1

    if rat == 0 or len(courses_list) == 0:
        return 0

    return round(rat / count, 2)


def certificates_issued(courses_list):
    certificates = 0
    for course in courses_list:
        certificates += course['course']['details']['number_completed']
    return certificates


def count_announcements(courses_list):
    announcements = 0
    for course in courses_list:
        announcements += course['course']['details']['number_completed']
        announcements += course['course']['details']['number_of_active']
    return announcements
