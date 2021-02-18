from canvas_grab.configurable import Configurable
from canvasapi import Canvas
from termcolor import colored

from .endpoint import Endpoint
from .organize_mode import OrganizeMode
from canvas_grab.course_filter import CourseFilter
from canvas_grab.utils import filter_available_courses


class Config(Configurable):
    def __init__(self):
        self.endpoint = Endpoint()
        self.course_filter = CourseFilter()
        self.organize_mode = OrganizeMode()
        self.download_folder = 'files'

    def to_config(self):
        return {
            'endpoint': self.endpoint.to_config(),
            'course_filter': self.course_filter.to_config(),
            'organize_mode': self.organize_mode.to_config()
        }

    def from_config(self, config):
        self.endpoint.from_config(config['endpoint'])
        self.course_filter.from_config(config['course_filter'])
        self.organize_mode.from_config(config['organize_mode'])

    def interact(self):
        self.endpoint.interact()
        canvas = self.endpoint.login()
        print(
            f'You are logged in as {colored(canvas.get_current_user(), "cyan")}')
        courses, not_enrolled = filter_available_courses(canvas.get_courses())
        print(
            f'There are {len(courses)} currently enrolled courses and {len(not_enrolled)} courses not available.')
        self.course_filter.interact(courses)
        self.organize_mode.interact()
        print("Other settings won't be covered in this wizard. Please look into `config.toml` if you want to modify.")
