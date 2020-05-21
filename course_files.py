from canvasapi.canvas import Course, File
from canvasapi.exceptions import ResourceDoesNotExist


__all__ = ['CourseFiles']


class CourseFileCache:
    _files = {}

    def __init__(self, course: Course):
        self._files = {file.id: file for file in course.get_files()}

    def get_file(self, file_id: str) -> File:
        return self._files.get(file_id)

    def get_iter(self):
        return self._files.values()


class CourseFiles:

    _cache = {}

    def __init__(self):
        pass

    def get_files(self, course: Course) -> File:
        cache = self._check_cache(course)
        if cache:
            for file in cache.get_iter():
                yield file
        else:
            raise ResourceDoesNotExist("File tab is not supported.")

    def get_file(self, course: Course, file_id: str) -> File:
        cache = self._check_cache(course)
        if cache:
            return cache.get_file(file_id)
        else:
            return course.get_file(file_id)

    def _check_cache(self, course: Course) -> bool:
        if course.id not in self._cache:
            if 'files' in [tab.id for tab in course.get_tabs()]:
                self._cache[course.id] = CourseFileCache(course)
            else:
                self._cache[course.id] = None

        return self._cache.get(course.id)
