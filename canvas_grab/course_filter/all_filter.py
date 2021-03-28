from .base_filter import BaseFilter


class AllFilter(BaseFilter):
    """Synchronize all courses.

    ``AllFilter`` returns selected courses as-is.
    """

    def filter_course(self, courses):
        return courses
