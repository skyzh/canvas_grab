from PyInquirer import prompt
from .base_filter import BaseFilter
from canvas_grab.utils import group_by, summarize_courses


class PerFilter(BaseFilter):
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
        for course in courses:
            choices.append({
                'name': f'{course.name} (Term {course.enrollment_term_id})',
                'value': course.id,
                'term': course.enrollment_term_id,
                'checked': course.id in self.course_id
            })
        choices = sorted(choices, key=lambda choice: choice['term'])
        choices.reverse()
        while True:
            questions = [
                {
                    'type': 'checkbox',
                    'message': 'Select courses to download',
                    'name': 'per_course_filter',
                    'choices': choices
                }
            ]
            answers = prompt(questions)
            self.course_id = answers['per_course_filter']
            if len(self.course_id) == 0:
                print('At least one course must be selected.')
            else:
                break
