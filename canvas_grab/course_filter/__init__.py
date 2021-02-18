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


def get_name(course_filter):
    if isinstance(course_filter, TermFilter):
        return 'term'
    if isinstance(course_filter, AllFilter):
        return 'all'
    if isinstance(course_filter, PerFilter):
        return 'per'
    return ''


class CourseFilter(Configurable):
    def __init__(self):
        self.course_filter = None

    def to_config(self):
        filter_name = get_name(self.course_filter)
        return {
            'type': filter_name,
            'config': self.course_filter.to_config()
        }

    def from_config(self, config):
        filter_name = config.get('type', '')
        self.course_filter = get_filter(filter_name)
        self.course_filter.from_config(config['config'])

    def interact(self, courses):
        choices = [
            {'name': 'All courses', 'value': 'all'},
            {'name': 'Filter by term', 'value': 'term'},
            {'name': 'Select individual courses', 'value': 'per'}
        ]
        questions = [
            {
                'type': 'list',
                'message': 'Select course filter mode',
                'name': 'course_filter',
                'choices': choices,
                'default': get_name(self.course_filter) or 'all'
            }
        ]
        answers = prompt(questions)
        filter_name = answers['course_filter']
        self.course_filter = get_filter(filter_name)
        self.course_filter.interact(courses)
