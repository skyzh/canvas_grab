from canvas_grab.configurable import Configurable
from canvasapi import Canvas
from canvasapi.exceptions import InvalidAccessToken
from termcolor import colored

from .endpoint import Endpoint
from .organize_mode import OrganizeMode
from canvas_grab.course_filter import CourseFilter
from canvas_grab.file_filter import FileFilter
from canvas_grab.utils import filter_available_courses


class Config(Configurable):
    def __init__(self):
        self.endpoint = Endpoint()
        self.course_filter = CourseFilter()
        self.organize_mode = OrganizeMode()
        self.download_folder = 'files'
        self.file_filter = FileFilter()

    def to_config(self):
        return {
            'endpoint': self.endpoint.to_config(),
            'course_filter': self.course_filter.to_config(),
            'organize_mode': self.organize_mode.to_config(),
            'download_folder': self.download_folder,
            'file_filter': self.file_filter.to_config()
        }

    def try_from_config(self, func):
        try:
            return func(), None
        except KeyError as e:
            return None, e

    def from_config(self, config):
        final_err = None
        self.download_folder, err = self.try_from_config(
            lambda: config.get(
                'download_folder', self.download_folder))
        final_err = final_err or err
        _, err = self.try_from_config(
            lambda: self.endpoint.from_config(
                config['endpoint'])
        )
        final_err = final_err or err
        _, err = self.try_from_config(
            lambda: self.organize_mode.from_config(config['organize_mode']))
        final_err = final_err or err
        _, err = self.try_from_config(
            lambda: self.course_filter.from_config(config['course_filter']))
        final_err = final_err or err
        _, err = self.try_from_config(
            lambda: self.file_filter.from_config(config['file_filter']))
        final_err = final_err or err
        if final_err:
            raise final_err

    def interact(self):
        while True:
            self.endpoint.interact()
            canvas = self.endpoint.login()
            try:
                print(
                    f'You are logged in as {colored(canvas.get_current_user(), "cyan")}')
            except InvalidAccessToken:
                print(f'Failed to login')
                continue
            break

        courses, not_enrolled = filter_available_courses(canvas.get_courses())
        print(
            f'There are {len(courses)} currently enrolled courses and {len(not_enrolled)} courses not available.')
        self.course_filter.interact(courses)
        self.organize_mode.interact()
        self.file_filter.interact()
        print("Other settings won't be covered in this wizard. Please look into `config.toml` if you want to modify.")
