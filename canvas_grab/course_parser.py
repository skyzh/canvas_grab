import re
from .utils import normalize_path, file_regex


class CourseParser(object):
    def get_parsed_name(self, course):
        r = re.search(
            r"\((?P<semester_id>[0-9\-]+)\)-(?P<sjtu_id>[A-Za-z0-9]+)-(?P<classroom_id>.+)-(?P<name>.+)\Z", course.course_code)
        if r is not None:
            r = r.groupdict()
        else:
            return normalize_path(course.name)

        if hasattr(course, 'original_name'):
            course_name = course.original_name
            course_nickname = course.name
        else:
            course_name = course.name
            course_nickname = course.name

        template_map = {
            r"{CANVAS_ID}": str(course.id),
            r"{SJTU_ID}": r.get("sjtu_id", ""),
            r"{SEMESTER_ID}": r.get("semester_id", ""),
            r"{CLASSROOM_ID}": r.get("classroom_id", ""),
            r"{NAME}": normalize_path(course_name.replace("（", "(").replace("）", ")"), file_regex),
            r"{NICKNAME}": normalize_path(course_nickname.replace("（", "(").replace("）", ")"), file_regex),
            r"{COURSE_CODE}": course.course_code
        }

        folder_name = '{SJTU_ID}-{NAME}'
        for old, new in template_map.items():
            folder_name = folder_name.replace(old, new)

        folder_name = normalize_path(folder_name)
        return folder_name
