from ..configurable import Configurable, Interactable


class BaseFilter(Configurable, Interactable):
    def filter_course(self, courses):
        """Filter courses

        Args:
            courses ([canvasapi.course.Course]): list of courses
        Returns:
            [canvasapi.course.Course]: list of courses
        """
        pass

    def interact(self, courses):
        """TUI for asking users what courses to choose from.

        Args:
            courses ([canvasapi.course.Course]): list of courses
        """
        pass
