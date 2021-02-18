from .all_filter import AllFilter
from .term_filter import TermFilter
from .base_filter import BaseFilter
from .per_filter import PerFilter
from canvas_grab.configurable import Configurable
from PyInquirer import prompt


def get_filter(filter_name):
    if filter_name == 'term':
        return TermFilter()
    if filter_name == 'all':
        return AllFilter()
    if filter_name == 'per':
        return PerFilter()
    return None


class CourseFilter(Configurable):
    def __init__(self):
        self.course_filter = None

    def to_config(self):
        filter_name = ''
        if isinstance(self.course_filter, TermFilter):
            filter_name = 'term'
        if isinstance(self.course_filter, AllFilter):
            filter_name = 'all'
        if isinstance(self.course_filter, PerFilter):
            filter_name = 'per'
        return {
            'type': filter_name,
            'config': self.course_filter.to_config()
        }

    def from_config(self, config):
        filter_name = config.get('type', '')
        self.course_filter = get_filter(filter_name)
        self.course_filter.from_config(config['config'])

    def interact(self, courses):
        questions = [
            {
                'type': 'list',
                'message': 'Select course filter mode',
                'name': 'course_filter',
                'choices': [
                    {'name': 'All courses', 'value': 'all'},
                    {'name': 'Filter by term', 'value': 'term'},
                    {'name': 'Select individual courses', 'value': 'per'}
                ]
            }
        ]
        answers = prompt(questions)
        filter_name = answers['course_filter']
        self.course_filter = get_filter(filter_name)
        self.course_filter.interact(courses)
