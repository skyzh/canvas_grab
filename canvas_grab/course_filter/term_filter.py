import questionary
from .base_filter import BaseFilter
from canvas_grab.utils import group_by, summarize_courses


class TermFilter(BaseFilter):
    def __init__(self):
        self.terms = [-1]

    def filter_course(self, courses):
        terms = self.terms.copy()
        if -1 in terms:
            terms = [
                max(map(lambda course: course.enrollment_term_id, courses))]
            print(f'TermFilter: Select latest term {terms[0]}')

        return list(filter(lambda course: course.enrollment_term_id in terms, courses))

    def to_config(self):
        return {
            'terms': self.terms
        }

    def from_config(self, config):
        self.terms = config['terms']

    def interact(self, courses):
        groups = group_by(courses, lambda course: course.enrollment_term_id)
        choices = []
        for (term, courses) in groups.items():
            choices.append(
                questionary.Choice(
                    f'Term {term}: {summarize_courses(courses)}',
                    term,
                    checked=term in self.terms
                )
            )
        choices = sorted(choices, key=lambda choice: choice.value)
        choices.append(
            questionary.Choice(
                'Latest term only',
                -1,
                checked=-1 in self.terms
            )
        )
        choices.reverse()
        while True:
            self.terms = questionary.checkbox(
                'Select terms to download',
                choices
            ).ask()
            if len(self.terms) == 0:
                print('At least one term must be selected.')
            elif -1 in self.terms and len(self.terms) != 1:
                print('Invalid choice')
            else:
                break
