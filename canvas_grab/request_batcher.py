class RequestBatcher:
    def __init__(self, course):
        self.course = course
        self.cache = {}

    def get_tabs(self):
        if 'tabs' not in self.cache:
            self.cache['tabs'] = [tab.id for tab in self.course.get_tabs()]

        return self.cache['tabs']

    def get_files(self):
        if 'files' not in self.get_tabs():
            return None

        if 'files' not in self.cache:
            self.cache['files'] = {
                file.id: file
                for file in self.course.get_files()
            }

        return self.cache['files']

    def get_folders(self):
        if 'files' not in self.get_tabs():
            return None

        if 'folders' not in self.cache:
            self.cache['folders'] = {
                folder.id: folder
                for folder in self.course.get_folders()
            }

        return self.cache['folders']

    def get_file(self, file_id):
        files = self.get_files()
        if files is None:
            return self.course.get_file(file_id)
        else:
            return files.get(file_id, self.course.get_file(file_id))

    def get_modules(self):
        if 'modules' not in self.get_tabs():
            return None

        if 'modules' not in self.cache:
            self.cache['modules'] = {
                module.id: module
                for module in self.course.get_modules()
            }

        return self.cache['modules']

    def get_pages(self):
        if 'pages' not in self.get_tabs():
            return None

        if 'pages' not in self.cache:
            self.cache['pages'] = list(self.course.get_pages())

        return self.cache['pages']
