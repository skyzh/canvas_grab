from .base_filter import BaseFilter


class AllFilter(BaseFilter):
    def filter_course(self, courses):
        return courses
