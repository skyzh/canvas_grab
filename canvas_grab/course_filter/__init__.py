from .all_filter import AllFilter
from .term_filter import TermFilter
from .base_filter import BaseFilter
from .per_filter import PerFilter
from canvas_grab.configurable import Configurable
import questionary


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
        self.filter_name = 'all'
        self.all_filter = AllFilter()
        self.term_filter = TermFilter()
        self.per_filter = PerFilter()

    def get_filter(self):
        if self.filter_name == 'term':
            return self.term_filter
        if self.filter_name == 'all':
            return self.all_filter
        if self.filter_name == 'per':
            return self.per_filter
        return None

    def to_config(self):
        return {
            'filter_name': self.filter_name,
            'all_filter': self.all_filter.to_config(),
            'term_filter': self.term_filter.to_config(),
            'per_filter': self.per_filter.to_config()
        }

    def from_config(self, config):
        self.filter_name = config['filter_name']
        self.all_filter.from_config(config['all_filter'])
        self.term_filter.from_config(config['term_filter'])
        self.per_filter.from_config(config['per_filter'])

    def interact(self, courses):
        choices = [
            questionary.Choice('All courses', 'all'),
            questionary.Choice('Filter by term', 'term'),
            questionary.Choice('Select individual courses', 'per')
        ]
        current_id = ['all', 'term', 'per'].index(self.filter_name)
        self.filter_name = questionary.select(
            'Select course filter mode',
            choices,
            default=choices[current_id]
        ).unsafe_ask()
        self.get_filter().interact(courses)
