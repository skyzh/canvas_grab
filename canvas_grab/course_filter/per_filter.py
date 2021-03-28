import questionary
from .base_filter import BaseFilter
from ..utils import group_by, summarize_courses


class PerFilter(BaseFilter):
    """Filter single courses.

    ``PerFilter`` filters every single courses as selected by user. IDs of courses
    will be stored in a list.
    """

    def __init__(self):
        self.course_id = []

    def filter_course(self, courses):
        return list(filter(lambda course: course.id in self.course_id, courses))

    def to_config(self):
        return {
            'course_id': self.course_id
        }

    def from_config(self, config):
        self.course_id = config['course_id']

    def interact(self, courses):
        choices = []
        sorted_courses = sorted(
            courses, key=lambda course: course.enrollment_term_id)
        sorted_courses.reverse()
        for course in sorted_courses:
            choices.append(questionary.Choice(
                f'{course.name} (Term {course.enrollment_term_id})',
                course.id,
                checked=course.id in self.course_id
            ))
        while True:
            self.course_id = questionary.checkbox(
                'Select courses to download',
                choices).unsafe_ask()
            if len(self.course_id) == 0:
                print('At least one course must be selected.')
            else:
                break
