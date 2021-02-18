from canvas_grab.configurable import Configurable


class BaseFilter(Configurable):
    def filter_course(self, courses):
        pass

    def interact(self, courses):
        pass
