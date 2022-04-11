from time import time
import os
import re


def group_by(items, predicate):
    groups = {}
    for item in items:
        key = predicate(item)
        all_objs = groups.get(key, [])
        all_objs.append(item)
        groups[key] = all_objs
    return groups


def summarize_courses(courses, number=5):
    joins = []
    for idx, course in enumerate(courses):
        if idx >= number:
            break
        joins.append(course.name)
    if len(courses) > number:
        joins.append('...')
    return ", ".join(joins) + f"  ({len(courses)} courses)"


def filter_available_courses(courses):
    available_courses = []
    not_available_courses = []
    for course in courses:
        if hasattr(course, 'name'):
            available_courses.append(course)
        else:
            not_available_courses.append(course)
    return available_courses, not_available_courses


file_regex = r"[\t\\\/:\*\?\"<>\|]"
path_regex = r"[\t:*?\"<>|\/]"


def is_windows():
    return os.name == "nt"


if is_windows():
    from win32_setctime import setctime


def apply_datetime_attr(path, c_time: int, m_time: int):
    a_time = time()
    if is_windows():
        setctime(path, c_time)
    os.utime(path, (a_time, m_time))


def normalize_path(filename, regex=path_regex):
    return re.sub(regex, '_', filename)


def truncate_name(name, length=40):
    if len(name) > length:
        return name[:length - 3] + "..."
    else:
        return name


def find_choice(choices, value):
    for choice in choices:
        if choice.value == value:
            return choice
    return None
